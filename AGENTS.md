# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## What this is

`vaimennuskorjain` ("attenuation corrector") is a single-purpose CLI that applies Py-ART's ZPHI
attenuation correction to FMI weather radar polar volumes in ODIM HDF5 format, and writes the
corrected fields back out as HDF5.

## Commands

```shell
pip install .                     # install (pulls radproc from GitHub)
vaimennuskorjain --help

hatch run cov                     # pytest with coverage
hatch run no-cov                  # pytest without coverage
pytest tests/test_x.py::test_name # single test
podman build -t vaimennuskorjain .   # or docker build
```

The `tests/` directory currently contains no tests beyond the package marker.

## Architecture

Two source trees under [src/](src/), only the first is packaged:

- [src/vaimennuskorjain/](src/vaimennuskorjain/) — the library ([\_\_init\_\_.py](src/vaimennuskorjain/__init__.py))
  plus a thin Click wrapper ([cli.py](src/vaimennuskorjain/cli.py)).
- [src/scripts/](src/scripts/) — throwaway development/visualization scripts run directly
  (`python src/scripts/foo.py`). They contain hardcoded `~/data/...` paths and commented-out
  alternatives, and some have drifted out of sync with the library API (e.g.
  [accum.py](src/scripts/accum.py) calls `correct_attenuation_zphi(fname)` with a filename and
  expects a return value, which no longer matches the signature). Do not treat them as
  specifications for library behaviour.

### Processing pipeline

`correct_attenuation_zphi()` mutates the `Radar` object in place; nothing returns a new radar.
Order matters:

1. `phidp_base0()` subtracts the PHIDP baseline offset, masks negative values and
   non-meteorological gates (`rhohv < 0.9`), and stores `PHIDPA`. The baseline comes from the
   ODIM file (`read_odim_phidp_base`); estimating it from the data is a noisy fallback that warns.
2. `pyart.correct.calculate_attenuation_zphi` runs on `PHIDPA` with band coefficients pulled from
   Py-ART's private `_param_attzphi_table()`, producing `DBZHA`, `PIA`, `SPEC`, `PIDA`, `ZDRA`,
   `SPECD`.
3. `smoothen_attn_cor()` is called twice — once for reflectivity, once for ZDR. It Savitzky-Golay
   smooths the PIA field **along the azimuth axis** (`axis=0`) and re-adds it to the *uncorrected*
   source field, giving `PIAS`/`DBZHAS` and `PIDAS`/`ZDRAS`.
4. `attn_quality_field()` (CLI: field `AQ`) is optional and must run after step 3, since it
   compares azimuthal smoothness of `DBZH` against `DBZHAS`.

### Conventions that matter

- **ODIM field names, not Py-ART canonical names.** `read_h5(..., file_field_names=True)` keeps
  `DBZH`, `ZDR`, `PHIDP`, `RHOHV`, so every call into Py-ART must pass explicit `*_field=` names.
  Py-ART's default field names will not resolve here.
- **`ATTN_FIELDS` is the single source of truth** for the set of output fields: it drives the CLI's
  `-f/--field` choices, the generated help text (via `radproc.cli.gen_help`), and documents each
  field. A new output field must be registered there or it cannot be selected or written.
- **Melting layer and PHIDP baseline are read from HDF5 attributes** (`how/freeze` and the PHIDP
  offset) in the CLI, not inside the library — the library takes them as optional arguments.
  `--ml` overrides the file value.
- `-o/--output-file` supports `{timestamp}` and `{site}` substitution; `site` comes from the ODIM
  `source` string's `NOD` component.
- `--orig` (default on) prepends the input file's existing fields to the write list, so output
  contains both original and corrected data.

### Dependencies and versioning

- [radproc](https://github.com/fmidev/radproc) (installed as a direct git reference with the `mch`
  extra) supplies all radar I/O and gate filtering: `read_h5`/`write_h5`, `read_odim_ml`,
  `read_odim_phidp_base`, `nonmet_filter`, `filter_field`, `gen_help`. Prefer reusing these over
  reimplementing HDF5 or masking logic. When behaviour looks wrong, check radproc's source — it is
  a moving upstream, not a stable API.
- Version comes from git tags via `hatch-vcs`; `src/vaimennuskorjain/_version.py` is generated and
  gitignored. Never edit or commit it.
- The Docker image is a two-stage build ending in `python:3-slim` with `PYART_QUIET=1` and the CLI
  as entrypoint; images are published to quay.io/fmi.
