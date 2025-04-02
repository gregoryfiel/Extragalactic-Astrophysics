import numpy as np # type: ignore
from scipy.interpolate import UnivariateSpline # type: ignore
import rpy2.robjects as robjects # type: ignore
from rpy2.robjects.packages import importr # type: ignore
from rpy2.robjects.vectors import FloatVector, ListVector # type: ignore
from statsmodels.nonparametric.smoothers_lowess import lowess # type: ignore
from scipy.interpolate import interp1d # type: ignore
from rpy2.robjects import r, pandas2ri # type: ignore


class SpectralAnalysis:
    def __init__(self, lam_ex, flux, error, xx_line, l0_line=6562, norm_cont=False, **fit_cont_kwargs):
        self.lam_ex = lam_ex.copy()
        self.flux_ex = flux.copy()
        self.error_original = error.copy()
        self.l0_line = l0_line
        self.xx_line = xx_line

        if norm_cont:
            self._normalize_continuum(**fit_cont_kwargs)
        else:
            self.flux = self.flux_ex.copy()
            self.error = self.error_original.copy()

    def _normalize_continuum(self, **kwargs):
        """Normaliza o fluxo subtraindo o contínuo."""
        # Ajustar o contínuo usando a função R
        loess_model = self.fit_cont(**kwargs)

        # Prever os valores ajustados
        predict_r = r['predict']
        self.mean_flux = np.array(predict_r(loess_model, FloatVector(self.lam_ex)))

        # Subtrair o contínuo ajustado
        self.flux = self.flux_ex - self.mean_flux
        self.error = np.ones_like(self.flux)

    def fit_cont(self, nsig_up=20, nsig_low=2, degree=2, span=0.1, Nit=10):
        """Chama a função fit_cont em R para ajustar o contínuo."""
        pandas2ri.activate()
        r('''
        fit_cont <- function(x, y, nsig_up=20, nsig_low=2, degree=2, span=0.1, Nit=10) {
            x2_temp <- y
            x1_temp <- x
            
            for (nn in 1:Nit) {
                temp <- loess(x2_temp ~ x1_temp, degree = degree, span = span)
                residuals <- x2_temp - predict(temp)
                xx_temp1 <- residuals <= nsig_up * sd(residuals) & residuals >= 0
                xx_temp2 <- abs(residuals) <= nsig_low * sd(residuals) & residuals < 0
                xx_temp <- xx_temp1 | xx_temp2
                
                x1_temp <- x1_temp[xx_temp]
                x2_temp <- x2_temp[xx_temp]
            }
            
            temp <- loess(x2_temp ~ x1_temp, degree = degree, span = span)
            return(temp)
        }
        ''')
        x_r = FloatVector(self.lam_ex)
        y_r = FloatVector(self.flux_ex)

        fit_cont_r = r['fit_cont']
        loess_model = fit_cont_r(x_r, y_r, nsig_up, nsig_low, degree, span, Nit)

        return loess_model

    def run_analysis(self):
        bbmle = importr('bbmle')
        robjects.r('''
        single_gauss <- function(l0, s0, F0, lambda, flux, err) {
            model_line <- F0 * exp(-(lambda - l0)^2 / (2 * s0^2)) / sqrt(2 * pi * s0^2)
            ln_p_i <- -log(sqrt(2 * pi) * err) - (flux - model_line)^2 / (2 * err^2)
            lnlike <- -sum(ln_p_i)
            return(lnlike)
        }
        
        two_gauss <- function(l0_1, s0_1, F0_1, l0_2, s0_2, F0_2, lambda, flux, err) {
            line_1 <- F0_1 * exp(-(lambda - l0_1)^2 / (2 * s0_1^2)) / sqrt(2 * pi * s0_1^2)
            line_2 <- F0_2 * exp(-(lambda - l0_2)^2 / (2 * s0_2^2)) / sqrt(2 * pi * s0_2^2)
            model_line <- line_1 + line_2
            ln_p_i <- -log(sqrt(2 * pi) * err) - (flux - model_line)^2 / (2 * err^2)
            lnlike <- -sum(ln_p_i)
            return(lnlike)
        }
        ''')

        lambda_r = FloatVector(self.lam_ex[self.xx_line])
        flux_r = FloatVector(self.flux[self.xx_line])
        error_r = FloatVector(self.error[self.xx_line])

        start_params_single = ListVector({'l0': self.l0_line, 's0': 2, 'F0': 4500})
        lower_bounds_single = ListVector({'l0': self.l0_line - 10, 's0': 1, 'F0': 5})
        upper_bounds_single = ListVector({'l0': self.l0_line + 10, 's0': 8, 'F0': 1e4})

        mle_result_single = bbmle.mle2(robjects.r['single_gauss'],
                                       start=start_params_single,
                                       data=ListVector({'lambda': lambda_r, 'flux': flux_r, 'err': error_r}),
                                       method="L-BFGS-B",
                                       skip_hessian = True,
                                       lower=lower_bounds_single,
                                       upper=upper_bounds_single,
                                       control=ListVector({'maxit': 1e5}))

        tt_single = robjects.r['coef'](mle_result_single)
        self.l0_bin, self.s0_bin, self.F0_bin = tt_single[0], tt_single[1], tt_single[2]
        self.aic_1 = robjects.r['AIC'](mle_result_single)[0]
        self.bic_1 = robjects.r['BIC'](mle_result_single)[0]

        print("Single Component Results:")
        print("BIC =", self.bic_1, "AIC =", self.aic_1)
        print("l0 =", self.l0_bin, "s0 =", self.s0_bin, "F0 =", self.F0_bin)
        
        start_params_two = ListVector({'l0_1': self.l0_line, 's0_1': 2, 'F0_1': 4500,
                                    'l0_2': self.l0_line + 10, 's0_2': 3, 'F0_2': 2000})
        lower_bounds_two = ListVector({'l0_1': self.l0_line - 20, 's0_1': 1, 'F0_1': 5,
                                    'l0_2': self.l0_line - 10, 's0_2': 1, 'F0_2': 5})
        upper_bounds_two = ListVector({'l0_1': self.l0_line + 20, 's0_1': 8, 'F0_1': 1e4,
                                    'l0_2': self.l0_line + 10, 's0_2': 10, 'F0_2': 5e3})

        mle_result_two = bbmle.mle2(robjects.r['two_gauss'],
                                    start=start_params_two,
                                    data=ListVector({'lambda': lambda_r, 'flux': flux_r, 'err': error_r}),
                                    method="L-BFGS-B",
                                    skip_hessian = True,
                                    lower=lower_bounds_two,
                                    upper=upper_bounds_two,
                                    control=ListVector({'maxit': 1e8}))

        tt_two = robjects.r['coef'](mle_result_two)
        (self.l0_1_bin, self.s0_1_bin, self.F0_1_bin,
        self.l0_2_bin, self.s0_2_bin, self.F0_2_bin) = tt_two
        self.aic_2 = robjects.r['AIC'](mle_result_two)[0]
        self.bic_2 = robjects.r['BIC'](mle_result_two)[0]

        print("\nTwo Components Results:")
        print("BIC =", self.bic_2, "AIC =", self.aic_2)
        print("l0_1 =", self.l0_1_bin, "s0_1 =", self.s0_1_bin, "F0_1 =", self.F0_1_bin)
        print("l0_2 =", self.l0_2_bin, "s0_2 =", self.s0_2_bin, "F0_2 =", self.F0_2_bin)
