# MobiSurvStd is now Nemobi

**This package is deprecated.** MobiSurvStd has been renamed to
[**Nemobi**](https://github.com/LucasJavaudin/Nemobi) (*Normalisation des enquêtes mobilités*).

```bash
pip uninstall mobisurvstd
pip install nemobi
```

Then replace `import mobisurvstd` with `import nemobi` and the `mobisurvstd` command with `nemobi`.
Everything else (functions, CLI options, standardized format) is unchanged.

This last `mobisurvstd` release is a thin wrapper that installs `nemobi` and forwards all imports
and CLI calls to it, with a deprecation warning.
Older `mobisurvstd` versions (≤ 1.6.1) remain available on PyPI.

- Migration guide: <https://nemobi.lucasjavaudin.com/migration.html>
- Documentation: <https://nemobi.lucasjavaudin.com/>
- PyPI: <https://pypi.org/project/nemobi/>
