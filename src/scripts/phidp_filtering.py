import os

import pyart
import numpy as np
import matplotlib.pyplot as plt

from vaimennuskorjain import correct_attenuation, nonmet_filter
from radproc.io import read_h5


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
    radar = read_h5(fname, file_field_names=True)
    fig, ax = plt.subplots(ncols=2, figsize=(11, 5))
    kws = dict(sweep=0)
    display = pyart.graph.RadarDisplay(radar)
    display.plot('PHIDP', ax=ax[0], vmin=0, vmax=360, cmap='hsv', **kws)
    display.plot('PHIDPC', ax=ax[1], vmin=0, vmax=360, cmap='hsv', **kws)
    fig.tight_layout()
