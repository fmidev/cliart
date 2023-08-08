import os

import pyart
import matplotlib.pyplot as plt

from vaimennuskorjain import correct_attenuation


if __name__ == '__main__':
    #fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202206030010_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307081105_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307030835_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307010920_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/polar/fivan/201708121600_radar.polar.fivan.h5')
    #fname = os.path.expanduser('~/data/polar/fikor/202308071610_radar.polar.fikor.h5')
    fname = os.path.expanduser('~/data/polar/fikor/202308080540_radar.polar.fikor.h5')
    radar = correct_attenuation(fname, smooth_window_len=6)
    figz, axz = plt.subplots(nrows=3, ncols=3, figsize=(17, 17), dpi=110)
    figd, axd = plt.subplots(nrows=2, ncols=3, figsize=(18, 12), dpi=120)
    display = pyart.graph.RadarDisplay(radar)
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    zdrkws = dict(vmin=-4, vmax=4, cmap='pyart_ChaseSpectral')
    display.plot('DBZHC', sweep=0, ax=axz[0,0], **zkws)
    display.plot('DBZHA', sweep=0, ax=axz[0,1], **zkws)
    display.plot('DBZHB', sweep=0, ax=axz[0,2], **zkws)
    display.plot('DBZH', sweep=0, ax=axz[1,0], **zkws)
    display.plot('PHIDP', sweep=0, ax=axz[1,1], vmin=0, vmax=360, cmap='hsv')
    display.plot('RHOHV', sweep=0, ax=axz[2,0], vmin=0.8, vmax=1)
    display.plot('PIA', sweep=0, ax=axz[2,1], vmin=0, vmax=22)
    display.plot('PIA_filtered', sweep=0, ax=axz[2,2], vmin=0, vmax=22)
    display.plot('ZDR', sweep=0, ax=axz[1,2], **zdrkws)
    figz.tight_layout()
    display.plot('ZDR', sweep=0, ax=axd[0,0], **zdrkws)
    display.plot('ZDRC', sweep=0, ax=axd[1,0], **zdrkws)
    display.plot('ZDRA', sweep=0, ax=axd[0,1], **zdrkws)
    display.plot('ZDRB', sweep=0, ax=axd[0,2], **zdrkws)
    display.plot('PIDA', sweep=0, ax=axd[1,1], vmin=0, vmax=6)
    display.plot('PIDA_filtered', sweep=0, ax=axd[1,2], vmin=0, vmax=6)
    figd.tight_layout()
    #print(radar.fields['SPEC']['data'].max())
    fout = '/tmp/rad.h5'
    pyart.aux_io.write_odim_h5(fout, radar)
