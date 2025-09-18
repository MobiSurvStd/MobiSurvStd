This directory contains several examples of Python scripts to analyze multiple surveys
simultaneously.
All scripts assume that the standardized surveys are stored in the `output/all/` directory.

- `bicycle_shares.py`: Compute the share of bicycle trips by survey; plot that share as a function
  of the survey date.
- `bicycle_shares_by_insee.py`: Compute the share of bicycle trips by INSEE municipality, over all
  surveys; plot a map of that shares.
- `commuting_time.py`: For each socioprofessional category, compute the average commuting time by
  survey and plot the values as a function of the survey date.
- `households_by_insee_map.py`: Compute the number of surveyed household by INSEE municipality, over
  all surveys; plot a map of the values.
- `mode_shares.py`: Compute the mode shares for each survey; plot those shares as horizontal bars.
- `null_counts.py`: Compute the share of null values for each variable and each survey; generate the
  HTML tables used in the [documentation](https://mobisurvstd.github.io/MobiSurvStd/table.html).
- `persons_in_vehicle.py`: Compute the shares of car commuting trips according to the number of
  persons in the car.
