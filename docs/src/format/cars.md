# Cars

Sort order: `car_id`

## Indexing

### `car_id`

Unique identifier of the car.

- **Type:** UInt32
- **Guarantees:**
  - Values range from 1 to the number of cars.

### `household_id`

Identifier of the household which owns that car.

- **Type:** UInt32
- **Guarantees:**
  - There exists a household with this `household_id`.
  - The value is not null.

### `car_index`

Index of the car among the household's cars.

- **Type:** UInt8
- **Guarantees:**
  - Values are unique *within a household* and range from 1 to the number of cars (whose
    characteristics are known) for that household.
  - The value is not null.

### `original_car_id`

Identifier of the car in the original data.

- **Type:** Struct whose fields depend on the survey

## Characteristics

### `type`

Type of car / vehicle.

- **Modalities:**
  - `"passenger_car"`: a standard car ("véhicule de tourisme")
  - `"recreational_car"`: "camping-car" and similar
  - `"utility_car"`: "véhicule utilitaire" (usually defined as having a payload larger than 800kg)
  - `"license_free_car"`: a car that does not require a driving license to be driven

### `fuel_type`

Fuel type that the car is using.

- **Modalities:**
  - `"thermic:petrol"`: "essence" ("sans plomb" or "super")
  - `"thermic:diesel"`: "diesel"
  - `"thermic:gas"`: "gaz"
  - `"electric"`: "électrique"
  - `"hybrid:regular"`: "hybride non-rechargeable" (unspecified engine type)
  - `"hybrid:regular:petrol"`: "hybride non-rechargeable" (petrol engine)
  - `"hybrid:regular:diesel"`: "hybride non-rechargeable" (diesel engine)
  - `"hybrid:plug-in"`: "hybride rechargeable"
  - `"hybrid:unspecified"`: "hybride" (without additional details)
  - `"other"`

### `fuel_type_group`

Fuel type of the car in general groups.

- **Modalities:**
  - `"thermic"`
  - `"electric"`
  - `"hybrid"`: hybrid car (regular or plug-in)
  - `"other"`
- **Guarantees:**
  - The value is consistent with `fuel_type`.

### `year`

Year during which the car was used for the first time.

- **Type:** UInt16
- **Guarantees:**
  - The value is not earlier than 1900.
  - The value is not in the future.

### `tax_horsepower`

Tax horsepower of the car ("cheval fiscale CV").

- **Type:** UInt16

### `critair`

[Crit'Air vignette](https://en.wikipedia.org/wiki/Crit%27air) of the car.

- **Modalities:**
  - `"E"`: Vignette Crit'Air E
  - `"1"`: Vignette Crit'Air 1
  - `"2"`: Vignette Crit'Air 2
  - `"3"`: Vignette Crit'Air 3
  - `"4"`: Vignette Crit'Air 4
  - `"5"`: Vignette Crit'Air 5
  - `"N"`: Unclassified vehicle
- **Guarantees:**
  - The vignette Crit'Air is compatible with the fuel type and age of the vehicle.

## Usage

### `total_mileage`

Total mileage of the car, in kilometers.

Note that, depending on the survey and the respondent, the value might not be very accurate.

- **Type:** UInt32

### `total_mileage_lower_bound`

Lower bound for the total mileage of the car, in kilometers.

- **Type:** UInt32
- **Guarantees:**
  - The value is not larger than `total_mileage`.

### `total_mileage_upper_bound`

Upper bound for the total mileage of the car, in kilometers.

- **Type:** UInt32
- **Guarantees:**
  - The value is not small than `total_mileage_lower_bound`.
  - The value is not larger than `total_mileage`.

### `annual_mileage`

Estimated annual mileage of the car, in kilometers.

Note that, depending on the survey and the respondent, the value might not be very accurate.

- **Type:** UInt32

### `annual_mileage_lower_bound`

Lower bound for the estimated annual mileage of the car, in kilometers.

- **Type:** UInt32
- **Guarantees:**
  - The value is not larger than `annual_mileage`.

### `annual_mileage_upper_bound`

Upper bound for the estimated annual mileage of the car, in kilometers.

- **Type:** UInt32
- **Guarantees:**
  - The value is not small than `annual_mileage_lower_bound`.
  - The value is not larger than `annual_mileage`.

## Ownership

### `ownership`

Type of ownership for the car.

- **Modalities:**
  - `"personal"`: the car is owned by the household
  - `"employer:full_availability"`: the car is owned by an employer of a household member and is
    made available for unlimited used ("voiture de fonction")
  - `"employer:limited_availability"`: the car is owned by an employer of a household member and is
    made available for limited used ("voiture de service")
  - `"shared"`: the car is shared between multiple households
  - `"leasing"`: the car is rented by the household over a long period of time
  - `"other"`: other type of ownership

## Parking

### `parking_location`

Type of location usually used to park the car overnight.

- **Modalities:**
  - `"garage"`: the car is parked in a private garage
  - `"street"`: the car is parked in the street
  - `"parking_lot"`: the car is park in a parking lot
  - `"other"`: other parking location

### `parking_type`

Type of parking (paid or free) usually used to park the car overnight.

- **Modalities:**
  - `"forbidden"`: the car is parked in a forbidden location
  - `"free"`: the car is parked in a free location
  - `"paid"`: the car is parked in a paid location, the person paies
  - `"paid_by_other"`: the car is parked in a paid location, someone else paies
  - `"other"`: other types
- **Guarantees:**
  - If `parking_location` is null, then the value is null.
