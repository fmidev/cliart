import os

import pyart

from vaimennuskorjain import correct_attenuation


if __name__ == '__main__':
    #fname = os.path.expanduser('~/data/pvol/202208132125_fivih_PVOL.h5')
    fname = os.path.expanduser('~/data/pvol/202206030010_fivih_PVOL.h5')
    radar = correct_attenuation(fname)
    pyart.aux_io.write_odim_h5('/tmp/rad.h5', radar)
