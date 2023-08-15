"""script for zisualizing attenuation correction"""

import os

import pyart
import matplotlib.pyplot as plt

from vaimennuskorjain import correct_attenuation_zphi


if __name__ == '__main__':
    #fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202206030010_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307081105_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307030835_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307010920_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/polar/fivan/201708121600_radar.polar.fivan.h5')
    #fname = os.path.expanduser('~/data/polar/fikor/202308071610_radar.polar.fikor.h5')
    #fname = os.path.expanduser('~/data/polar/fikor/202308080540_radar.polar.fikor.h5')
    fname = os.path.expanduser('~/data/polar/fikor/202308080405_radar.polar.fikor.h5')
    radar = correct_attenuation_zphi(fname, smooth_window_len=6)
    figz, axz = plt.subplots(nrows=3, ncols=3, figsize=(17, 17), dpi=110, sharex=True, sharey=True)
    figd, axd = plt.subplots(nrows=2, ncols=3, figsize=(18, 12), dpi=120, sharex=True, sharey=True)
    display = pyart.graph.RadarDisplay(radar)
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    kws = dict(sweep=0)
    zdrkws = dict(vmin=-4, vmax=4, cmap='pyart_ChaseSpectral')
    display.plot('DBZHC', ax=axz[0,0], **zkws, **kws)
    display.plot('DBZHA', ax=axz[0,1], **zkws, **kws)
    display.plot('DBZHB', ax=axz[0,2], **zkws)
    display.plot('DBZH', ax=axz[1,0], **zkws, **kws)
    display.plot('PHIDPA', ax=axz[1,1], vmin=0, vmax=360, cmap='hsv', **kws)
    display.plot('RHOHV', ax=axz[2,0], vmin=0.8, vmax=1, **kws)
    display.plot('PIA', ax=axz[2,1], vmin=0, vmax=8, **kws)
    display.plot('SPEC', ax=axz[2,2], vmin=0, vmax=0.5, **kws)
    #display.plot('PIA_filtered', sweep=0, ax=axz[2,2], vmin=0, vmax=22)
    display.plot('ZDR', ax=axz[1,2], **zdrkws, **kws)
    figz.tight_layout()
    display.plot('ZDR', ax=axd[0,0], **zdrkws, **kws)
    display.plot('ZDRC', ax=axd[1,0], **zdrkws, **kws)
    display.plot('ZDRA', ax=axd[0,1], **zdrkws, **kws)
    display.plot('ZDRB', ax=axd[0,2], **zdrkws, **kws)
    display.plot('PIDA', ax=axd[1,1], vmin=0, vmax=6, **kws)
    display.plot('PIDA_filtered', ax=axd[1,2], vmin=0, vmax=6, **kws)
    figd.tight_layout()
    #print(radar.fields['SPEC']['data'].max())
    fout = '/tmp/rad.h5'
    pyart.aux_io.write_odim_h5(fout, radar)
