import os
import glob

import pyart
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from vaimennuskorjain import correct_attenuation

colorbar_present = False


def animate(frame):
    global colorbar_present
    for ax in axz.flatten():
        ax.cla()
    fname = ls[frame]
    radar = correct_attenuation(fname, smooth_window_len=6)
    display = pyart.graph.RadarDisplay(radar)
    zkws = dict(vmin=0, vmax=50, cmap='viridis')
    kws = dict(colorbar_flag=False)
    display.plot_ppi('DBZHC', sweep=0, ax=axz[0,0], **zkws, **kws, title='DBZ corrected Vaisala')
    display.plot_ppi('DBZHA', sweep=0, ax=axz[0,1], **zkws, **kws, title='DBZ corrected pyart')
    display.plot_ppi('DBZHB', sweep=0, ax=axz[0,2], **zkws, **kws, title='DBZ corrected pyart smoothed')
    display.plot_ppi('DBZH', sweep=0, ax=axz[1,0], **zkws, **kws)
    display.plot_ppi('PHIDP', sweep=0, ax=axz[1,1], vmin=0, vmax=350, **kws)
    display.plot_ppi('ZDR', sweep=0, ax=axz[1,2], vmin=-3, vmax=2, **kws)
    figz.tight_layout()


if __name__ == '__main__':
    rcase = '20170321'
    patt = os.path.expanduser(f'~/data/polar/fivan/{rcase}*_radar.polar.fivan.h5')
    ls = glob.glob(patt)
    figz, axz = plt.subplots(nrows=2, ncols=3, figsize=(16, 12), dpi=80)
    anim = animation.FuncAnimation(figz, animate, frames=len(ls))
    resultsdir = os.path.expanduser('~/results/vaimennus')
    os.makedirs(resultsdir, exist_ok=True)
    anim.save(os.path.join(resultsdir, rcase+'.gif'), writer='pillow', fps=1)
