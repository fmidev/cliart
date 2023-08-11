# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import h5py
import pyart.correct
import numpy as np
from pyart.correct.attenuation import _param_attzphi_table
from scipy.signal import savgol_filter

from radproc.io import read_h5
from radproc.filtering import filter_field
from vaimennuskorjain._version import __version__


def phidp_base0(radar):
    """Add shifted and filtered phidp field."""
    gf = nonmet_filter(radar, rhohv_min=0.9)
    phidp_corr = radar.fields['PHIDP']['data'].copy()
    phidp_valid = phidp_corr.copy()
    phidp_valid.mask = np.ma.logical_or(gf.gate_excluded, np.isnan(phidp_corr)).filled(True)
    phidp_base = np.ma.median(phidp_valid.min(axis=1))
    phidp_corr -= phidp_base
    mask = np.ma.getmaskarray(phidp_corr)
    phidp_corr.mask = np.logical_or(mask, phidp_corr < 0).filled(True)
    radar.add_field_like('PHIDP', 'PHIDPA', phidp_corr, replace_existing=True)


def nonmet_filter(radar, rhohv_min=0.8, z_min=0.5):
    gf = pyart.correct.GateFilter(radar)
    gf.exclude_below('DBZH', 10)
    gf.exclude_above('ZDR', 2, op='and')
    gf.exclude_below('DBZH', z_min)
    gf.exclude_below('RHOHV', rhohv_min)
    return gf


def correct_attenuation(infile, ml=None, band='C', **kws):
    if ml is None:
        with h5py.File(infile) as f:
            ml = f['how'].attrs['freeze']*1000
    radar = read_h5(infile, file_field_names=True)
    phidp_base0(radar)
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDPA')
    spec, pia, cor_z, specd, pida, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
         temp_ref='fixed_fzl', fzl=ml, doc=15, gatefilter=nonmet_filter(radar),
         **namekws, **attnparams, **kws)
    radar.add_field('DBZHA', cor_z)
    radar.add_field('PIA', pia)
    radar.add_field('SPEC', spec)
    radar.add_field('PIDA', pida)
    radar.add_field('ZDRA', cor_zdr)
    smoothen_attn_cor(radar)
    smoothen_attn_cor(radar, pia_field='PIDA', src_field='ZDR',
                      template_field='ZDRA', dest_field='ZDRB')
    return radar


def smoothen_attn_cor(radar, pia_field='PIA', src_field='DBZH',
                      template_field='DBZHA', dest_field='DBZHB'):
    """angular smooting on attenuation correction"""
    filter_field(radar, pia_field, filterfun=savgol_filter, axis=0, window_length=6, polyorder=3)
    data = radar.fields[src_field]['data']+radar.fields[pia_field+'_filtered']['data']
    radar.add_field_like(template_field, dest_field, data=data, replace_existing=True)
