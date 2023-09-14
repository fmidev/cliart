"""animated attenuation correction visualization"""

import os
import glob

import pyart
import matplotlib.pyplot as plt
from matplotlib import animation
from functools import partial

from vaimennuskorjain import correct_attenuation_zphi
from radproc.visual import canvas

colorbar_present = False


def plot_atten(display, axarr, plot_cb=False):
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    piakws = dict(vmin=0, vmax=15, cmap='gnuplot2_r')
    d = 360000
    kws = dict(colorbar_flag=plot_cb, sweep=0, resolution='50m', add_grid_lines=False, width=d, height=d)
    plotfun = display.plot_ppi_map
    plotfun('DBZHC', ax=axarr[0,2], **zkws, **kws, title='Corrected DBZ, Vaisala (DBZHC)',
            colorbar_label='corrected equivalent reflectivity factor (dBZ)')
    #plotfun('DBZHA', ax=axarr[0,1], **zkws, **kws, title='Corrected DBZ, ZPHI')
    plotfun('SPEC', ax=axarr[1,0], vmin=0, vmax=0.4, **kws, cmap='pyart_Theodore16', title='Specific attenuation')
    plotfun('DBZHAS', ax=axarr[0,1], **zkws, **kws, title='Corrected DBZ, ZPHI')
    plotfun('DBZH', ax=axarr[0,0], **zkws, **kws, title='Attenuated DBZH', colorbar_label='equivalent reflectivity factor (dBZ)')
    #plotfun('PIA', ax=axarr[1,1], **piakws, **kws)
    plotfun('PIAS', ax=axarr[1,1], **piakws, **kws)
    plotfun('PHIDPA', ax=axarr[1,2], vmin=0, vmax=360, cmap='pyart_Wild25', **kws, title='PHIDP', colorbar_label='differential phase (dB)')
    try: # plotting third row
        plotfun('SPEC', ax=axarr[2,0], vmin=0, vmax=0.4, **kws, cmap='pyart_Theodore16')
        plotfun('PHIDPA', ax=axarr[2,1], vmin=0, vmax=360, cmap='pyart_Wild25', **kws)
        plotfun('ZDR', ax=axarr[2,2], vmin=-3, vmax=3, cmap='pyart_ChaseSpectral', **kws)
    except IndexError:
        pass


def animate(frame, axarr, **plotkws):
    global colorbar_present
    for ax in axarr.flatten():
        ax.cla()
    fname = ls[frame]
    radar = correct_attenuation_zphi(fname, smooth_window_len=6)
    display = pyart.graph.RadarMapDisplay(radar)
    plot_atten(display, axarr, **plotkws)


if __name__ == '__main__':
    rcase = '20170812'
    #rcase = '20230807'
    site = 'fivan'
    patt = os.path.expanduser(f'~/data/polar/{site}/{rcase}*_radar.polar.{site}.h5')
    ls = sorted(glob.glob(patt))
    radar = pyart.aux_io.read_odim_h5(ls[0], include_datasets=['dataset1'])
    figz, axz = canvas(radar, 3, 2)
    animate(0, axz, plot_cb=True)
    anim = partial(animate, axarr=axz)
    anim = animation.FuncAnimation(figz, anim, frames=len(ls))
    resultsdir = os.path.expanduser('~/results/vaimennus')
    os.makedirs(resultsdir, exist_ok=True)
    anim.save(os.path.join(resultsdir, site+rcase+'.gif'), writer='pillow', fps=1)
    plt.close(figz)
    #
    fig, axs = canvas(radar, 3, 2)
    animate(9, axs, plot_cb=True)
    fig.savefig(os.path.join(resultsdir, site+rcase+'.png'))
