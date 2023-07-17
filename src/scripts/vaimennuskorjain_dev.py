import os
import pyart.correct
from pyart.correct.attenuation import _param_attzphi_table

from radproc.io import read_h5


if __name__ == '__main__':
    fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    radar = read_h5(fname)
    a_coef, beta, c, d = _param_attzphi_table()['C']
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    _, _, cor_z, _, _, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
        refl_field='reflectivity_horizontal', **attnparams)
