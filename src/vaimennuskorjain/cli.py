# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import click
from pyart.graph.common import generate_radar_time_begin

from radproc.io import read_h5, write_h5, read_odim_ml
from radproc.tools import source2dict
from radproc.cli import gen_help
from vaimennuskorjain import correct_attenuation_zphi, attn_quality_field, ATTN_FIELDS
from vaimennuskorjain._version import __version__


def _field_help():
    base = 'Variable to write. This option can be selected multiple times. '\
        'The default is to write all variables.'
    return gen_help(base, ATTN_FIELDS)


def _out_help():
    variables = {'timestamp': 'scan start time as %Y%m%d%H%M',
                 'site': 'radar site abbreviation'}
    base = 'Output file path. '\
        'Special variables can be used enclosed in curly brackets, e.g. '\
        '/path/to/{site}/file_{timestamp}.h5.'
    return gen_help(base, variables)


@click.command()
@click.argument('inputfile', type=click.Path(exists=True, dir_okay=False,
                                             readable=True))
@click.option('-o', '--output-file', type=click.Path(dir_okay=False),
              help=_out_help(),  metavar='PATH', required=True)
@click.option('-f', '--field', type=click.Choice(list(ATTN_FIELDS), case_sensitive=False),
              multiple=True, help=_field_help(), default=list(ATTN_FIELDS))
@click.option('--orig/--no-orig', default=True, show_default=False,
              help='Include/exclude all data from the input file. Included by default.')
@click.option('--ml', metavar='METERS', help='override melting layer cut-off altitude', type=float)
@click.version_option(version=__version__, prog_name='vaimennuskorjain')
def vaimennuskorjain(inputfile, output_file, ml, field, orig):
    """Perform attenuation correction on INPUTFILE.

    Py-ART calculate_attenuation_zphi is used under the hood.
    Melting layer height is read from the HDF5 attribute how/freeze."""
    if ml is None:
        ml = read_odim_ml(inputfile)
    radar = read_h5(inputfile, file_field_names=True)
    t = generate_radar_time_begin(radar)
    tstamp = t.strftime('%Y%m%d%H%M')
    site = source2dict(radar.metadata['source'])['NOD']
    if orig:
        field = list(radar.fields) + list(field)
    correct_attenuation_zphi(radar, ml)
    if 'AQ' in field:
        attn_quality_field(radar, add_field=True)
    outfile = output_file.format(timestamp=tstamp, site=site)
    write_h5(radar, outfile, inputfile=inputfile, field_names=field)
