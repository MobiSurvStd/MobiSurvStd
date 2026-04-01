# Changelog

## [Unreleased]

## [1.1.0] - 2026-04-01

- EMG 2023 is now supported (@sebhoerl).
- EGT18-20 v3 is now supported.
- New urban unit columns: `*_insee_urban_type`, `*_urban_unit`, and `*_urban_unit_name` for `home`,
  `origin`, and `destination`.
- New script to plot activity schedules of a household: `analysis/plot_household_schedule.py`.
- New command-line option `--skip-spatial` to skip downloading INSEE data.
- Show progress bars when downloading INSEE or IGN data.
- Add MobiSurvStd logos.
- Update INSEE data for 2026.
- Add ruff configuration to `pyproject.toml`.

[unreleased]: https://github.com/Metropolis2/Metropolis-Core/compare/1.1.0...HEAD
[1.1.0]: https://github.com/MobiSurvStd/MobiSurvStd/releases/tag/1.1.0
