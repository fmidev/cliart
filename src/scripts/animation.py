"""animated attenuation correction visualization"""

import os
import glob

import numpy as np
import pyart
import matplotlib.pyplot as plt
from matplotlib import animation
import cartopy.crs as ccrs

from vaimennuskorjain import correct_attenuation_zphi

colorbar_present = False


def animate(frame, plot_cb=False):
    global colorbar_present
    for ax in axz.flatten():
        ax.cla()
    fname = ls[frame]
    radar = correct_attenuation_zphi(fname, smooth_window_len=6)
    display = pyart.graph.RadarMapDisplay(radar)
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    piakws = dict(vmin=0, vmax=12, cmap='gnuplot2_r')
    kws = dict(colorbar_flag=plot_cb, sweep=0, resolution='50m', add_grid_lines=False)
    plotfun = display.plot_ppi_map
    plotfun('DBZHC', ax=axz[0,0], **zkws, **kws, title='corrected DBZ, Vaisala (DBZHC)',
            colorbar_label='corrected equivalent reflectivity factor (dBZ)')
    plotfun('DBZHA', ax=axz[0,1], **zkws, **kws, title='corrected DBZ, ZPhi')
    plotfun('DBZHB', ax=axz[0,2], **zkws, **kws, title='corrected DBZ, ZPhi smoothed')
    plotfun('DBZH', ax=axz[1,0], **zkws, **kws, colorbar_label='equivalent reflectivity factor (dBZ)')
    plotfun('PIA', ax=axz[1,1], **piakws, **kws)
    plotfun('PIA_filtered', ax=axz[1,2], **piakws, **kws)
    try:
        plotfun('SPEC', ax=axz[2,0], vmin=0, vmax=0.4, **kws, cmap='pyart_Theodore16')
        plotfun('PHIDPA', ax=axz[2,1], vmin=0, vmax=360, cmap='pyart_Wild25', **kws)
        plotfun('ZDR', ax=axz[2,2], vmin=-3, vmax=3, cmap='pyart_ChaseSpectral', **kws)
    except IndexError:
        pass


if __name__ == '__main__':
    rcase = '20170812'
    #rcase = '20230807'
    site = 'fivan'
    patt = os.path.expanduser(f'~/data/polar/{site}/{rcase}*_radar.polar.{site}.h5')
    ls = sorted(glob.glob(patt))
    radar = pyart.aux_io.read_odim_h5(ls[0], include_datasets=['dataset1'])
    colsrows = (3, 2)
    figsize = np.multiply(colsrows, (6,5))
    target_resolution = (1920, 1080)
    dpi = np.divide(target_resolution, figsize).min()
    proj = ccrs.LambertConformal(
        central_latitude=radar.latitude["data"][0],
        central_longitude=radar.longitude["data"][0],
    )
    figz, axz = plt.subplots(nrows=2, ncols=3, figsize=figsize, dpi=dpi,
                             subplot_kw={'projection': proj})
    figz.subplots_adjust(left=0, bottom=0.02, right=1, top=0.96, wspace=0, hspace=None)
    animate(0, plot_cb=True)
    anim = animation.FuncAnimation(figz, animate, frames=len(ls))
    resultsdir = os.path.expanduser('~/results/vaimennus')
    os.makedirs(resultsdir, exist_ok=True)
    anim.save(os.path.join(resultsdir, site+rcase+'.gif'), writer='pillow', fps=1)
    plt.close(figz)
