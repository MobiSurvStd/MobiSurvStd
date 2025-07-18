# Households

Sort order: `household_id`

## Indexing

### `household_id`

Unique identifier of the household.

- **Type:** UInt32
- **Guarantees:**
  - Values range from 1 to the number of households.

### `original_household_id`

Identifier of the household in the original data.

- **Type:** Struct whose fields depend on the survey

## Surveying

### `survey_method`

Method that was used to survey the household.

- **Modalities:**
  - `"face_to_face"`: the household was surveyed during a face-to-face meeting
  - `"phone"`: the household was surveyed on the phone
- **Guarantees:**
  - Values are either all null (undefined survey method) or all defined.

### `interview_date`

Date at which the interview took place.

Note that this is not the date at which the reported trips (if any) took place.
See TODO.

- **Type:** Date

### `sample_weight`

Sample weight of the household.

The sum of the values is supposed to be approximately equal to the number of households in the
survey area.

- **Type:** Float64
- **Guarantees:**
  - Values are either all null (undefined survey method) or all defined.
  - The value is non-negative.

## Home location

### `home_lng`

Longitude of home coordinates.

The accuracy depends on the survey type.
For EGT surveys, the coordinates are guaranteed to be within 100 meters of the actual location.
For other surveys, the coordinates represent the centroid of `home_detailed_zone` (or the exact
coordinates defined by `home_special_location` when it is non-null).

- **Type:** Float64

### `home_lat`

Latitude of home coordinates.

See [`home_lng`](#home_lng) for details on the accuracy of the value.

- **Type:** Float64

### `home_special_location`

Identifier of the special location where the household is located.

- **Type:** String
- **Guarantees:**
  - The home special location intersects with the home detailed zone, draw zone, and INSEE zone
    (only checked if the locations and zones are known).

### `home_detailed_zone`

Identifier of the detailed zone where the household is located.

- **Type:** String
- **Guarantees:**
  - Values are either all null or all defined.
  - If `detailed_zones.parquet` exists, then the value is a valid `detailed_zone_id`.
  - The home detailed zone intersects with the home draw zone and INSEE zone (only checked if the
    zones are known).

### `home_draw_zone`

Identifier of the draw zone where the household is located.

- **Type:** String
- **Guarantees:**
  - Values are either all null or all defined.
  - If `draw_zones.parquet` exists, then the value is a valid `draw_zone_id`.
  - The home draw zone intersects with the home INSEE zone (only checked if the zones are known).

### `home_insee`

INSEE code of the municipality where the household is located.

- **Type:** String
- **Guarantees:**
  - Values are either all null or all defined.
  - String is a [valid INSEE code](TODO).

### `home_insee_name`

Name of the municipality where the household is located.

- **Type:** String

### `home_dep`

_Département_ code of the household home.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `home_insee` is not null, then the value is equal to the _département_ of the home INSEE
    municipality.

### `home_dep_name`

Name of the _département_ of the household home.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `home_dep`.

### `home_nuts2`

NUTS 2 code of the household home.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `home_dep` is not null, then the value is equal to the NUTS 2 code corresponding to the home
    _département_.

### `home_nuts2_name`

Name of the NUTS 2 region of the household home.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `home_nuts2`.

### `home_nuts1`

NUTS 1 code of the household home.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `home_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to the
    home NUTS 2.

### `home_nuts1_name`

Name of the NUTS 1 region of the household home.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `home_nuts1`.

## Household characteristics

### `household_type`

Type of household structure.

- **Modalities:**
  - `"single:man"`: household with only one man
  - `"single:woman"`: household with only one woman
  - `"couple:no_child"`: couple with no child
  - `"couple:children"`: couple with at least one child
  - `"singleparent:father"`: singleparent family (man and at least one child)
  - `"singleparent:mother"`: singleparent family (woman and at least one child)
  - `"other"`: other type of household structure
- **Guarantees:**
  - The value is compatible with the actual household structure (`nb_persons`,
    `reference_person_link`, etc.).

### `income_lower_bound`

Lower bound for the net income of the household, in euros.

- **Type:** UInt16

### `income_upper_bound`

Upper bound for the net income of the household, in euros.

- **Type:** UInt16
- **Guarantees:**
  - The value is not smaller than `income_lower_bound`.

## Housing

### `housing_type`

Type of the housing the household is living in.

- **Modalities:**
  - `"house"`: an individual house
  - `"apartment"`: an apartment in a collective building
  - `"other"`: an other type of housing

### `housing_status`

Type of ownership / renting for the housing.

- **Modalities:**
  - `"owner:ongoing_loan"`: the household is owning the housing and is paying loans ("accédant à la
    propriété")
  - `"owner:fully_repaid"`: the household is owning the housing and is not paying loans
  - `"owner:usufructuary"`: the household is usufructuary of the housing ("usufruitier")
  - `"owner:unspecified"`: the household is owning the housing (without more specification)
  - `"tenant:public_housing"`: the household is a tenant inside a public housing
  - `"tenant:private"`: the household is a tenant inside a private-owned housing
  - `"tenant:unspecified"`: the household is a tenant (without more specification)
  - `"rent_free"`: the household is hosted for free
  - `"university_resident"`: the household is living inside a university residence
  - `"other"`: other type of ownership / renting

### `has_internet`

Whether the household has internet access at home.

- **Type:** Boolean

## Motorized vehicles

### `nb_cars`

Number of cars owned by the household.

- **Type:** UInt8
- **Guarantees:**
  - The number of cars for this household in `cars.parquet` is not larger than this value (but
    it can be smaller if the car details are not known for all cars).

### `nb_motorcycles`

Number of motorcycles owned by the household.

- **Type:** UInt8
- **Guarantees:**
  - The number of motorcycles for this household in `motorcycles.parquet` is not larger than this
    value (but it can be smaller if the motorcycles details are not known for all motorcycles).

## Bicycles

### `nb_bicycles`

Number of bicycles (standard or electric) owned by the household.

- **Type:** UInt8
- **Guarantees:**
  - When `nb_standard_bicycles` and `nb_electric_bicycles` are specified, then we always have
    `nb_bicycles = nb_standard_bicycles + nb_electric_bicycles`.

### `nb_standard_bicycles`

Number of standard bicycles (i.e., non-electric) owned by the household.

- **Type:** UInt8

### `nb_electric_bicycles`

Number of electric bicycles owned by the household.

- **Type:** UInt8

### `has_bicycle_parking`

Whether the household can park bicycles at home.

- **Type:** Boolean

## Counts

### `nb_persons`

Number of persons belonging to the household.

Note that persons below 5 year old are sometimes excluded from the surveys.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null.
  - The value is positive.
  - The value is equal to the number of persons in `persons.parquet` who belong to this household.

### `nb_persons_5plus`

Number of persons in the household whose age is 6 or more.

- **Type:** UInt8
- **Guarantees:**
  - The value is not smaller than the number of persons in this household whose age is 6 or more.
  - The value is not larger than the number of persons in this household whose age is unknown or 6
    or more.

### `nb_majors`

Number of persons in the household whose age is 18 or more.

- **Type:** UInt8
- **Guarantees:**
  - The value is not smaller than the number of persons in this household whose age is 18 or more.
  - The value is not larger than the number of persons in this household whose age is unknown or 18
    or more.

### `nb_minors`

Number of persons in the household whose age is 17 or less.

- **Type:** UInt8
- **Guarantees:**
  - The value is not smaller than the number of persons in this household whose age is 17 or less.
  - The value is not larger than the number of persons in this household whose age is unknown or 17
    or less.
