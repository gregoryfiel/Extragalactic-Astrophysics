import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from pathlib import Path
from analysis.spectral_analysis import SpectralAnalysis
from analysis.spectral_analysis_plotter import Plotter


def get_path(cxt_filename):
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'spectral_data'
    cxt_file = data_dir / f'{cxt_filename}.cxt'
    png_file = data_dir / f'{cxt_filename}.png'

    return cxt_file, png_file

def main():
    spectrum_cxt = '0555-52266-0558'
    cxt_file, png_file = get_path(spectrum_cxt)
    
    ex_gal = pd.read_csv(cxt_file, sep=r'\s+', header=None)
    lam_ex = ex_gal[0][ex_gal[1] > 0].values
    flux_ex = ex_gal[1][ex_gal[1] > 0].values
    error_original = ex_gal[2][ex_gal[1] > 0].values
    l0_line = 6562
    xx_line = (lam_ex >= l0_line - 20) & (lam_ex <= l0_line + 20)
    
    analyzer = SpectralAnalysis(
        lam_ex, 
        flux_ex, 
        error_original,
        xx_line=xx_line,
        l0_line=l0_line,
        norm_cont=True # Normalizes the continuum
    )
    
    analyzer.run_analysis()

    plotter = Plotter(analyzer, xx_line)
    plotter.save_plots(png_file)

if __name__ == "__main__":
    main()