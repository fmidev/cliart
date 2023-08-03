# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import h5py
import pyart.correct
from pyart.correct.attenuation import _param_attzphi_table
from scipy.signal import savgol_filter

from radproc.io import read_h5
from radproc.filtering import filter_field


def correct_attenuation(infile, ml=None, band='C', **kws):
    if ml is None:
        with h5py.File(infile) as f:
            ml = f['how'].attrs['freeze']*1000
    radar = read_h5(infile, file_field_names=True)
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDP')
    spec, pia, cor_z, specd, pida, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
         temp_ref='fixed_fzl', fzl=ml, doc=20, **namekws, **attnparams, **kws)
    radar.add_field('DBZHA', cor_z)
    radar.add_field('PIA', pia)
    radar.add_field('SPEC', spec)
    radar.add_field('PIDA', pida)
    radar.add_field('ZDRA', cor_zdr)
    smoothen_attn_cor(radar)
    smoothen_attn_cor(radar, pia_field='PIDA', src_field='ZDR',
                      template_field='ZDRA', dest_field='ZDRB')
    if radar.ray_angle_res is None:
        # TODO: open issue on github
        # TODO: check the correct resolution
        radar.ray_angle_res = {'data': 360/radar.rays_per_sweep['data']}
    return radar


def smoothen_attn_cor(radar, pia_field='PIA', src_field='DBZH',
                      template_field='DBZHA', dest_field='DBZHB'):
    """angular smooting on attenuation correction"""
    filter_field(radar, pia_field, filterfun=savgol_filter, axis=0, window_length=6, polyorder=3)
    data = radar.fields[src_field]['data']+radar.fields[pia_field+'_filtered']['data']
    radar.add_field_like(template_field, dest_field, data=data, replace_existing=True)
