import numpy as np
from scipy.optimize import minimize


class SpectralAnalysis:
    def __init__(self, lam_ex, flux_ex, error_ex):
        self.lam_ex = lam_ex
        self.flux_ex = flux_ex
        self.error_ex = error_ex
        self.norm_cont = True
        self.l0_line = 6562

    def single_gauss(self, params):
        l0, s0, F0 = params
        model_line = F0 * np.exp(-((self.lam_ex - l0)**2) / (2 * s0**2)) / np.sqrt(2 * np.pi * s0**2)
        ln_p_i = -np.log(np.sqrt(2 * np.pi) * self.error_ex) - ((self.flux_ex - model_line)**2) / (2 * self.error_ex**2)
        lnlike = -np.sum(ln_p_i)
        
        return lnlike

    def two_gauss(self, params):
        l0_1, s0_1, F0_1, l0_2, s0_2, F0_2 = params
        line_1 = F0_1 * np.exp(-((self.lam_ex - l0_1)**2) / (2 * s0_1**2)) / np.sqrt(2 * np.pi * s0_1**2)
        line_2 = F0_2 * np.exp(-((self.lam_ex - l0_2)**2) / (2 * s0_2**2)) / np.sqrt(2 * np.pi * s0_2**2)
        model_line = line_1 + line_2
        ln_p_i = -np.log(np.sqrt(2 * np.pi) * self.error_ex) - ((self.flux_ex - model_line)**2) / (2 * self.error_ex**2)
        lnlike = -np.sum(ln_p_i)
        
        return lnlike

    def fit_cont(self, nsig_up=20, nsig_low=2, degree=3, span=0.05, Nit=20):
        x1_temp = self.lam_ex
        x2_temp = self.flux_ex

        for nn in range(Nit):
            temp = np.polyfit(x1_temp, x2_temp, degree)
            model_line = np.polyval(temp, x1_temp)
            xx_temp1 = (x2_temp - model_line) <= nsig_up * np.std(x2_temp - model_line) 
            xx_temp2 = np.abs(x2_temp - model_line) <= nsig_low * np.std(x2_temp - model_line)
            xx_temp = xx_temp1 | xx_temp2
            x1_temp = x1_temp[xx_temp]
            x2_temp = x2_temp[xx_temp]

        temp = np.polyfit(x1_temp, x2_temp, degree)
        
        return temp

    def run_analysis(self):
        if self.norm_cont:
            temp = self.fit_cont()
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
        k = len(res.x)
        equation = -2 * res.fun + k * np.log(len(self.lam_ex[self.xx_line]))
        
        return equation

    def AIC(self, res):
        k = len(res.x)
        equation = 2 * k - 2 * res.fun
        
        return equation
