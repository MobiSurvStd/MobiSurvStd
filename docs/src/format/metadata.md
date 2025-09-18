# Metadata

Each survey standardized with MobiSurvStd includes a `metadata.json` JSON file with the following
variables.

### `name`

Survey name.

- **Type:** String

### `type`

Survey type

- **Modalities:**
  - `"EMP2019"`
  - `"EMC2"`
  - `"EGT2020"`
  - `"EDVM"`
  - `"EDGT"`
  - `"EGT2010"`
  - `"EMD"`

### `survey_method`

Method used to survey the households.

- **Modalities:**
  - `"face_to_face"`: the households were all surveyed during a face-to-face meeting
  - `"phone"`: the households were all surveyed on the phone
  - `"mixed"`: some households were surveyed during face-to-face meetings, other were surveyed on
    the phone

### `nb_households`

Number of households in the standardized survey data.

- **Type:** Integer

### `nb_cars`

Number of cars in the standardized survey data.

- **Type:** Integer

### `nb_motorcycles`

Number of motorcycles in the standardized survey data.

- **Type:** Integer

### `nb_persons`

Number of persons in the standardized survey data.

- **Type:** Integer

### `nb_trips`

Number of trips in the standardized survey data.

- **Type:** Integer

### `nb_legs`

Number of legs in the standardized survey data.

- **Type:** Integer

### `nb_special_locations`

Number of special locations in the standardized survey data.

- **Type:** Integer

### `nb_detailed_zones`

Number of detailed zones in the standardized survey data.

- **Type:** Integer

### `nb_draw_zones`

Number of draw zones in the standardized survey data.

- **Type:** Integer

### `start_date`

Earliest interview date observed in the survey.

- **Type:** String (`"yyyy-mm-dd"` format)

### `end_date`

Latest interview date observed in the survey.

- **Type:** String (`"yyyy-mm-dd"` format)

### `insee`

INSEE code of the main municipality of the survey.

- **Type:** String
