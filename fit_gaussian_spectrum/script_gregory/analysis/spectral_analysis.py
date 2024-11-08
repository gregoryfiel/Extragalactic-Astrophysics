import numpy as np
from scipy.interpolate import UnivariateSpline
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector, ListVector


class SpectralAnalysis:
    def __init__(self, lambda_, flux, err, error_original, norm_cont, l0_line, xx_line):
        self.lam_ex = lambda_
        self.flux_ex = flux
        self.error_ex = err
        self.error_original = error_original
        self.norm_cont = norm_cont
        self.l0_line = l0_line
        self.xx_line = xx_line

    def fit_cont(self, nsig_up=20, nsig_low=2, degree=3, span=0.05, Nit=20):
        x1_temp = self.lam_ex
        x2_temp = self.flux_ex

        for _ in range(Nit):
            spline = UnivariateSpline(x1_temp, x2_temp, k=degree, s=span*len(x1_temp))
            model_line = spline(x1_temp)
            diff = x2_temp - model_line
            xx_temp1 = (diff <= nsig_up * np.std(diff)) & (diff >= 0)
            xx_temp2 = (np.abs(diff) <= nsig_low * np.std(diff)) & (diff < 0)
            xx_temp = xx_temp1 | xx_temp2
            x1_temp = x1_temp[xx_temp]
            x2_temp = x2_temp[xx_temp]
            
        final_spline = UnivariateSpline(x1_temp, x2_temp, k=degree, s=span*len(x1_temp))
        
        return final_spline

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
        flux_r = FloatVector(self.flux_ex[self.xx_line])
        error_r = FloatVector(self.error_ex[self.xx_line])

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

# Código feito anteriormente   
"""
    def run_analysis(self):
        if self.norm_cont:
            temp = self.fit_cont(self.lam_ex, self.flux_ex)
            self.mean_flux = np.polyval(temp, self.lam_ex)
            self.flux_ex = self.flux_ex - self.mean_flux
            self.flux_original = self.flux_ex

        self.xx_line = (self.lam_ex >= self.l0_line - 20) & (self.lam_ex <= self.l0_line + 20)

        # Single Component
        res = minimize(self.single_gauss, [self.l0_line, 2, 4500], method='L-BFGS-B',
                       bounds=[(self.l0_line - 10, self.l0_line + 10), (1, 8), (5, 10000)])
        self.l0_bin, self.s0_bin, self.F0_bin = res.x
        self.bic_1 = self.BIC(res)
        self.aic_1 = self.AIC(res)
        print("Single Component: BIC =", self.bic_1, "AIC =", self.aic_1)
        print("l0 = ", self.l0_bin, "s0 = ", self.s0_bin, "F0 = ", self.F0_bin)

        # Two Components 
        res = minimize(self.two_gauss, [self.l0_line, 2, 4500, self.l0_line + 10, 3, 2000], method='L-BFGS-B',
                       bounds=[(self.l0_line - 20, self.l0_line + 20), (1, 8), (5, 10000), 
                              (self.l0_line - 10, self.l0_line + 10), (1, 10), (5, 5000)])
        self.l0_1_bin, self.s0_1_bin, self.F0_1_bin, self.l0_2_bin, self.s0_2_bin, self.F0_2_bin = res.x
        self.bic_2 = self.BIC(res)
        self.aic_2 = self.AIC(res)
        print("\nTwo Components: BIC =", self.bic_2, "AIC =", self.aic_2)
        print("l0_1 = ", self.l0_1_bin, "s0_1 = ", self.s0_1_bin, "F0_1 = ", self.F0_1_bin, "l0_2 = ", self.l0_2_bin, "s0_2 = ", self.s0_2_bin, "F0_2 = ", self.F0_2_bin)
    
    def BIC(self, res):
        nobs = len(self.lam_ex[self.xx_line])
        k = len(res.x)
        llf = res.fun
        bic = -2 * res.fun + (k+1) * np.log(nobs)
        
        return bic

    def AIC(self, res):
        k = len(res.x)
        llf = res.fun
        aic = - 2 * llf + 2 * (k + 1)
        
        return aic
"""