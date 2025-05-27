# Motorcycles

Sort order: `motorcycle_id`

## Indexing

### `motorcycle_id`

Unique identifier of the motorcycle.

- **Type:** UInt32
- **Guarantees:**
  - Values range from 1 to the number of motorcycles.

### `household_id`

Identifier of the household which owns that motorcycle.

- **Type:** UInt32
- **Guarantees:**
  - There exists a household with this `household_id`.
  - The value is not null.

### `motorcycle_index`

Index of the motorcycle among the household's motorcycles.

- **Type:** UInt8
- **Guarantees:**
  - Values are unique *within a household* and range from 1 to the number of motorcycles (whose
    characteristics are known) for that household.
  - The value is not null.

### `original_motorcycle_id`

Identifier of the motorcycle in the original data.

- **Type:** Struct whose fields depend on the survey

## Characteristics

### `type`

Type of motorcycle.

- **Modalities:**
  - `"moped"`: small-size motorcycle, usually with limited speed ("cyclomoteur")
  - `"scooter"`
  - `"motorbike"`: large-size motorcycle ("moto")
  - `"motorized_tricycle"`: large-size motorcycle with three wheels ("3-roues motorisé")
  - `"other"`: other type of motorcycle

### `fuel_type`

Fuel type that the motorcycle is using.

- **Modalities:**
  - `"thermic"`
  - `"electric"`
  - `"other"`

### `year`

Year during which the motorcycle was used for the first time.

- **Type:** UInt16
- **Guarantees:**
  - The value is not earlier than 1900.
  - The value is not in the future.

## Thermic characteristics

### `thermic_engine_type`

Type of engine for the thermic motorcycle.

- **Modalities:**
  - `"two_stroke"`: "deux temps"
  - `"four_stroke"`: "quatre temps"
- **Guarantees:**
  - If `fuel_type` is not `"thermic"`, then the value is null.

### `cm3_lower_bound`

Lower bound for the cubic capacity ("cylindrée") of the motorcycle in cm³ (for thermic motorcycles).

- **Type:** UInt16
- **Guarantees:**
  - If `fuel_type` is not `"thermic"`, then the value is null.

### `cm3_upper_bound`

Upper bound for the cubic capacity ("cylindrée") of the motorcycle in cm³ (for thermic motorcycles).

- **Type:** UInt16
- **Guarantees:**
  - If `fuel_type` is not `"thermic"`, then the value is null.
  - The value is not smaller than `cm3_lower_bound`.

## Electric characteristics

### `kw_lower_bound`

Lower bound for the energy power of the motorcycle in kilowatts (for electric motorcycles).

- **Type:** UInt16
- **Guarantees:**
  - If `fuel_type` is not `"electric"`, then the value is null.

### `kw_upper_bound`

Upper bound for the energy power of the motorcycle in kilowatts (for electric motorcycles).

- **Type:** UInt16
- **Guarantees:**
  - If `fuel_type` is not `"electric"`, then the value is null.
  - The value is not smaller than `kw_lower_bound`.

## Usage

### `annual_mileage`

Estimated annual mileage of the motorcycle, in kilometers.

Note that, depending on the survey and the respondent, the value might not be very accurate.

- **Type:** UInt32

### `annual_mileage_lower_bound`

Lower bound for the estimated annual mileage of the motorcycle, in kilometers.

- **Type:** UInt32
- **Guarantees:**
  - The value is not larger than `annual_mileage`.

### `annual_mileage_upper_bound`

Upper bound for the estimated annual mileage of the motorcycle, in kilometers.

- **Type:** UInt32
- **Guarantees:**
  - The value is not small than `annual_mileage_lower_bound`.
  - The value is not larger than `annual_mileage`.

## Parking

### `parking_location`

Type of location usually used to park the motorcycle overnight.

- **Modalities:**
  - `"garage"`: the motorcycle is parked in a private garage
  - `"street"`: the motorcycle is parked in the street
  - `"parking_lot"`: the motorcycle is park in a parking lot
  - `"other"`: other parking location

### `parking_type`

Type of parking (paid or free) usually used to park the motorcycle overnight.

- **Modalities:**
  - `"forbidden"`: the motorcycle is parked in a forbidden location
  - `"free"`: the motorcycle is parked in a free location
  - `"paid"`: the motorcycle is parked in a paid location, the person paies
  - `"paid_by_other"`: the motorcycle is parked in a paid location, someone else paies
  - `"other"`: other types
- **Guarantees:**
  - If `parking_location` is null, then the value is null.
