"""playing around with pysteps"""

import os

import pyart
import pysteps
import matplotlib.pyplot as plt
import numpy as np
from radproc.radar import z_r_qpe, dummy_radar, pyart_aeqd, PYART_AEQD_FMT
from scipy.ndimage import map_coordinates


def advection_correction(p1, p2, tdelta=5, dt=1):
    """
    p1, p2: precipitation fields
    tdelta: time between two observations (5 min)
    dt: interpolation timestep (1 min)
    """
    # Evaluate advection
    pp = np.nan_to_num(np.array([p1, p2]))
    oflow_method = pysteps.motion.get_method("LK")
    fd_kwargs = {"buffer_mask": 10}  # avoid edge effects
    flow = oflow_method(np.log(pp), fd_kwargs=fd_kwargs)
    # Perform temporal interpolation
    ppd = np.zeros((pp[0].shape))
    x, y = np.meshgrid(np.arange(pp[0].shape[1], dtype=float),
                       np.arange(pp[0].shape[0], dtype=float))
    for i in range(dt, tdelta + dt, dt):
        pos1 = (y - i/tdelta*flow[1], x - i/tdelta*flow[0])
        pp1 = map_coordinates(pp[0], pos1, order=1)
        pos2 = (y + (tdelta-i)/tdelta*flow[1], x + (tdelta-i)/tdelta*flow[0])
        pp2 = map_coordinates(pp[1], pos2, order=1)
        ppd += (tdelta-i)*pp1 + i*pp2
    return dt/tdelta**2*ppd


def import_fmi_hdf5(fname):
    radar = dummy_radar(fname)
    z_r_qpe(radar, dbz_field='DBZH', lwe_field='RATE')
    size = 512
    resolution = 1000
    r_m = size*resolution/2
    grid_shape = (1, size, size)
    grid_limits = ((0, 5000), (-r_m, r_m), (-r_m, r_m))
    proj = pyart_aeqd(radar)
    projstr = PYART_AEQD_FMT.format(**proj)
    grid = pyart.map.grid_from_radars(radar, grid_shape=grid_shape,
                                      grid_limits=grid_limits, fields=['RATE'],
                                      grid_projection=proj)
    data = np.squeeze(grid.fields['RATE']['data'].filled(np.nan))
    meta = dict(projection=projstr,
                cartesian_unit='m',
                x1=grid.x['data'][0],
                x2=grid.x['data'][-1],
                y1=grid.y['data'][0],
                y2=grid.y['data'][-1],
                xpixelsize=resolution,
                ypixelsize=resolution,
                yorigin='upper',
                institution='Finnish Meteorological Institute',
                accutime=5.0,
                unit='mm/h',
                transform=None,
                zerovalue=0.0,
                zr_a=223.0,
                zr_b=1.53)
    return data, meta


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
