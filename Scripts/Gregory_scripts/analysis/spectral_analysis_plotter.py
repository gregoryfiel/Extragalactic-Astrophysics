import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
import os  # Import necessário para criar subpastas


class Plotter:
    def __init__(self, analyzer, xx_line):
        self.analyzer = analyzer
        self.xx_line = xx_line

    def plot_spectrum(self):
        plt.figure(figsize=(12, 9))
        
        plt.subplot(3, 1, 1)
        plt.plot(self.analyzer.lam_ex[self.xx_line], self.analyzer.flux_ex[self.xx_line], 'k-', lw=2)
        
        self.model_line = self.analyzer.F0_bin * np.exp(-(self.analyzer.lam_ex - self.analyzer.l0_bin)**2 / (2 * self.analyzer.s0_bin**2)) / np.sqrt(2 * np.pi * self.analyzer.s0_bin**2)
        
        plt.plot(self.analyzer.lam_ex, self.model_line, 'b-')
            
        self.model_line_2 = self.analyzer.F0_1_bin * np.exp(-((self.analyzer.lam_ex - self.analyzer.l0_1_bin)**2) / (2 * self.analyzer.s0_1_bin**2)) / np.sqrt(2 * np.pi * self.analyzer.s0_1_bin**2) + \
                       self.analyzer.F0_2_bin * np.exp(-(self.analyzer.lam_ex - self.analyzer.l0_2_bin)**2 / (2 * self.analyzer.s0_2_bin**2)) / np.sqrt(2 * np.pi * self.analyzer.s0_2_bin**2)
        
        plt.plot(self.analyzer.lam_ex, self.model_line_2, 'r--')
        plt.xlim([6545, 6580])
        plt.xlabel('lambda')
        plt.ylabel('Flux')
        plt.legend(['Observed', 'One component', 'Two components', 'Two components',], loc='upper left')

    def plot_error(self):
        plt.subplot(3, 1, 2)
        plt.plot(self.analyzer.lam_ex[self.xx_line], self.analyzer.error_original[self.xx_line], 'k-', lw=2)
        plt.xlim([6550, 6580])
        plt.ticklabel_format(axis='y',style='sci',scilimits=(1,4))
        plt.xlabel('lambda')
        plt.ylabel('Error')

    def plot_residuals(self):
        plt.subplot(3, 1, 3)
        
        residuals_one = self.analyzer.flux_ex[self.xx_line] - self.model_line[self.xx_line]
        residuals_one -= np.mean(residuals_one) 
        
        residuals_two = self.analyzer.flux_ex[self.xx_line] - self.model_line_2[self.xx_line]
        residuals_two -= np.mean(residuals_two)
        
        plt.plot(self.analyzer.lam_ex[self.xx_line], residuals_one, 'b-', label='One Component Residuals')
        plt.plot(self.analyzer.lam_ex[self.xx_line], residuals_two, 'r--', label='Two Components Residuals')
        plt.axhline(y=0, color='k', linestyle='--')
        plt.xlabel('lambda')
        plt.ylabel(r'$\Delta$ Flux')
        plt.legend()

    def save_plots(self, filename):
        self.plot_spectrum()
        self.plot_error()
        self.plot_residuals()
        plt.tight_layout()
        plt.savefig(filename)

        # Extrair o diretório do arquivo e criar a subpasta para os gráficos com zoom
        output_folder = os.path.join(os.path.dirname(filename), "zoomed_plots")
        self.save_zoomed_plots(output_folder)

    def save_zoomed_plots(self, output_folder):
        """
        Salva 5 imagens com recortes de 5 em 5 no comprimento de onda (X).
        """
        # Criar a subpasta para salvar as imagens, se não existir
        os.makedirs(output_folder, exist_ok=True)

        # Definir os limites de recorte
        start = 6545
        end = 6580
        step = 5

        # Gerar os gráficos com recortes
        for i, x_min in enumerate(range(start, end, step)):
            x_max = x_min + step

            # Filtrar os dados para o intervalo atual
            mask = (self.analyzer.lam_ex >= x_min) & (self.analyzer.lam_ex < x_max)

            plt.figure(figsize=(8, 6))
            plt.plot(self.analyzer.lam_ex[mask], self.analyzer.flux_ex[mask], 'k-', lw=2, label='Observed')
            plt.plot(self.analyzer.lam_ex[mask], self.model_line[mask], 'b-', label='One Component')
            plt.plot(self.analyzer.lam_ex[mask], self.model_line_2[mask], 'r--', label='Two Components')

            plt.xlim([x_min, x_max])
            plt.xlabel('lambda')
            plt.ylabel('Flux')
            plt.legend(loc='upper left')
            plt.title(f'Zoomed Spectrum: {x_min} - {x_max}')

            # Salvar a imagem na subpasta
            filename = os.path.join(output_folder, f'spectrum_zoom_{i + 1}.png')
            plt.savefig(filename)
            plt.close()

        print(f"Zoomed plots saved in folder: {output_folder}")
