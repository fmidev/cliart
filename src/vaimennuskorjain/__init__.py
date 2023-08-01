# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import pyart.correct
from pyart.correct.attenuation import _param_attzphi_table
from scipy.signal import savgol_filter

from radproc.io import read_h5
from radproc.filtering import filter_field


def correct_attenuation(infile, ml=3000, band='C', **kws):
    radar = read_h5(infile, file_field_names=True)
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDP')
    spec, pia, cor_z, specd, pida, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
         temp_ref='fixed_fzl', fzl=ml, doc=20, **namekws, **attnparams, **kws)
    radar.add_field('DBZHA', cor_z)
    radar.add_field('PIA', pia)
    radar.add_field('SPEC', spec)
    radar.add_field('ZDRA', cor_zdr)
    if radar.ray_angle_res is None:
        # TODO: open issue on github
        # TODO: check the correct resolution
        radar.ray_angle_res = {'data': 360/radar.rays_per_sweep['data']}
    return radar


def smoothen_atten_cor(radar):
    filter_field(radar, 'PIA', filterfun=savgol_filter, axis=0, window_length=6, polyorder=3)
    data = radar.fields['DBZH']['data']+radar.fields['PIA_filtered']['data']
    radar.add_field_like('DBZHA', 'DBZHB', data=data, replace_existing=True)
