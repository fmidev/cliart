"""playing around with pysteps"""

import os

import pysteps
import matplotlib.pyplot as plt
import numpy as np

from radproc.dynamics import import_fmi_hdf5, advection_correction


if __name__ == '__main__':
    pgmfile = os.path.expanduser('~/data/pgm/201705091045_fmi.radar.composite.lowest_FIN_SUOMI1.pgm.gz')
    h5file1 = os.path.expanduser('~/data/polar/fikor/201708121500_radar.polar.fikor.h5')
    h5file2 = os.path.expanduser('~/data/polar/fikor/201708121515_radar.polar.fikor.h5')
    dat1, _, meta1 = pysteps.io.import_fmi_pgm(pgmfile, gzipped=True)
    r1, metar1 = pysteps.utils.conversion.to_rainrate(dat1, meta1)
    p1, metap1 = import_fmi_hdf5(h5file1)
    p2, metap2 = import_fmi_hdf5(h5file2)
    pp = (np.nan_to_num(p1)+np.nan_to_num(p2))*0.5
    pac = advection_correction(p1, p2, tdelta=15, dt=1)
    fig, ax = plt.subplots(ncols=2, nrows=2)
    pysteps.visualization.plot_precip_field(p1, ax=ax[0,0])
    pysteps.visualization.plot_precip_field(p2, ax=ax[0,1])
    pysteps.visualization.plot_precip_field(pac, ax=ax[1,0])
    pysteps.visualization.plot_precip_field(pp, ax=ax[1,1])
