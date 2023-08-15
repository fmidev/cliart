"""animated attenuation correction visualization"""

import os
import glob

import numpy as np
import pyart
import matplotlib.pyplot as plt
from matplotlib import animation

from vaimennuskorjain import correct_attenuation_zphi

colorbar_present = False


def animate(frame, plot_cb=False):
    global colorbar_present
    for ax in axz.flatten():
        ax.cla()
    fname = ls[frame]
    radar = correct_attenuation_zphi(fname, smooth_window_len=6)
    display = pyart.graph.RadarDisplay(radar)
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    piakws = dict(vmin=0, vmax=12, cmap='gnuplot2_r')
    kws = dict(colorbar_flag=plot_cb, sweep=0)
    display.plot_ppi('DBZHC', ax=axz[0,0], **zkws, **kws, title='DBZ corrected Vaisala')
    display.plot_ppi('DBZHA', ax=axz[0,1], **zkws, **kws, title='DBZ corrected pyart')
    display.plot_ppi('DBZHB', ax=axz[0,2], **zkws, **kws, title='DBZ corrected pyart smoothed')
    display.plot_ppi('DBZH', ax=axz[1,0], **zkws, **kws)
    display.plot_ppi('PHIDPA', ax=axz[2,1], vmin=0, vmax=360, cmap='pyart_Wild25', **kws)
    display.plot_ppi('ZDR', ax=axz[2,2], vmin=-3, vmax=3, cmap='pyart_ChaseSpectral', **kws)
    display.plot_ppi('SPEC', ax=axz[2,0], vmin=0, vmax=0.4, **kws, cmap='pyart_Theodore16')
    display.plot_ppi('PIA_filtered', ax=axz[1,2], **piakws, **kws)
    display.plot_ppi('PIA', ax=axz[1,1], **piakws, **kws)
    figz.tight_layout()


if __name__ == '__main__':
    rcase = '20170812'
    #rcase = '20230807'
    site = 'fivan'
    patt = os.path.expanduser(f'~/data/polar/{site}/{rcase}*_radar.polar.{site}.h5')
    ls = sorted(glob.glob(patt))
    figsize = (18, 15)
    target_resolution = (1920, 1080)
    dpi = np.divide(target_resolution, figsize).min()
    figz, axz = plt.subplots(nrows=3, ncols=3, figsize=figsize, dpi=dpi)
    animate(0, plot_cb=True)
    anim = animation.FuncAnimation(figz, animate, frames=len(ls))
    resultsdir = os.path.expanduser('~/results/vaimennus')
    os.makedirs(resultsdir, exist_ok=True)
    anim.save(os.path.join(resultsdir, site+rcase+'.gif'), writer='pillow', fps=1)
    plt.close(figz)
