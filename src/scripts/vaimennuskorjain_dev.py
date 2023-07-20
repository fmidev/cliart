import os
import pyart.correct
from pyart.correct.attenuation import _param_attzphi_table

from radproc.io import read_h5


if __name__ == '__main__':
    #fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    fname = os.path.expanduser('~/data/pvol/202206030010_fivih_PVOL.h5')
    radar = read_h5(fname, file_field_names=True)
    #radar = pyart.aux_io.read_odim_h5(fname, include_datasets=['dataset1'], file_field_names=True)
    a_coef, beta, c, d = _param_attzphi_table()['C']
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDP')
    _, _, cor_z, _, _, cor_zdr = pyart.correct.calculate_attenuation_zphi(radar,
         temp_ref='fixed_fzl', **namekws, **attnparams)
    radar.add_field('DBZHA', cor_z)
    radar.add_field('ZDRA', cor_zdr)
    if radar.ray_angle_res is None:
        radar.ray_angle_res = {'data': 360/radar.rays_per_sweep['data']}
        # TODO: open issue
    pyart.aux_io.write_odim_h5('/tmp/rad.h5', radar)
