# SPDX-FileCopyrightText: 2023-present Jussi Tiira <jussi.tiira@fmi.fi>
#
# SPDX-License-Identifier:

"""vaimennuskorjain: attenuation correction for weather radar data"""

# Built-in modules
from typing import Any, Optional

# Third party modules
import pyart.correct
import numpy as np
from pyart.correct.attenuation import _param_attzphi_table
from pyart.core import Radar
from scipy.signal import savgol_filter

# FMI modules
from radproc.filtering import filter_field
from radproc.radar import nonmet_filter
from vaimennuskorjain._version import __version__


ATTN_FIELDS = {'DBZHA': 'DBZH with attenuation correction',
               'DBZHAS': 'DBZH with smoothed attenuation correction',
               'PIA': 'path integrated attenuation',
               'PIAS': 'smoothed path integrated attenuation',
               'SPEC': 'specific attenuation',
               'ZDRA': 'ZDR with attenuation correction',
               'ZDRAS': 'ZDR with smoothed attenuation correction',
               'PIDA': 'path integrated differential attenuation',
               'PIDAS': 'smoothed path integrated differential attenuation',
               'SPECD': 'specific differential attenuation',
               'AQ': 'relative azimuthal smoothness of DBZHAS to DBZH'}


def phidp_base0(radar: Radar, phidp_base: Optional[float] = None) -> None:
    """Compute a shifted PHIDP field anchored at zero degrees and add it to the radar object.

    Subtracts a baseline offset from the PHIDP field so that it starts from
    zero degrees, then masks gates with negative values or non-meteorological
    echoes (rhohv < 0.9). The resulting field is stored as ``PHIDPA``.

    Args:
        radar: Py-ART Radar object containing a ``PHIDP`` field.
        phidp_base: Baseline offset (degrees) to subtract from PHIDP.
            If ``None``, the baseline is estimated from the data as the median
            of per-ray minimums over valid gates. This estimate may be
            inaccurate and a warning is printed.
    """
    gf = nonmet_filter(radar, rhohv_min=0.9)
    phidp_corr = radar.fields['PHIDP']['data'].copy()
    phidp_valid = phidp_corr.copy()
    phidp_valid.mask = np.ma.logical_or(gf.gate_excluded, np.isnan(phidp_corr)).filled(True)
    if phidp_base is None:
        print('Warning: phidp_base not provided, calculating from data. This may be inaccurate.')
        phidp_base = np.ma.median(phidp_valid.min(axis=1))
    phidp_corr -= phidp_base
    mask = np.ma.getmaskarray(phidp_corr)
    phidp_corr.mask = np.logical_or(mask, phidp_corr < 0).filled(True)
    radar.add_field_like('PHIDP', 'PHIDPA', phidp_corr, replace_existing=True)


def correct_attenuation_zphi(radar: Radar, ml: Optional[float] = None,
                             band: str = 'C', phidp_base: Optional[float] = None, **kws: Any) -> None:
    """Apply ZPHI attenuation correction and add corrected fields to the radar object.

    Uses the Py-ART implementation of the ZPHI method to estimate specific
    attenuation and path-integrated attenuation (PIA) from the differential
    phase (PHIDP). Both raw and angularly smoothed corrected fields are added.

    The following fields are added to ``radar``:

    * ``DBZHA``  – reflectivity corrected for attenuation
    * ``PIA``    – path integrated attenuation
    * ``SPEC``   – specific attenuation
    * ``PIDA``   – path integrated differential attenuation
    * ``ZDRA``   – ZDR corrected for differential attenuation
    * ``SPECD``  – specific differential attenuation
    * ``DBZHAS`` – angularly smoothed ``DBZHA``
    * ``PIAS``   – angularly smoothed ``PIA``
    * ``ZDRAS``  – angularly smoothed ``ZDRA``
    * ``PIDAS``  – angularly smoothed ``PIDA``

    Args:
        radar: Py-ART Radar object. Must contain ``DBZH``, ``ZDR``, and
            ``PHIDP`` fields.
        ml: Melting-layer height (metres above sea level) used as the
            freezing-level height for the ZPHI algorithm. If ``None``, Py-ART
            uses its own default.
        band: Radar frequency band used to look up ZPHI coefficients.
            Supported values follow :func:`pyart.correct.attenuation._param_attzphi_table`
            (e.g. ``'C'``, ``'S'``, ``'X'``).
        **kws: Additional keyword arguments forwarded to
            :func:`pyart.correct.calculate_attenuation_zphi`.
    """
    phidp_base0(radar, phidp_base=phidp_base)
    a_coef, beta, c, d = _param_attzphi_table()[band]
    attnparams = dict(a_coef=a_coef, beta=beta, c=c, d=d)
    namekws = dict(refl_field='DBZH', zdr_field='ZDR', phidp_field='PHIDPA')
    spec, pia, cor_z, specd, pida, cor_zdr = pyart.correct.calculate_attenuation_zphi(
        radar,
        temp_ref='fixed_fzl',
        fzl=ml,
        doc=15,
        gatefilter=nonmet_filter(radar),
        **namekws,
        **attnparams,
        **kws
    )
    radar.add_field('DBZHA', cor_z)
    radar.add_field('PIA', pia, replace_existing=True)
    radar.add_field('SPEC', spec)
    radar.add_field('PIDA', pida)
    radar.add_field('ZDRA', cor_zdr)
    radar.add_field('SPECD', specd)
    smoothen_attn_cor(radar)
    smoothen_attn_cor(
        radar,
        pia_field='PIDA',
        smooth_pia_field='PIDAS',
        src_field='ZDR',
        template_field='ZDRA',
        dest_field='ZDRAS'
    )


def smoothen_attn_cor(radar: Radar, pia_field: str = 'PIA', smooth_pia_field: str = 'PIAS',
                      src_field: str = 'DBZH', template_field: str = 'DBZHA',
                      dest_field: str = 'DBZHAS') -> None:
    """Apply azimuthal (angular) smoothing to a PIA field and produce a smoothed corrected field.

    Smooths ``pia_field`` along the azimuth axis using a Savitzky-Golay filter
    and stores the result as ``smooth_pia_field``. The smoothed PIA is then
    added to ``src_field`` to produce the smoothed corrected field ``dest_field``.

    Args:
        radar: Py-ART Radar object containing the fields specified by the
            remaining arguments.
        pia_field: Name of the path-integrated attenuation field to smooth.
        smooth_pia_field: Name of the output smoothed PIA field.
        src_field: Name of the uncorrected source field (e.g. ``'DBZH'``).
        template_field: Name of an existing corrected field whose metadata are
            used as a template when adding ``dest_field`` to the radar.
        dest_field: Name of the output smoothed corrected field.
    """
    filter_field(radar, pia_field, field_name=smooth_pia_field,
                 filterfun=savgol_filter, axis=0, window_length=6, polyorder=3)
    data = radar.fields[src_field]['data'] + radar.fields[smooth_pia_field]['data']
    radar.add_field_like(template_field, dest_field, data=data, replace_existing=True)


def _angular_diff(data):
    """Compute absolute first-order differences along the azimuth axis with wrap-around.

    Calculates ``|data[i+1] - data[i]|`` for each consecutive pair of rays,
    treating the array as circular so that the last ray is compared against
    the first.

    Args:
        data: 2-D masked array of shape ``(n_rays, n_gates)``.

    Returns:
        Masked array of the same shape as ``data`` containing the absolute
        azimuthal differences.
    """
    z_ray0 = data[0].reshape(1, data.shape[1])
    return np.ma.abs(np.ma.diff(data, axis=0, append=z_ray0))


def attn_quality_field(radar: Radar, add_field: bool = False) -> dict:
    """Compute a quality field based on the azimuthal smoothness of the corrected reflectivity.

    For each sweep the per-ray median of the absolute azimuthal gradient is
    computed for both ``DBZH`` and ``DBZHAS``. The quality metric ``AQ`` is
    the difference ``median(|Δ DBZH|) - median(|Δ DBZHAS|)``, broadcast over
    all gates. Positive values indicate that the attenuation correction
    improved the azimuthal consistency of the reflectivity field.

    Args:
        radar: Py-ART Radar object containing ``DBZH`` and ``DBZHAS`` fields.
        add_field: If ``True``, add the resulting quality field to ``radar``
            under the name ``'AQ'``.

    Returns:
        A Py-ART field dictionary with key ``'data'`` containing a masked
        array of shape ``(total_rays, n_gates)`` with the ``AQ`` values.
    """
    aqdata = []
    for sweep in radar.sweep_number['data']:
        dbzhas = radar.get_field(sweep, 'DBZHAS')
        dbzh = radar.get_field(sweep, 'DBZH')
        diffz = _angular_diff(dbzh)
        diffza = _angular_diff(dbzhas)
        mz = np.ma.median(diffz, axis=1)
        mza = np.ma.median(diffza, axis=1)
        aq = np.ma.column_stack([mz-mza]*500)
        aq.mask = np.logical_or(aq.mask, dbzhas.mask)
        aqdata.append(aq)
    aq_field = dict(data=np.ma.concatenate(aqdata))
    if add_field:
        radar.add_field('AQ', aq_field)
    return aq_field
