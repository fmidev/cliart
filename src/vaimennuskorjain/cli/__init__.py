# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import click

from vaimennuskorjain._version import __version__


@click.command()
@click.version_option(version=__version__, prog_name='vaimennuskorjain')
def vaimennuskorjain():
    pass
