# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import pyart.correct
from pyart.correct.attenuation import _param_attzphi_table

from radproc.io import read_h5


def correct_attenuation(infile, band='C'):
    radar = read_h5(infile, file_field_names=True)
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDP')
    spec, pia, cor_z, specd, pida, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
         temp_ref='fixed_fzl', **namekws, **attnparams)
    radar.add_field('DBZHA', cor_z)
    #radar.add_field('PIA', pia)
    #radar.add_field('SPEC', spec)
    radar.add_field('ZDRA', cor_zdr)
    if radar.ray_angle_res is None:
        radar.ray_angle_res = {'data': 360/radar.rays_per_sweep['data']}
        # TODO: open issue
    return radar
