# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import click

from vaimennuskorjain._version import __version__


@click.command()
@click.argument('inputfile', type=click.Path(exists=True, dir_okay=False,
                                             readable=True))
@click.option('-o', '--outputfile', type=click.Path(dir_okay=False),
              help='output HDF5 file path',  metavar='PATH')
@click.version_option(version=__version__, prog_name='vaimennuskorjain')
def vaimennuskorjain(inputfile, outputfile):
    """Perform attenuation correction on INPUTFILE."""
    pass
