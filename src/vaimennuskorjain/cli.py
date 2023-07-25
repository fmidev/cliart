# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import click
import pyart.aux_io

from vaimennuskorjain import correct_attenuation
from vaimennuskorjain._version import __version__


@click.command()
@click.argument('inputfile', type=click.Path(exists=True, dir_okay=False,
                                             readable=True))
@click.option('-o', '--output-file', type=click.Path(dir_okay=False),
              help='output HDF5 file path',  metavar='PATH')
@click.version_option(version=__version__, prog_name='vaimennuskorjain')
def vaimennuskorjain(inputfile, output_file):
    """Perform attenuation correction on INPUTFILE."""
    radar = correct_attenuation(inputfile)
    pyart.aux_io.write_odim_h5(output_file, radar)
