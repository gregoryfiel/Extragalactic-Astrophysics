import math as mt
import numpy as np
from scipy.interpolate import UnivariateSpline

class Gaussians:
    def __init__(self, lmbda, flux, err, l0, s0, F0, l0_1, s0_1, F0_1, l0_2, s0_2, F0_2):
        self.lmbda = lmbda
        self.flux = flux
        self.err = err
        self.l0 = l0
        self.s0 = s0
        self.F0 = F0
        self.l0_1 = l0_1
        self.s0_1 = s0_1
        self.F0_1 = F0_1
        self.l0_2 = l0_2
        self.s0_2 = s0_2
        self.F0_2 = F0_2

    def single_gaussian(self):
        model_line = self.F0 * mt.exp(-(self.lmbda - self.l0)**2 / (2 * self.s0**2)) / mt.sqrt(2 * mt.pi * self.s0**2)
        ln_p_i = -mt.log(mt.sqrt(2 * mt.pi) * self.err) - (self.flux - model_line)**2 / (2 * self.err**2)
        lnlike = -sum(ln_p_i)
        
        return(lnlike)

    def double_gaussian(self):
        line_1 = self.F0_1 * mt.exp(-(self.lmbda - self.l0_1)**2 / (2 * self.s0_1**2)) / mt.sqrt(2 * mt.pi * self.s0_1**2)
        line_2 = self.F0_2 * mt.exp(-(self.lmbda - self.l0_2)**2 / (2 * self.s0_2**2)) / mt.sqrt(2 * mt.pi * self.s0_2**2)
        model_line = line_1 + line_2
        ln_p_i = -mt.log(mt.sqrt(2 * mt.pi) * self.err) - (self.flux - model_line)**2 / (2 * self.err**2)
        lnlike = -sum(ln_p_i)
        
        return(lnlike)
    

class Normalize:
    def __init__(self, x, y, nsig_up, nsig_low, degree, span, Nit):
        self.x1_temp = x
        self.x2_temp = y
        self.nsig_up = nsig_up
        self.nsig_low = nsig_low
        self.degree = degree
        self.span = span
        self.Nit = Nit

    def fit_cont(self):
        for nn in range(1, self.Nit+1):
            temp = UnivariateSpline(self.x1_temp, self.x2_temp, k=self.degree, s=self.span * len(self.x1_temp))
            predicted = temp(self.x1_temp)

            diff = self.x2_temp - predicted
            xx_temp1 = (diff <= self.nsig_up * np.std(diff)) & (diff >= 0)
            xx_temp2 = (np.abs(diff) <= self.nsig_low * np.std(diff)) & (diff < 0)

            xx_temp = xx_temp1 | xx_temp2
            self.x1_temp = self.x1_temp[xx_temp]
            self.x2_temp = self.x2_temp[xx_temp]

        final_fit = UnivariateSpline(self.x1_temp, self.x2_temp, k=self.degree, s=self.span * len(self.x1_temp))

        return final_fit
