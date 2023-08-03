import os

import pyart
import matplotlib.pyplot as plt

from vaimennuskorjain import correct_attenuation, smoothen_atten_cor


if __name__ == '__main__':
    #fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202206030010_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307081105_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307030835_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307010920_fivih_PVOL.h5')
    fname = os.path.expanduser('~/data/polar/fivan/201708121600_radar.polar.fivan.h5')
    radar = correct_attenuation(fname, smooth_window_len=6)
    figz, axz = plt.subplots(nrows=2, ncols=3, figsize=(18, 12), dpi=120)
    display = pyart.graph.RadarDisplay(radar)
    zmax = 50
    display.plot('DBZHC', sweep=0, ax=axz[0,0], vmin=0, vmax=zmax, cmap='viridis')
    display.plot('DBZHA', sweep=0, ax=axz[0,1], vmin=0, vmax=zmax, cmap='viridis')
    display.plot('DBZHB', sweep=0, ax=axz[0,2], vmin=0, vmax=zmax, cmap='viridis')
    display.plot('DBZH', sweep=0, ax=axz[1,0], vmin=0, vmax=zmax, cmap='viridis')
    display.plot('PHIDP', sweep=0, ax=axz[1,1], vmin=0, vmax=350)
    display.plot('ZDR', sweep=0, ax=axz[1,2], vmin=-3, vmax=2)
    figz.tight_layout()
    #print(radar.fields['SPEC']['data'].max())
    pyart.aux_io.write_odim_h5('/tmp/rad.h5', radar)
