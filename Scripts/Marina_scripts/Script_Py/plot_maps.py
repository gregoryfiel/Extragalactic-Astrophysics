import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from marvin.tools import Maps
# from marvin.tools import Cube

maps = Maps('12772-12705', bintype='SPX')
# cube = Cube('12772-12705')

halpha_flux = maps.emline_gflux_ha_6564
hbeta_flux = maps.emline_gflux_hb_4862

halpha_vel = maps.emline_gvel_ha_6564
halpha_sig = maps.emline_gsigma_ha_6564

halpha_sig_corr = halpha_sig.inst_sigma_correction()
halpha_ew = maps.emline_gew_ha_6564
hbeta_ew = maps.emline_gew_hb_4862

stvel = maps.stellar_vel
stsig = maps.stellar_sigma
stsig_corr = stsig.inst_sigma_correction()

nii_ha = np.log10(maps.emline_gflux_nii_6585 / halpha_flux)
oiii_hb = np.log10(maps.emline_gflux_oiii_5008 / hbeta_flux)

dn4000 = maps.specindex_dn4000 * np.array(maps.specindex_corr_dn4000)
# hb_corr = np.array(maps.specindex_corr_hb)
hb_index = maps.specindex_hb * np.array(maps.specindex_corr_hb)
hdeltaa = maps.specindex_hdeltaa * np.array(maps.specindex_corr_hdeltaa)
fe4383 = maps.specindex_fe4383 * np.array(maps.specindex_corr_fe4383)
fe5270 = maps.specindex_fe5270 * np.array(maps.specindex_corr_fe5270)
fe5335 = maps.specindex_fe5335 * np.array(maps.specindex_corr_fe5335)
mgb = maps.specindex_mgb * np.array(maps.specindex_corr_mgb)
mg1 = maps.specindex_mg1 * np.array(maps.specindex_corr_mg1)
mg2 = maps.specindex_mg2 * np.array(maps.specindex_corr_mg2)

fe2 = (maps.specindex_fe4383 + fe5270 + fe5335)
fe3 = fe2 / 3
temp = 0.72 * fe5270 + 0.28 * fe5335
temp2 = mgb * temp
mg_fe_p = temp2**(0.5)

hbeta_287 = 2.87 * hbeta_flux
Av_1 = np.log10(maps.emline_gflux_ha_6564 / hbeta_287)
Av = 7.22 * Av_1

r_re = maps.spx_ellcoo_r_re
spx_mflux = maps.spx_mflux
spx_snr = maps.spx_snr

# print(type(maps.specindex_hb))
# print(type(maps.specindex_corr_hb))
# print(maps.specindex_hb.shape)
# print(maps.specindex_corr_hb.shape)

with plt.style.context('seaborn-darkgrid'):
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(18, 18))
    stvel.plot(fig=fig, ax=axes[0, 0], snr_min=None)
    stsig_corr.plot(fig=fig, ax=axes[0, 1], snr_min=None)
    halpha_vel.plot(fig=fig, ax=axes[1, 0], title="H-alpha emission: velocity", snr_min=None)
    halpha_sig_corr.plot(fig=fig, ax=axes[1, 1], title="H-alpha emission: sigma", snr_min=None)

    halpha_flux.plot(fig=fig, ax=axes[0, 2], title="H-alpha emission: flux", snr_min=None)
    hbeta_flux.plot(fig=fig, ax=axes[0, 3], title="H-Beta emission: flux", snr_min=None)
    halpha_ew.plot(fig=fig, ax=axes[1, 2], title="H-alpha emission: EW", snr_min=None)
    hb_index.plot(fig=fig, ax=axes[1, 3], title="Index Hb", snr_min=None)

    # nii_ha.plot(fig=fig, ax=axes[2, 0], title="log([NII]6585 / H-alpha)", snr_min=None)
    # oiii_hb.plot(fig=fig, ax=axes[3, 2], title="log([OIII]5007 / H-beta)", snr_min=None)

    dn4000.plot(fig=fig, ax=axes[2, 0], title="Index Dn4000", snr_min=None)
    hdeltaa.plot(fig=fig, ax=axes[2, 1], title="Index HdeltaA", snr_min=None)
    fe3.plot(fig=fig, ax=axes[2, 2], title="Index Fe3", snr_min=None)
    mg_fe_p.plot(fig=fig, ax=axes[2, 3], title="Index [Mg/Fe]'", snr_min=None)

    mgb.plot(fig=fig, ax=axes[3, 0], title="Index Mgb", snr_min=None)
    mg1.plot(fig=fig, ax=axes[3, 1], title="Index Mg1", snr_min=None)
    mg2.plot(fig=fig, ax=axes[3, 2], title="Index  Mg2", snr_min=None)
    Av.plot(fig=fig, ax=axes[3, 3], title="Av Balmer", snr_min=None)

fig.savefig('maps/12772/12772-12705_maps.png')

with plt.style.context('seaborn-darkgrid'):
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))
    spx_mflux.plot(fig=fig, ax=axes[0], snr_min=None)
    spx_snr.plot(fig=fig, ax=axes[1], snr_min=None)
    r_re.plot(fig=fig, ax=axes[2], snr_min=None)

fig.savefig('maps/12772/12772-12705_SN_r_re.png')

# image = cube.getImage()
# image.save('maps/12772/12772-12705_image.png')

masks, bpt, axes = maps.get_bpt(show_plot=False)
bpt.savefig('maps/12772/12772-12705_bpt.png')
