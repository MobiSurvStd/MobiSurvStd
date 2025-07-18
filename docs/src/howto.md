# User Guide

## Command Line Interface

```bash
python -m mobisurvstd SOURCE OUTPUT_DIRECTORY --survey-type TYPE [--bulk]
```

- `SOURCE` is a path to either a directory or a zipfile where the survey data is stored.
- `OUTPUT_DIRECTORY` is a path to the directory where the standardized survey should be stored.
- `--survey-type TYPE` is the type of the original survey ("emc2", "emp2019", "egt2010", or
  "egt2020"). If omitted, MobiSurvStd will guess the survey type.
- `--bulk` must be used when you want to import all surveys located within the SOURCE directory.

### Examples

#### From directory

Read the EGT2020 survey from the `original_egt2020` directory and store the standardized version in
the `standardized_egt2020` directory.

```bash
python -m mobisurvstd original_egt2020 standardized_egt2020 --survey-type egt2020
```

#### From zipfile

Read the EGT2020 survey from the `original_egt2020.zip` file and store the standardized version in
the `standardized_egt2020` directory.

```bash
python -m mobisurvstd original_egt2020.zip standardized_egt2020 --survey-type egt2020
```

#### Bulk import

Read all surveys in the `my_surveys` directory and store their standardized version in the
`standardized_surveys` directory.

```bash
python -m mobisurvstd my_surveys standardized_surveys --bulk
```

## Usage from Python

### `standardize`

Converts a mobility survey to a clean standardized format.

```python
mobisurvstd.standardize(
    source: str,
    output_directory: str,
    survey_type: str | None = None,
    add_name_subdir: bool = False,
) -> mobisurvstd.classes.SurveyData | None
```

```markdown
Parameters
----------
source
    Path to a directory or zipfile.
    When a directory is given, it must be the top-level directory of the survey to be converted.
    When a zipfile is given, the directories within the zipfile are read recursively so that the
    survey's files can be found no matter how deeply nested the zipfile is.
output_directory
    Path to the directory where the standardized survey should be stored.
    If the directory does not exist, MobiSurvStd will create it (recursively).
survey_type
    String indicating the type of the survey to be converted.
    If the value is omitted, MobiSurvStd will do its best to guess the survey type.
    Possible values: "emc2", "emp2019", "egt2020", "egt2010".
add_name_subdir
    Whether the standardized survey is stored directly in `output_directory` or within a
    subdirectory of `output_directory`.
    If True, the standardized survey is stored in a subdirectory within `output_directory`. The
    subdirectory name is the survey name.
    If False (default), the standardized survey is stored directly in `output_directory`.

Returns
-------
SurveyData
```

**Example:** Read the EGT2020 survey from the `original_egt2020.zip` file and store the
standardized version in the `standardized_egt2020` directory.

```python
import mobisurvstd
mobisurvstd.standardize(
    "original_egt2020.zip",
    "standardized_egt2020",
    survey_type="egt2020",
)
```

### `bulk_standardize`

Standardizes mobility surveys in bulk from a given directory.

MobiSurvStd will explore all directories and zipfiles within `directory`, try to standardize
them and store the standardized data in `output_directory`.

```python
mobisurvstd.bulk_standardize(
    directory: str,
    output_directory: str,
    survey_type: str | None = None,
)
```

```markdown
Parameters
----------
directory
    Path to a directory.
    The directory must contain survey data, stored within directories or zipfiles.
output_directory
    Path to the directory where the standardized surveys should be stored.
    If the directory does not exist, MobiSurvStd will create it (recursively).
    Each survey read is stored in a subdirectory whose name is the survey's name.
survey_type
    String indicating the type of the surveys to be converted.
    If the directory contains surveys of different types, leave this value to None and
    MobiSurvStd will try to guess the type of each survey.
    Possible values: "emc2", "emp2019", "egt2020", "egt2010".
```

**Example:** Read all surveys in the `my_surveys` directory and store their standardized version
in the `standardized_surveys` directory.

```python
import mobisurvstd
mobisurvstd.bulk_standardize("my_surveys", "standardized_surveys")
```

### `SurveyDataReader`

Data structure representing a MobiSurvStd survey.

Create a SurveyDataReader from a directory.

```python
import mobisurvstd
>>> data = mobisurvstd.SurveyDataReader("output/emp2019/")
```

Access the survey's metadata as a dictionary:

```python
>>> data.metadata
{'type': 'EMP2019',
 'survey_method': 'face_to_face',
 'nb_households': 13825,
 'nb_cars': 18817,
 'nb_motorcycles': 1264,
 'nb_persons': 31694,
 'nb_trips': 45169,
 'nb_legs': 46507,
 'nb_special_locations': 0,
 'nb_detailed_zones': 0,
 'nb_draw_zones': 0,
 'nb_insee_zones': 0,
 'start_date': '2018-05-01',
 'end_date': '2019-04-30',
 'insee': None}
```

Access the survey's households as a polars.DataFrame:

```
>>> data.households
┌─────────────┬─────────────┬────────────┬────────────┬───┬────────────┬────────────┬───────────┬───────────┐
│ household_i ┆ original_ho ┆ survey_met ┆ interview_ ┆ … ┆ nb_persons ┆ nb_persons ┆ nb_majors ┆ nb_minors │
│ d           ┆ usehold_id  ┆ hod        ┆ date       ┆   ┆ ---        ┆ _5plus     ┆ ---       ┆ ---       │
│ ---         ┆ ---         ┆ ---        ┆ ---        ┆   ┆ u8         ┆ ---        ┆ u8        ┆ u8        │
│ u32         ┆ struct[1]   ┆ enum       ┆ date       ┆   ┆            ┆ u8         ┆           ┆           │
╞═════════════╪═════════════╪════════════╪════════════╪═══╪════════════╪════════════╪═══════════╪═══════════╡
│ 1           ┆ {"110000011 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
│             ┆ 4000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 2           ┆ {"110000011 ┆ face_to_fa ┆ null       ┆ … ┆ 4          ┆ null       ┆ 3         ┆ 1         │
│             ┆ 5000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 3           ┆ {"110000011 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
│             ┆ 6000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 4           ┆ {"110000012 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
│             ┆ 4000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 5           ┆ {"110000012 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
│             ┆ 5000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ …           ┆ …           ┆ …          ┆ …          ┆ … ┆ …          ┆ …          ┆ …         ┆ …         │
│ 13821       ┆ {"940000036 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
│             ┆ 1000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 13822       ┆ {"940000036 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
│             ┆ 4000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 13823       ┆ {"940000041 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
│             ┆ 5000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 13824       ┆ {"940000044 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
│             ┆ 1000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
│ 13825       ┆ {"940000052 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
│             ┆ 1000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
└─────────────┴─────────────┴────────────┴────────────┴───┴────────────┴────────────┴───────────┴───────────┘
```

### `read_many`

Runs a function on all MobiSurvStd surveys found in a directory and aggregates the results.

```python
mobisurvstd.read_many(
    directory: str,
    read_fn: collections.abc.Callable,
    acc_fn: collections.abc.Callable,
)
```

```markdown
Parameters
----------
directory
    Path to the directory where the MobiSurvStd surveys to read are stored.
    The directory will be read recursively so the surveys can be stored in subdirectories.
read_fn
    Function to be run on each survey.
    It takes a single argument whose type is `SurveyDataReader`.
acc_fn
    Function to aggregate the results from two surveys.
    This must be a function of two arguments, whose type is the same as the return type of
    `read_fn`.
```

**Examples**

Read the total number of households from all surveys in the "output" directory:

```python
import mobisurvstd
mobisurvstd.read_many("output/", lambda d: len(d.households), lambda x, y: x + y)
```

Concatenate all trips in a single DataFrame:

```python
import mobisurvstd
mobisurvstd.read_many("output/", lambda d: d.trips, lambda x, y: pl.concat((x, y)))
```

More complex examples on the use of `read_many` can be found in the `analyses` directory.
