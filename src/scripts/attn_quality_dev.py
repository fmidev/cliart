"""Attenuation correction quality field development script"""

import os

import pyart
import matplotlib.pyplot as plt
import numpy as np

from radproc.io import read_h5, read_odim_ml
from vaimennuskorjain import correct_attenuation_zphi


def add_single_sweep_field(radar, data, sweep: int, name: str, **kws) -> None:
    afield = radar.fields[list(radar.fields)[0]]['data'].copy()
    res_ang = data.shape[0]
    afield[res_ang*sweep:res_ang*(sweep+1), :] = data
    field = dict(data=afield)
    radar.add_field(name, field, **kws)


if __name__ == '__main__':
    plt.close('all')
    sweep = 0
    fname = os.path.expanduser('~/data/polar/fivan/201708121600_radar.polar.fivan.h5')
    ml = read_odim_ml(fname)
    radar = read_h5(fname, file_field_names=True)
    correct_attenuation_zphi(radar, ml=ml)
    dbzhas = radar.get_field(sweep, 'DBZHAS')
    dbzh = radar.get_field(sweep, 'DBZH')
    z_ray0 = dbzh[0].reshape(1, dbzh.shape[1])
    diff = np.ma.abs(np.ma.diff(dbzh, axis=0, append=z_ray0))
    add_single_sweep_field(radar, diff, sweep, 'DIFF')
    #
    figz, axz = plt.subplots(nrows=3, ncols=3, figsize=(17, 17), dpi=110, sharex=True, sharey=True)
    display = pyart.graph.RadarDisplay(radar)
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    kws = dict(sweep=sweep)
    zdrkws = dict(vmin=-4, vmax=4, cmap='pyart_ChaseSpectral')
    display.plot('DBZHC', ax=axz[0,0], **zkws, **kws)
    display.plot('DBZHA', ax=axz[0,1], **zkws, **kws)
    display.plot('DBZHAS', ax=axz[0,2], **zkws)
    display.plot('DBZH', ax=axz[1,0], **zkws, **kws)
    display.plot('PHIDPA', ax=axz[1,1], vmin=0, vmax=360, cmap='hsv', **kws)
    display.plot('RHOHV', ax=axz[2,0], vmin=0.8, vmax=1, **kws)
    display.plot('PIA', ax=axz[2,1], vmin=0, vmax=8, **kws)
    display.plot('SPEC', ax=axz[2,2], vmin=0, vmax=0.5, **kws)
    display.plot('DIFF', ax=axz[1,2], vmin=0, vmax=10, **kws)
    figz.tight_layout()
