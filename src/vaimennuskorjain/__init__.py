# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import pyart.correct
from pyart.correct.attenuation import _param_attzphi_table

from radproc.io import read_h5


def correct_attenuation(infile, outfile, band='C'):
    radar = read_h5(infile)
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    _, _, cor_z, _, _, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
        refl_field='reflectivity_horizontal', **attnparams)
