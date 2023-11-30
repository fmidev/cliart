"""animated attenuation correction visualization"""

import os
import glob

import pyart
import matplotlib.pyplot as plt
from matplotlib import animation
from functools import partial

from radproc.io import read_h5, read_odim_ml
from vaimennuskorjain import correct_attenuation_zphi
from radproc.visual import canvas

colorbar_present = False


def plot_atten(display, ax, var='DBZH', title='DBZ', plot_cb=True, suffix=''):
    zkws = dict(vmin=0, vmax=50, cmap='pyart_HomeyerRainbow')
    piakws = dict(vmin=0, vmax=15, cmap='gnuplot2_r')
    d = 360000
    kws = dict(colorbar_flag=plot_cb, sweep=0, resolution='50m', add_grid_lines=True, width=d, height=d)
    plotfun = display.plot_ppi_map
    plotfun(var, ax=ax, **zkws, **kws, title=title,
            colorbar_label='corrected equivalent reflectivity factor (dBZ)')


if __name__ == '__main__':
    kws_vaisala = dict(var='DBZHC', title='Korjattu  DBZ, Vaisala', suffix='vaisala')
    kws_orig = dict(var='DBZH', title='Korjaamaton DBZ', suffix='orig')
    kws_zphi = dict(var='DBZHAS', title='Korjattu DBZ, ZPHI', suffix='zphi')
    fname = os.path.expanduser('~/data/polar/fivan/201708121600_radar.polar.fivan.h5')
    ml = read_odim_ml(fname)
    radar = read_h5(fname, file_field_names=True)
    correct_attenuation_zphi(radar, ml=ml)
    display = pyart.graph.RadarMapDisplay(radar)
    resultsdir = os.path.expanduser('~/results/vaimennus')
    os.makedirs(resultsdir, exist_ok=True)
    for d in [kws_vaisala, kws_orig, kws_zphi]:
        fig, ax = canvas(radar, 1, 1)
        plot_atten(display, ax, **d)
        fig.savefig(os.path.join(resultsdir, 'attn_'+d['suffix']+'.png'))
