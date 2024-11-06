import matplotlib.pyplot as plt
import numpy as np


class Plotter:
    def __init__(self, analyzer, xx_line):
        self.analyzer = analyzer
        self.xx_line = xx_line

    def plot_spectrum(self):
        plt.figure(figsize=(12, 9))
        
        plt.subplot(3, 1, 1)
        plt.plot(self.analyzer.lam_ex[self.xx_line], self.analyzer.flux_ex[self.xx_line], 'k-', lw=2)
        
        self.model_line = self.analyzer.F0_bin * np.exp(-((self.analyzer.lam_ex - self.analyzer.l0_bin)**2) / (2 * self.analyzer.s0_bin**2)) / np.sqrt(2 * np.pi * self.analyzer.s0_bin**2)
        
        plt.plot(self.analyzer.lam_ex, self.model_line, 'b-')
            
        self.model_line_2 = self.analyzer.F0_1_bin * np.exp(-((self.analyzer.lam_ex - self.analyzer.l0_1_bin)**2) / (2 * self.analyzer.s0_1_bin**2)) / np.sqrt(2 * np.pi * self.analyzer.s0_1_bin**2) + \
                       self.analyzer.F0_2_bin * np.exp(-((self.analyzer.lam_ex - self.analyzer.l0_2_bin)**2) / (2 * self.analyzer.s0_2_bin**2)) / np.sqrt(2 * np.pi * self.analyzer.s0_2_bin**2)
        
        plt.plot(self.analyzer.lam_ex, self.model_line_2, 'r--')
        plt.xlim([6540, 6580])
        plt.xlabel('lambda')
        plt.ylabel('Flux')
        plt.legend(['Observed', 'One component', f'(BIC = {self.analyzer.bic_1:.0f}, AIC = {self.analyzer.aic_1:.0f})',
                    'Two components', f'(BIC = {self.analyzer.bic_2:.0f}, AIC = {self.analyzer.aic_2:.0f})'], loc='upper left')

    def plot_error(self):
        plt.subplot(3, 1, 2)
        plt.plot(self.analyzer.lam_ex[self.xx_line], self.analyzer.error_ex[self.xx_line], 'k-', lw=2)
        plt.xlim([6550, 6580])
        plt.xlabel('lambda')
        plt.ylabel('Error')

    def plot_residuals(self):
        plt.subplot(3, 1, 3)
        plt.plot(self.analyzer.lam_ex[self.xx_line], self.analyzer.flux_ex[self.xx_line] - self.model_line[self.xx_line], 'b-')
        plt.plot(self.analyzer.lam_ex[self.xx_line], self.analyzer.flux_ex[self.xx_line] - self.model_line_2[self.xx_line], 'r--')
        plt.axhline(y=0, color='k', linestyle='--')
        plt.xlabel('lambda')
        plt.ylabel(r'$\Delta$ Flux')

    def save_plots(self, filename):
        self.plot_spectrum()
        self.plot_error()
        self.plot_residuals()
        plt.tight_layout()
        plt.savefig(filename)
