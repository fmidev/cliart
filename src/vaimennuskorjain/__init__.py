# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import pyart.correct
import numpy as np
from pyart.correct.attenuation import _param_attzphi_table
from pyart.core import Radar
from scipy.signal import savgol_filter

from radproc.filtering import filter_field
from radproc.radar import nonmet_filter
from vaimennuskorjain._version import __version__


ATTN_FIELDS = {'DBZHA': 'DBZH with attenuation correction',
               'DBZHAS': 'DBZH with smoothed attenuation correction',
               'PIA': 'path integrated attenuation',
               'PIAS': 'smoothed path integrated attenuation',
               'SPEC': 'specific attenuation',
               'ZDRA': 'ZDR with attenuation correction',
               'ZDRAS': 'ZDR with smoothed attenuation correction',
               'PIDA': 'path integrated differential attenuation',
               'PIDAS': 'smoothed path integrated differential attenuation',
               'SPECD': 'specific differential attenuation',
               'AQ': 'relative azimuthal smoothness of DBZHAS to DBZH'}


def phidp_base0(radar: Radar):
    """shifted and filtered phidp field that starts from zero degrees"""
    gf = nonmet_filter(radar, rhohv_min=0.9)
    phidp_corr = radar.fields['PHIDP']['data'].copy()
    phidp_valid = phidp_corr.copy()
    phidp_valid.mask = np.ma.logical_or(gf.gate_excluded, np.isnan(phidp_corr)).filled(True)
    phidp_base = np.ma.median(phidp_valid.min(axis=1))
    phidp_corr -= phidp_base
    mask = np.ma.getmaskarray(phidp_corr)
    phidp_corr.mask = np.logical_or(mask, phidp_corr < 0).filled(True)
    radar.add_field_like('PHIDP', 'PHIDPA', phidp_corr, replace_existing=True)


def correct_attenuation_zphi(radar: Radar, ml=None, band='C', **kws):
    """attenuation correction using PyART zphi implementation"""
    phidp_base0(radar) # TODO: read from metadata when available
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDPA')
    spec, pia, cor_z, specd, pida, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
         temp_ref='fixed_fzl', fzl=ml, doc=15, gatefilter=nonmet_filter(radar),
         **namekws, **attnparams, **kws)
    radar.add_field('DBZHA', cor_z)
    radar.add_field('PIA', pia, replace_existing=True)
    radar.add_field('SPEC', spec)
    radar.add_field('PIDA', pida)
    radar.add_field('ZDRA', cor_zdr)
    radar.add_field('SPECD', specd)
    smoothen_attn_cor(radar)
    smoothen_attn_cor(radar, pia_field='PIDA', smooth_pia_field='PIDAS',
                      src_field='ZDR', template_field='ZDRA', dest_field='ZDRAS')


def smoothen_attn_cor(radar: Radar, pia_field='PIA', smooth_pia_field='PIAS',
                      src_field='DBZH', template_field='DBZHA',
                      dest_field='DBZHAS'):
    """angular smooting on attenuation correction"""
    filter_field(radar, pia_field, field_name=smooth_pia_field,
                 filterfun=savgol_filter, axis=0, window_length=6, polyorder=3)
    data = radar.fields[src_field]['data']+radar.fields[smooth_pia_field]['data']
    radar.add_field_like(template_field, dest_field, data=data, replace_existing=True)


def _angular_diff(data):
    z_ray0 = data[0].reshape(1, data.shape[1])
    return np.ma.abs(np.ma.diff(data, axis=0, append=z_ray0))


def attn_quality_field(radar: Radar, add_field=False) -> dict:
    """relative azimuthal smoothness of DBZHAS to DBZH"""
    aqdata = []
    for sweep in radar.sweep_number['data']:
        dbzhas = radar.get_field(sweep, 'DBZHAS')
        dbzh = radar.get_field(sweep, 'DBZH')
        diffz = _angular_diff(dbzh)
        diffza = _angular_diff(dbzhas)
        mz = np.ma.median(diffz, axis=1)
        mza = np.ma.median(diffza, axis=1)
        aq = np.ma.column_stack([mz-mza]*500)
        aq.mask = np.logical_or(aq.mask, dbzhas.mask)
        aqdata.append(aq)
    aq_field = dict(data=np.ma.concatenate(aqdata))
    if add_field:
        radar.add_field('AQ', aq_field)
    return aq_field
