# Changelog

## [Unreleased]

- Add typing-extensions as an explicit dependency #8
- Fixes for EGT 2010 and 2020 with recent polars versions #9

## [1.2.1] - 2026-05-22

- Minor fixes for spatial data in the new EMC² surveys.

## [1.2.0] - 2026-05-21

- Various fixes to support four new EMC² surveys (Clermont-Ferrand 2023, Toulouse 2023, Nice 2023,
  and Strasbourg 2024).
- Update `py7zr` to `1.1.0`.

## [1.1.0] - 2026-04-01

- EMG 2023 is now supported (@sebhoerl).
- EGT18-20 v3 is now supported.
- New urban unit columns: `*_insee_urban_type`, `*_urban_unit`, and `*_urban_unit_name` for `home`,
  `origin`, and `destination`.
- New script to plot activity schedules of a household: `analysis/plot_household_schedule.py`.
- New command-line option `--skip-spatial` to skip downloading INSEE data.
- Show progress bars when downloading INSEE or IGN data (@sebhoerl).
- Add MobiSurvStd logos.
- Update INSEE data for 2026.
- Add ruff configuration to `pyproject.toml`.

[unreleased]: https://github.com/Metropolis2/Metropolis-Core/compare/1.2.1...HEAD
[1.2.1]: https://github.com/MobiSurvStd/MobiSurvStd/releases/tag/1.2.1
[1.2.0]: https://github.com/MobiSurvStd/MobiSurvStd/releases/tag/1.2.0
[1.1.0]: https://github.com/MobiSurvStd/MobiSurvStd/releases/tag/1.1.0
