# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import h5py
import click
import pyart.aux_io

from vaimennuskorjain import correct_attenuation_zphi
from vaimennuskorjain._version import __version__


@click.command()
@click.argument('inputfile', type=click.Path(exists=True, dir_okay=False,
                                             readable=True))
@click.option('-o', '--output-file', type=click.Path(dir_okay=False),
              help='output HDF5 file path',  metavar='PATH', required=True)
@click.option('--ml', metavar='HEIGHT', help='override melting layer height [meters]', type=float)
@click.version_option(version=__version__, prog_name='vaimennuskorjain')
def vaimennuskorjain(inputfile, output_file, ml):
    """Perform attenuation correction on INPUTFILE.

    Py-ART calculate_attenuation_zphi is used under the hood.
    Melting layer height is read from the HDF5 attribute how/freeze."""
    radar = correct_attenuation_zphi(inputfile, ml)
    pyart.aux_io.write_odim_h5(output_file, radar)
    with h5py.File(output_file, 'a') as new:
        with h5py.File(inputfile) as old:
            new['how'].attrs.update(old['how'].attrs)
