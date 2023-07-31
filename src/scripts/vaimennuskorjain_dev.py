import os

import pyart
import matplotlib.pyplot as plt

from vaimennuskorjain import correct_attenuation


if __name__ == '__main__':
    #fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202206030010_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307081105_fivih_PVOL.h5')
    #fname = os.path.expanduser('~/data/pvol/202307030835_fivih_PVOL.h5')
    fname = os.path.expanduser('~/data/pvol/202307010920_fivih_PVOL.h5')
    radar = correct_attenuation(fname, ml=3500)
    figz, axz = plt.subplots(nrows=2, ncols=3, figsize=(18, 12), dpi=150)
    display = pyart.graph.RadarDisplay(radar)
    display.plot('DBZH', sweep=0, ax=axz[0,0], vmin=0, vmax=40, cmap='viridis')
    display.plot('DBZHA', sweep=0, ax=axz[0,1], vmin=0, vmax=40, cmap='viridis')
    #display.plot('SPEC', sweep=0, ax=axz[0,2], vmin=0, vmax=0.5)
    display.plot('KDP', sweep=0, ax=axz[1,0], vmin=0, vmax=0.3)
    display.plot('PHIDP', sweep=0, ax=axz[1,1], vmin=0, vmax=150)
    display.plot('ZDR', sweep=0, ax=axz[1,2], vmin=-1, vmax=2)
    figz.tight_layout()
    #print(radar.fields['SPEC']['data'].max())
    pyart.aux_io.write_odim_h5('/tmp/rad.h5', radar)
