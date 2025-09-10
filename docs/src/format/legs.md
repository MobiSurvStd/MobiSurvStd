# Legs

Sort order: `leg_id`

## Indexing

### `leg_id`

Unique identifier of the leg.

- **Type:** UInt32
- **Guarantees:**
  - Values range from 1 to the number of legs.

### `trip_id`

Identifier of the trip the leg is a part of.

- **Type:** UInt32
- **Guarantees:**
  - There exists a trip with this `trip_id`.
  - The value is not null.

### `person_id`

Identifier of the person that performed the leg.

- **Type:** UInt32
- **Guarantees:**
  - The value is not null.
  - The value is equal to the `person_id` value of the trip with id `trip_id`.

### `household_id`

Identifier of the household of the person that performed the leg.

- **Type:** UInt32
- **Guarantees:**
  - The value is not null.
  - The value is equal to the `household_id` value of the person with id `person_id`.

### `leg_index`

Index of the leg among the trip's legs.

Legs with smaller index are performed first.

- **Type:** UInt8
- **Guarantees:**
  - Values are unique *within a trip* and range from 1 to the number of legs in that trip.
  - The value is not null.

### `first_leg`

Whether the leg is the first one of the trip.

- **Type:** Boolean
- **Guarantees:**
  - The value is not null.
  - The value is `true` if and only if `leg_index` is 1.

### `last_leg`

Whether the leg is the last one of the trip.

- **Type:** Boolean
- **Guarantees:**
  - The value is not null.
  - The value is `true` if and only if `leg_index` is equal to the number of legs in the trip.

### `original_leg_id`

Identifier of the leg in the original data.

- **Type:** Struct whose fields depend on the survey

## Transportation mode

### `mode`

Mode of transportation used to perform the leg.

- **Modalities:**
  - Same modalities as [trip's `main_mode`](trips.md#main_mode).

### `mode_group`

Mode group of the mode of transportation used to perform the leg.

- **Modalities:**
  - `"walking"`: walking, excluding wheelchair and personal transporter
  - `"bicycle"`: bicycle (traditional or electric, driver or passenger, personal or shared)
  - `"motorcycle"`: motorcycle (small and large, driver or passenger)
  - `"car_driver"`: car as a driver
  - `"car_passenger"`: car as a passenger (including taxi and VTC)
  - `"public_transit"`: any form of public transit (excluding employer transport)
  - `"other"`: all other modes
- **Guarantees:**
  - The values are consistent with `mode`.

### `public_transit_line`

Local name of the public-transit line taken, for public-transit legs.

The way public-transit lines' names are defined depends on the survey type.

- **Type:** String
- **Modalities:**
  - If `mode_group` is not `"public_transit"`, then the value is null.

## Start location

### `start_lng`

Longitude of the leg's start point.

The accuracy depends on the survey type.
For EGT surveys, the coordinates are guaranteed to be within 100 meters of the actual location.
For other surveys, the coordinates represent the centroid of `start_detailed_zone` (or the exact
coordinates defined by `start_special_location` when it is non-null).

- **Type:** Float64

### `start_lat`

Latitude of the leg's start point.

See [`start_lng`](#start_lng) for details on the accuracy of the value.

- **Type:** Float64

### `start_special_location`

Identifier of the special location corresponding to the leg start point.

- **Type:** String
- **Guarantees:**
  - The start special location intersects with the start detailed zone, draw zone, and INSEE zone
    (only checked if the zones are known).

### `start_detailed_zone`

Identifier of the detailed zone corresponding to the leg start point.

- **Type:** String
- **Guarantees:**
  - The start detailed zone intersects with the start draw zone and INSEE zone (only checked if the
    zones are known).

### `start_draw_zone`

Identifier of the draw zone corresponding to the leg start point.

- **Type:** String
- **Guarantees:**
  - The start detailed zone intersects with the start draw zone and INSEE zone (only checked if the
    zones are known).

### `start_insee`

INSEE code of the municipality corresponding to the leg start point.

- **Type:** String
- **Guarantees:**
  - String is a [valid INSEE code](TODO).

### `start_insee_name`

Name of the municipality corresponding to the leg start point.

- **Type:** String

### `start_dep`

_Département_ code of the leg start point.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `start_insee` is not null, then the value is equal to the _département_ of the start point INSEE
    municipality.

### `start_dep_name`

Name of the _département_ of the leg start point.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `start_dep`.

### `start_nuts2`

NUTS 2 code of the leg start point.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `start_dep` is not null, then the value is equal to the NUTS 2 code corresponding to the
    start point _département_.

### `start_nuts2_name`

Name of the NUTS 2 region of the leg start point.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `start_nuts2`.

### `start_nuts1`

NUTS 1 code of the leg start point.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `start_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to the
    start point NUTS 2.

### `start_nuts1_name`

Name of the NUTS 1 region of the leg start point.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `start_nuts1`.

## End location

### `end_lng`

Longitude of the leg's end point.

See [`start_lng`](#start_lng) for details on the accuracy of the value.

- **Type:** Float64

### `end_lat`

Latitude of the leg's end point.

See [`start_lng`](#start_lng) for details on the accuracy of the value.

- **Type:** Float64

### `end_special_location`

Identifier of the special location corresponding to the leg end point.

Note that in most cases, the end special location should be equal to the start special location of
the next leg in the trip (if any).
Exceptions can occur when two special locations are so closed that the person walked very quickly
from one to the other and did not report that as a dedicate leg.
MobiSurvStd will show warning messages indicating how many legs does not match the constraint.

- **Type:** String
- **Guarantees:**
  - The end special location intersects with the end detailed zone, draw zone, and INSEE zone
    (only checked if the zones are known).

### `end_detailed_zone`

Identifier of the detailed zone corresponding to the leg end point.

- **Type:** String
- **Guarantees:**
  - The end detailed zone intersects with the end draw zone and INSEE zone (only checked if the
    zones are known).
  - The value is equal to the `start_detailed_zone` of the next leg (if any).

### `end_draw_zone`

Identifier of the draw zone corresponding to the leg end point.

- **Type:** String
- **Guarantees:**
  - The end detailed zone intersects with the end draw zone and INSEE zone (only checked if the
    zones are known).
  - The value is equal to the `start_draw_zone` of the next leg (if any).

### `end_insee`

INSEE code of the municipality corresponding to the leg end point.

- **Type:** String
- **Guarantees:**
  - String is a [valid INSEE code](TODO).
  - The value is equal to the `start_insee` of the next leg (if any).

### `end_insee_name`

Name of the municipality corresponding to the leg end point.

- **Type:** String

### `end_dep`

_Département_ code of the leg end point.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `end_insee` is not null, then the value is equal to the _département_ of the end point INSEE
    municipality.

### `end_dep_name`

Name of the _département_ of the leg end point.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `end_dep`.

### `end_nuts2`

NUTS 2 code of the leg end point.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `end_dep` is not null, then the value is equal to the NUTS 2 code corresponding to the
    end point _département_.

### `end_nuts2_name`

Name of the NUTS 2 region of the leg end point.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `end_nuts2`.

### `end_nuts1`

NUTS 1 code of the leg end point.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `end_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to the
    end point NUTS 2.

### `end_nuts1_name`

Name of the NUTS 1 region of the leg end point.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `end_nuts1`.

## Time and distance

### `leg_travel_time`

Travel time spent for this leg, in minutes.

Usually, one can expect that the sum of `leg_travel_time` for all the legs of a trip is not larger
than the `travel_time` value of the trip.
In parctice, that constraint is not always satisfied due to miss-recorded travel times.
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Type:** UInt32
- **Guarantees:**
  - The value is positive.
  - The sum of `leg_travel_time` for the legs of a trip is not larger than the `travel_time` value
    of the trip.

### `leg_euclidean_distance_km`

Euclidean distance between the leg's start and stop points, in kilometers.

- **Type:** Float64
- **Guarantees:**
  - All values are non-negative.

### `leg_travel_distance_km`

Travel distance of the leg, in kilometers.

This is usually a distance on the road network.
The details regardings how this value is computed depends on the surveys.

- **Type:** Float64
- **Guarantees:**
  - All values are non-negative.
  - The value is not small than `leg_euclidean_distance_km`.
## Car

### `car_type`

Type of car used for the leg.

- **Modalities:**
  - `"household"`: the car used for the leg is a car owned by the household, whose
    characteristics are reported in `cars.parquet`
  - `"other_household"`: the car used for the leg is a car owned by the household, whose
    characteristics have not been reported.
  - `"rental"`: the car used for the leg is a rental car ("véhicule de location")
  - `"company"`: the car used for the leg is a car lended by the person's employer
  - `"shared"`: the car used for the leg is a car from a car-sharing service
  - `"other"`: other cases
- **Guarantees:**
  - If `mode` is not `car:driver` or `car:passenger`, then the value is null.
  - If the value is `"other_household"`, then the household must have at least one car whose
    characteristics are unknown (i.e., household variable `nb_cars` is larger than the number of
    cars with reported characteristics).

### `car_id`

Identifier of the car used to perform the leg.

- **Type:** UInt32
- **Guarantees:**
  - The value is non-null *if and only if* `car_type` is `"household"`.
  - There is a car with the corresponding identifier in `cars.parquet`.
  - The corresponding car is owned by the household of the person who performed the leg.

### `nolicense_car`

Whether the car used for the leg was a no-license car ("voiture sans permis").

- **Type:** Boolean
- **Guarantees:**
  - If `mode` is not `car:driver`, then the value is null.

## Motorcycle

### `motorcycle_type`

Type of motorcycle used for the leg.

- **Modalities:**
  - `"household"`: the motorcycle used for the leg is a motorcycle owned by the
    household, whose characteristics are reported in `motorcycles.parquet`
  - `"other_household"`: the motorcycle used for the leg is a motorcycle owned by the
    household, whose characteristics have not been reported.
  - `"rental"`: the motorcycle used for the leg is a rental motorcycle ("moto de
    location")
  - `"company"`: the motorcycle used for the leg is a motorcycle lended by the person's
    employer
  - `"shared"`: the motorcycle used for the leg is a motorcycle from a motorcycle-sharing
    service
  - `"other"`: other cases
- **Guarantees:**
  - If `mode_group` is not `motorcycle`, then the value is null.
  - If the value is `"other_household"`, then the household must have at least one motorcycle whose
    characteristics are unknown (i.e., household variable `nb_motorcycles` is larger than the number
    of motorcycles with reported characteristics).

### `motorcycle_id`

Identifier of the motorcycle used to perform the leg.

- **Type:** UInt32
- **Guarantees:**
  - The value is non-null *if and only if* `motorcycle_type` is `"household"`.
  - There is a motorcycle with the corresponding identifier in `motorcycles.parquet`.
  - The corresponding motorcycle is owned by the household of the person who performed the leg.

## Vehicle Occupancy

### `nb_persons_in_vehicle`

Number of persons that were present in the vehicle used.

- **Type:** UInt8
- **Guarantees:**
  - The value is positive.
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
  - If `mode` is passenger related (`"car:passenger"`, `"motorcycle:passenger"`, etc.), then the
    value is at least 2.

### `nb_majors_in_vehicle`

Number of majors (age ≥ 18) that were present in the vehicle used.

- **Type:** UInt8
- **Guarantees:**
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
  - The value is not larger than `nb_persons_in_vehicle`.
  - If the person is major, then the value is at least 1.

### `nb_minors_in_vehicle`

Number of minors (age < 18) that were present in the vehicle used.

- **Type:** UInt8
- **Guarantees:**
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
  - The value is not larger than `nb_persons_in_vehicle`.
  - If `nb_persons_in_vehicle` and `nb_majors_in_vehicle` are non-null, then the value is
    `nb_persons_in_vehicle - nb_majors_in_vehicle`.
  - If the person is minor, then the value is at least 1.

### `nb_household_members_in_vehicle`

Number of persons in the vehicle used that belong to the person's household.

- **Type:** UInt8
- **Guarantees:**
  - The value is positive.
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
  - The value is not larger than `nb_persons_in_vehicle`.

### `nb_non_household_members_in_vehicle`

Number of persons in the vehicle used that _do not_ belong to the person's household.

- **Type:** UInt8
- **Guarantees:**
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
  - The value is not larger than `nb_persons_in_vehicle`.
  - If `nb_persons_in_vehicle` and `nb_household_members_in_vehicle` are non-null, then the value is
    `nb_persons_in_vehicle - nb_household_members_in_vehicle`.

### `in_vehicle_person_ids`

Identifiers of the person that were present in the vehicle for this leg.

- **Type:** List of UInt32
- **Guarantees:**
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
  - The list includes the id of the current person.
  - The number of elements in the list is equal to `nb_household_members_in_vehicle`.
  - All values are valid ids of persons belonging to the same household as the current person.

## Parking

### `parking_location`

Location type where the car was parked at the end of the leg.

- **Modalities:**
  - `"stop_only"`: the car was only stopped temporarily and not parked
  - `"garage"`: the car was parked in a private garage
  - `"street"`: the car was parked in the street
  - `"parking_lot"`: the car was park in an parking lot (no further specification)
  - `"parking_lot:unsheltered"`: the car was park in an unsheltered parking lot
  - `"parking_lot:sheltered"`: the car was park in a sheltered parking lot
  - `"P+R"`: the car was park in a Park and Ride (P+R)
  - `"other"`: other parking location
- **Guarantees:**
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.

### `parking_type`

Type of parking (paid or free) used to park the car.

- **Modalities:**
  - `"forbidden"`: the car was parked in a forbidden location
  - `"free"`: the car was parked in a free location
  - `"paid"`: the car was parked in a paid location, the person paid
  - `"paid_by_other"`: the car was parked in a paid location, someone else paid
  - `"other"`: other types
- **Guarantees:**
  - If `parking_location` is `"stop_only"`, null, then the value is null.

### `parking_search_time`

Time spent searching for a parking location, in minutes.

- **Type:** UInt32
- **Guarantees:**
  - If `mode` does not use a personal vehicle (car, motorcycle, bicycle, truck, personal
    transporter), then the value is null.
