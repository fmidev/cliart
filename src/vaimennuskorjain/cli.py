# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import h5py
import click
import pyart.aux_io

from radproc.io import read_h5
from vaimennuskorjain import correct_attenuation_zphi, read_odim_ml, ATTN_FIELDS
from vaimennuskorjain._version import __version__


def _field_help():
    base = 'Variable to write. This option can be selected multiple times. '\
        'The default is to write all variables.'
    fieldstr = ''.join('\n{}: {}'.format(key, val) for key, val in ATTN_FIELDS.items())
    return base+'\n\n\b'+fieldstr


@click.command()
@click.argument('inputfile', type=click.Path(exists=True, dir_okay=False,
                                             readable=True))
@click.option('-o', '--output-file', type=click.Path(dir_okay=False),
              help='output HDF5 file path',  metavar='PATH', required=True)
@click.option('-f', '--field', type=click.Choice(list(ATTN_FIELDS), case_sensitive=False),
              multiple=True, help=_field_help(), default=list(ATTN_FIELDS))
@click.option('--orig/--no-orig', default=True, show_default=False,
              help='Include/exclude all data from the input file. Included by default.')
@click.option('--ml', metavar='HEIGHT', help='override melting layer height [meters]', type=float)
@click.version_option(version=__version__, prog_name='vaimennuskorjain')
def vaimennuskorjain(inputfile, output_file, ml, field, orig):
    """Perform attenuation correction on INPUTFILE.

    Py-ART calculate_attenuation_zphi is used under the hood.
    Melting layer height is read from the HDF5 attribute how/freeze."""
    if ml is None:
        ml = read_odim_ml(inputfile)
    radar = read_h5(inputfile, file_field_names=True)
    if orig:
        field = list(radar.fields) + list(field)
    correct_attenuation_zphi(radar, ml)
    pyart.aux_io.write_odim_h5(output_file, radar, field_names=field)
    with h5py.File(output_file, 'a') as new:
        with h5py.File(inputfile) as old:
            new['how'].attrs.update(old['how'].attrs)
