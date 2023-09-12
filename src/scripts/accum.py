"""impact of attenuation to rain accumulation"""

import os
import glob

import numpy as np
import pyart

from radproc.radar import z_r_qpe, dummy_radar
from radproc.visual import canvas
from vaimennuskorjain import correct_attenuation_zphi


def rfield(data):
    return {'units': 'mm h-1', 'data': data}


def precips(ls):
    ps = []
    pcs = []
    for fname in ls:
        radar = correct_attenuation_zphi(fname, smooth_window_len=6)
        ps.append(z_r_qpe(radar, dbz_field='DBZH', add_field=False)['data'].filled(0))
        pcs.append(z_r_qpe(radar, dbz_field='DBZHB', add_field=False)['data'].filled(0))
    return np.stack(ps), np.stack(pcs)


if __name__ == '__main__':
    rcase = '20170812'
    #rcase = '20230807'
    site = 'fivan'
    patt = os.path.expanduser(f'~/data/polar/{site}/{rcase}*_radar.polar.{site}.h5')
    ls = sorted(glob.glob(patt))
    p, pc = precips(ls)
    radar = dummy_radar(ls[0])
    radar.add_field('P', rfield(p.sum(axis=0)/12))
    radar.add_field('PC', rfield(pc.sum(axis=0)/12))
    display = pyart.graph.RadarMapDisplay(radar)
    #fig, axs = canvas(radar, 2, 1)
    d = 360000
    kws = dict(resolution='50m', add_grid_lines=False, width=d, height=d)
    #display.plot_ppi_map('P', ax=axs[0], vmin=0, vmax=20, **kws)
    #display.plot_ppi_map('PC', ax=axs[1], vmin=0, vmax=20, **kws)
