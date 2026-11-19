# Migrating from MobiSurvStd

Nemobi (*Normalisation des enquêtes mobilités*) is the new name of **MobiSurvStd**.
The rename happened with version 2.0.0; versions 1.x were published as `mobisurvstd`.
Apart from the name, the code, the standardized format and the supported surveys are unchanged.

## Installation

```bash
pip uninstall mobisurvstd
pip install nemobi
```

The latest release of `mobisurvstd` on PyPI is a thin compatibility package that installs `nemobi`
and emits a deprecation warning: it keeps old code working, but you should switch to `nemobi`.

## Command line

Replace the `mobisurvstd` command with `nemobi`:

```bash
# Before
mobisurvstd my_survey.zip output_dir
# After
nemobi my_survey.zip output_dir
```

All options are unchanged.

## Python API

Replace `mobisurvstd` with `nemobi` in your imports:

```python
# Before
import mobisurvstd
from mobisurvstd import SurveyDataReader

# After
import nemobi
from nemobi import SurveyDataReader
```

All functions keep the same names and arguments (`standardize`, `bulk_standardize`,
`SurveyDataReader`, `read_many`, `setup`).

## Existing standardized surveys

Surveys standardized with MobiSurvStd do not need to be standardized again: the format is the
same, so `nemobi.SurveyDataReader` and `nemobi.read_many` can read them directly.

## Cache

The downloaded IGN and INSEE data is now cached in a `nemobi` cache directory.
The first time Nemobi runs, it moves the existing MobiSurvStd cache there (if any), so the data
does not need to be downloaded again.

## Links

- Documentation: <https://nemobi.lucasjavaudin.com/> (formerly
  `https://mobisurvstd.github.io/MobiSurvStd/`)
- Repository: <https://github.com/LucasJavaudin/Nemobi> (formerly
  `https://github.com/MobiSurvStd/MobiSurvStd`)
- PyPI: <https://pypi.org/project/nemobi/> (formerly <https://pypi.org/project/mobisurvstd/>)
