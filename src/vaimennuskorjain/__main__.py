# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == '__main__':
    from .cli import vaimennuskorjain

    sys.exit(vaimennuskorjain())
