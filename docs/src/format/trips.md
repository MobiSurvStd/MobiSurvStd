# Trips

Sort order: `trip_id`

## Indexing

### `trip_id`

Unique identifier of the trip.

- **Type:** UInt32
- **Guarantees:**
  - Values range from 1 to the number of trips.

### `person_id`

Identifier of the person that performed the trip.

- **Type:** UInt32
- **Guarantees:**
  - There exists a person with this `person_id`.
  - The value is not null.

### `household_id`

Identifier of the household of the person that performed the trip.

- **Type:** UInt32
- **Guarantees:**
  - The value is not null.
  - The value is equal to the `household_id` value of the person with id `person_id`.

### `trip_index`

Index of the trip among the person's trips.

Trips with smaller index are performed first.

- **Type:** UInt8
- **Guarantees:**
  - Values are unique *within a person* and range from 1 to the number of trips performed by that
    person.
  - The value is not null.

### `first_trip`

Whether the trip is the first one of the person.

- **Type:** Boolean
- **Guarantees:**
  - The value is not null.
  - The value is `true` if and only if `trip_index` is 1.

### `last_trip`

Whether the trip is the last one of the person.

- **Type:** Boolean
- **Guarantees:**
  - The value is not null.
  - The value is `true` if and only if `trip_index` is equal to the number of trips for this person.

### `home_sequence_index`

The cumulative number of times that the person has started a trip from their home over the course of
a day.

This variable is designed to identify sequences of trips that begin and end at home ("home-based
tours").

The value starts at 0 and increments by 1 each time a trip begins with
`origin_purpose_group == "home"`.

Examples:

1. Trips:
    `home → work` → `work → home`

    `home_sequence_index`: 1, 1

    (One tour starting and ending at home.)
2. Trips:
    `home → work` → `work → home` → `home → leisure` → `leisure → home`

    `home_sequence_index`: 1, 1, 2, 2

    (Two distinct tours, both home-based.)
3. Trips:
    `work → home` → `home → work`

    `home_sequence_index`: 0, 1

    (The value is 0 if the first trip of the day is not from home.)

- **Type:** UInt8
- **Guarantees:**
  - The value is equal to the cumulative number of times that the trip's origin purpose group is
    `"home"`, over a person's trips.

### `original_trip_id`

Identifier of the trip in the original data.

- **Type:** Struct whose fields depend on the survey

## Purpose

### `origin_purpose`

Purpose of the activity performed at the trip's origin.

- **Modalities:**
  - `"home:main"`: the person is at their usual home location
  - `"home:secondary"`: the person is at a secondary home
  - `"work:usual"`: the person is working at the usual workplace
  - `"work:telework"`: the person is working from home
  - `"work:secondary"`: the person is working at a secondary workplace
  - `"work:business_meal"`: the person is having a meal in a business context
  - `"work:other"`: the person is working at another place
  - `"work:professional_tour"`: the person is doing trips for a professional tour ("tournée
    professionnelle")
  - `"education:childcare"`: the person (child) is at a daycare / nursery school
  - `"education:usual"`: the person is studying at their usual study location
  - `"education:other"`: the person is studying at a different location
  - `"shopping:daily"`: the person is shopping for daily needs (e.g., bread, newspaper)
  - `"shopping:weekly"`: the person is shopping for weekly needs (e.g., groceries)
  - `"shopping:specialized"`: the person is shopping for occasional needs (e.g., bookstore,
    clothing)
  - `"shopping:unspecified"`: the person is shopping for goods without further specification (daily,
    weekly, or specialized)
  - `"shopping:pickup"`: the person is picking up purchases from online shopping ("drive",
    "point relais")
  - `"shopping:no_purchase"`: the person is visiting a store without doing any purchase
  - `"shopping:tour_no_purchase"`: the person is doing a tour of stores with buying anything
  - `"task:healthcare:hospital"`: the person is at a hospital for healthcare reasons
  - `"task:healthcare:doctor"`: the person is at a medical appointment (not in a hospital)
  - `"task:healthcare"`: other healthcare-related activities
  - `"task:procedure"`: the person is doing an administrative procedure or other procedure (apart
    from finding a job)
  - `"task:job_search"`: the person is finding a job
  - `"task:other"`: other task activity
  - `"leisure:sport_or_culture"`: the person is involved in sport, cultural, or associative activity
  - `"leisure:walk_or_driving_lesson"`: the person is doing a walk ("promenade") or taking driving
    lessons
  - `"leisure:lunch_break"`: the person is having lunch before / after work
  - `"leisure:restaurant"`: the person is having diner outside home
  - `"leisure:visiting"`: the person is visiting relatives, friends, or any other person
  - `"leisure:visiting:parents"`: the person is visiting relatives
  - `"leisure:visiting:friends"`: the person is visiting friends
  - `"leisure:other"`: other leisure activity
  - `"escort:activity:drop_off"`: the person is dropping off someone to an activity
  - `"escort:activity:pick_up"`: the person is picking up someone from an activity
  - `"escort:transport:drop_off"`: the person is dropping off someone to a transportation mode
  - `"escort:transport:pick_up"`: the person is picking up someone from a transportation mode
  - `"escort:unspecified:drop_off"`: the person is dropping off someone (either to an activity or
    a transportation mode)
  - `"escort:unspecified:pick_up"`: the person is picking up someone (either from an activity or a
    transportation mode)
  - `"other"`: other purpose not in the list

### `origin_purpose_group`

Purpose group of the activity performed at the trip's origin.

- **Modalities:**
  - `"home"`
  - `"work"`
  - `"education"`
  - `"shopping"`
  - `"task"`
  - `"leisure"`
  - `"escort"`
  - `"other"`
- **Guarantees:**
  - The values are consistent with `origin_purpose`.
  - If `origin_purpose` is not null, then the value is not null.

### `origin_activity_duration`

Duration of the activity performed at the trip's origin, in minutes.

If this is the first trip of the day, the value is null.
Otherwise, the value is equal to the difference between the departure time of this trip and the
arrival time of the previous trip.

- **Type:** UInt16
- **Guarantees:**
  - If `first_trip` is `true`, then the value is null.
  - The value is equal to the difference between `departure_time` for the current trip and
    `arrival_time` for the previous trip.

### `destination_purpose`

Purpose of the activity performed at the trip's destination.

Note that in most cases, the destination purpose should be equal to the origin purpose of the next
trip (if any).
Rare exceptions can occur when someone is moving to a different location while the activity is
performed (e.g., for bus drivers).
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Modalities:**
  - Same modalities as [`origin_purpose`](#origin_purpose).
- **Guarantees:**
  - Same guarantees as [`origin_purpose`](#origin_purpose).

### `destination_purpose_group`

Purpose group of the activity performed at the trip's destination.

- **Modalities:**
  - `"home"`
  - `"work"`
  - `"education"`
  - `"shopping"`
  - `"task"`
  - `"leisure"`
  - `"escort"`
  - `"other"`
- **Guarantees:**
  - Same guarantees as [`origin_purpose_group`](#origin_purpose_group).

### `destination_activity_duration`

Duration of the activity performed at the trip's destination, in minutes.

If this is the last trip of the day, the value is null.
Otherwise, the value is equal to the difference between the arrival time of the next trip and the
departure time of this trip (i.e., it is equal to the `origin_activity_duration` value of the next
trip).

- **Type:** UInt16
- **Guarantees:**
  - If `last_trip` is `true`, then the value is null.
  - The value is equal to the difference between `departure_time` for the next trip and
    `arrival_time` for the current trip.

## Escorting

### `origin_escort_purpose`

Purpose of the activity performed at the trip's origin by the person who is escorted.

- **Modalities:**
  - Same modalities as [`origin_purpose`](#origin_purpose), excluding all the `"escort:*"` purposes.
- **Guarantees:**
  - If `origin_purpose_group` is not `"escort"`, then the value is null.

### `origin_escort_purpose_group`

Purpose group of the activity performed at the trip's origin by the person who is escorted.

- **Modalities:**
  - `"home"`
  - `"work"`
  - `"education"`
  - `"shopping"`
  - `"task"`
  - `"leisure"`
  - `"other"`
- **Guarantees:**
  - If `origin_purpose_group` is not `"escort"`, then the value is null.
  - The values are consistent with `origin_escort_purpose`.

### `destination_escort_purpose`

Purpose of the activity performed at the trip's destination by the person who is escorted.

Note that in most cases, the destination escort purpose should be equal to the origin escort purpose
of the next trip (if any).
Rare exceptions can occur when someone is moving to a different location while the activity is
performed (e.g., for bus drivers).
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Modalities:**
  - Same modalities as [`origin_purpose`](#origin_purpose), excluding all the `"escort:*"`
    purposes.
- **Guarantees:**
  - If `destination_purpose_group` is not `"escort"`, then the value is null.

### `destination_escort_purpose_group`

Purpose group of the activity performed at the trip's destination by the person who is escorted.

- **Modalities:**
  - `"home"`
  - `"work"`
  - `"education"`
  - `"shopping"`
  - `"task"`
  - `"leisure"`
  - `"other"`
- **Guarantees:**
  - If `destination_purpose_group` is not `"escort"`, then the value is null.
  - The values are consistent with `destination_escort_purpose`.

## Shopping

### `origin_shop_type`

Type of shop where the activity at origin was performed (for shopping activities).

- **Modalities:**
  - `"small_shop"`: "petit commerce" / "supérette"
  - `"supermarket"`: "supermarché"
  - `"hypermarket"`: "hypermarché" / "grande surface"
  - `"supermarket_or_hypermarket"`: "supermarché" / "hypermarché" / "grande surface"
  - `"mall"`: "centre commercial" / "grand magasin"
  - `"market"`: "marché"
  - `"drive_in"`: "drive-in" / "point relais"
  - `"private"`: "particulier"
  - `"other"`
- **Guarantees:**
  - If `origin_purpose_group` is not `"shopping"`, then the value is null.

### `destination_shop_type`

Type of shop where the activity at destination was performed (for shopping activities).

- **Modalities:**
  - `"small_shop"`: "petit commerce"
  - `"supermarket"`: "supermarché"
  - `"hypermarket"`: "hypermarché" / "grande surface"
  - `"mall"`: "centre commercial" / "grand magasin"
  - `"market"`: "marché"
  - `"drive_in"`: "drive-in" / "point relais"
  - `"private"`: "particulier"
  - `"other"`
- **Guarantees:**
  - If `destination_purpose_group` is not `"shopping"`, then the value is null.

## Origin location

### `origin_lng`

Longitude of the trip's origin.

The accuracy depends on the survey type.
For EGT surveys, the coordinates are guaranteed to be within 100 meters of the actual location.
For other surveys, the coordinates represent the centroid of `origin_detailed_zone` (or the exact
coordinates defined by `origin_special_location` when it is non-null).

- **Type:** Float64

### `origin_lat`

Latitude of the trip's origin.

See [`origin_lng`](#origin_lng) for details on the accuracy of the value.

- **Type:** Float64

### `origin_special_location`

Identifier of the special location of the trip's origin.

- **Type:** String

### `origin_detailed_zone`

Identifier of the detailed zone of the trip's origin.

- **Type:** String

### `origin_draw_zone`

Identifier of the draw zone of the trip's origin.

- **Type:** String

### `origin_insee`

INSEE code of the municipality of the trip's origin.

- **Type:** String
- **Guarantees:**
  - String is a [valid INSEE code](../miscellaneous.md#insee-codes).

### `origin_insee_name`

Name of the municipality of the trip's origin.

- **Type:** String

### `origin_insee_density`

Density category of the origin INSEE municipality.

Density categories are defined by [INSEE](https://www.insee.fr/fr/information/6439600).

- **Modalities:**
  - `1`: "commune densément peuplée"
  - `2`: "centre urbain intermédiaire"
  - `3`: "ceinture urbaine"
  - `4`: "petite ville"
  - `5`: "bourg rural"
  - `6`: "rural à habitat dispersé"
  - `7`: "rural à habitat très dispersé"

### `origin_insee_aav_type`

Category of the origin INSEE municipality within its
["aire d'attraction des villes" (AAV)](https://www.insee.fr/fr/information/4803954).

The modalities follow the codes proposed by INSEE.

- **Modalities:**
  - `11`: "Commune-centre"
  - `12`: "Autre commune du pôle principal"
  - `13`: "Commune d'un pôle secondaire"
  - `20`: "Commune de la couronne"
  - `30`: "Commune hors attraction des villes"

### `origin_aav`

Code of the ["aire d'attraction des villes" (AAV)](https://www.insee.fr/fr/information/4803954) of
the trip's origin.

- **Type:** String

### `origin_aav_name`

Name of the ["aire d'attraction des villes" (AAV)](https://www.insee.fr/fr/information/4803954) of
the trip's origin.

- **Type:** String

### `origin_aav_category`

Category of the "aire d'attraction des villes" (AAV) of the trip's origin.

- **Modalities:**
  - `1`: Paris AAV
  - `2`: area with more than 700,000 inhabitants, excluding Paris ("aire de 700 000 habitants ou
    plus (hors Paris)")
  - `3`: area between 200,000 and 700,000 inhabitants ("aire de 200 000 à moins de 700 000
    habitants")
  - `4`: area between 50,000 and 200,000 inhabitants ("aire de 50 000 à moins de 200 000 habitants")
  - `5`: area with less than 50,000 inhabitants ("aire de moins de 50 000 habitants")

### `origin_dep`

_Département_ code of the trip's origin.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `origin_insee` is not null, then the value is equal to the _département_ of the origin INSEE
    municipality.

### `origin_dep_name`

Name of the _département_ of the trip's origin.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `origin_dep`.

### `origin_nuts2`

NUTS 2 code of the trip's origin.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `origin_dep` is not null, then the value is equal to the NUTS 2 code corresponding to the
    origin _département_.

### `origin_nuts2_name`

Name of the NUTS 2 region of the trip's origin.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `origin_nuts2`.

### `origin_nuts1`

NUTS 1 code of the trip's origin.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `origin_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to the
    origin NUTS 2.

### `origin_nuts1_name`

Name of the NUTS 1 region of the trip's origin.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `origin_nuts1`.

## Destination location

### `destination_lng`

Longitude of the trip's destination.

See [`origin_lng`](#origin_lng) for details on the accuracy of the value.

- **Type:** Float64

### `destination_lat`

Latitude of the trip's destination.

See [`origin_lng`](#origin_lng) for details on the accuracy of the value.

- **Type:** Float64

### `destination_special_location`

Identifier of the special location of the trip's destination.

Note that in most cases, the destination special location should be equal to the origin special
location of the next trip (if any).
Rare exceptions can occur when someone is moving to a different location while the activity is
performed (e.g., for bus drivers).
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Type:** String

### `destination_detailed_zone`

Identifier of the detailed zone of the trip's destination.

Note that in most cases, the destination detailed zone should be equal to the origin detailed zone
of the next trip (if any).
Rare exceptions can occur when someone is moving to a different location while the activity is
performed (e.g., for bus drivers).
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Type:** String

### `destination_draw_zone`

Identifier of the draw zone of the trip's destination.

Note that in most cases, the destination draw zone should be equal to the origin draw zone of the
next trip (if any).
Rare exceptions can occur when someone is moving to a different location while the activity is
performed (e.g., for bus drivers).
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Type:** String

### `destination_insee`

INSEE code of the municipality of the trip's destination.

Note that in most cases, the destination INSEE code should be equal to the origin INSEE code of the
next trip (if any).
Rare exceptions can occur when someone is moving to a different location while the activity is
performed (e.g., for bus drivers).
MobiSurvStd will show warning messages indicating how many trips does not match the constraint.

- **Type:** String
- **Guarantees:**
  - String is a [valid INSEE code](../miscellaneous.md#insee-codes).

### `destination_insee_name`

Name of the municipality of the trip's destination.

- **Type:** String

### `destination_insee_density`

Density category of the destination INSEE municipality.

Density categories are defined by [INSEE](https://www.insee.fr/fr/information/6439600).

- **Modalities:**
  - `1`: "commune densément peuplée"
  - `2`: "centre urbain intermédiaire"
  - `3`: "ceinture urbaine"
  - `4`: "petite ville"
  - `5`: "bourg rural"
  - `6`: "rural à habitat dispersé"
  - `7`: "rural à habitat très dispersé"

### `destination_insee_aav_type`

Category of the destination INSEE municipality within its
["aire d'attraction des villes" (AAV)](https://www.insee.fr/fr/information/4803954).

The modalities follow the codes proposed by INSEE.

- **Modalities:**
  - `11`: "Commune-centre"
  - `12`: "Autre commune du pôle principal"
  - `13`: "Commune d'un pôle secondaire"
  - `20`: "Commune de la couronne"
  - `30`: "Commune hors attraction des villes"

### `destination_aav`

Code of the ["aire d'attraction des villes" (AAV)](https://www.insee.fr/fr/information/4803954) of
the trip's destination.

- **Type:** String

### `destination_aav_name`

Name of the ["aire d'attraction des villes" (AAV)](https://www.insee.fr/fr/information/4803954) of
the trip's destination.

- **Type:** String

### `destination_aav_category`

Category of the "aire d'attraction des villes" (AAV) of the trip's destination.

- **Modalities:**
  - `1`: Paris AAV
  - `2`: area with more than 700,000 inhabitants, excluding Paris ("aire de 700 000 habitants ou
    plus (hors Paris)")
  - `3`: area between 200,000 and 700,000 inhabitants ("aire de 200 000 à moins de 700 000
    habitants")
  - `4`: area between 50,000 and 200,000 inhabitants ("aire de 50 000 à moins de 200 000 habitants")
  - `5`: area with less than 50,000 inhabitants ("aire de moins de 50 000 habitants")

### `destination_dep`

_Département_ code of the trip's destination.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `destination_insee` is not null, then the value is equal to the _département_ of the
    destination INSEE municipality.

### `destination_dep_name`

Name of the _département_ of the trip's destination.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `destination_dep`.

### `destination_nuts2`

NUTS 2 code of the trip's destination.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `destination_dep` is not null, then the value is equal to the NUTS 2 code corresponding to
    the destination _département_.

### `destination_nuts2_name`

Name of the NUTS 2 region of the trip's destination.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `destination_nuts2`.

### `destination_nuts1`

NUTS 1 code of the trip's destination.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `destination_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to
    the destination NUTS 2.

### `destination_nuts1_name`

Name of the NUTS 1 region of the trip's destination.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `destination_nuts1`.

## Timing

### `departure_time`

Departure time from origin, in number of minutes after midnight.

- **Type:** UInt16
- **Guarantees:**
  - The value is larger than `departure_time` values of the person's trips with a smaller
    `trip_index`.

### `arrival_time`

Arrival time at destination, in number of minutes after midnight.

- **Type:** UInt16
- **Guarantees:**
  - The value is not smaller than `departure_time`.
  - The value is not larger than the `departure_time` values of the next trip (if any).

### `travel_time`

Travel time of the trip, in minutes.

- **Type:** UInt16
- **Guarantees:**
  - The value is equal to `arrival_time - departure_time`.

### `trip_date`

Date at which the trip took place.

- **Type:** Date
- **Guarantees:**
  - The value cannot be later than the household's `interview_date`.

### `trip_weekday`

Day of the week when the trip took place.

- **Modalities:**
  - `"monday"`
  - `"tuesday"`
  - `"wednesday"`
  - `"thursday"`
  - `"friday"`
  - `"saturday"`
  - `"sunday"`
- **Guarantees:**
  - The value is consistent with `trip_date`.
  - The value is equal to the household `trips_weekday` (when it is non-null).

## Transportation mode

### `main_mode`

Main mode of transportation used for the trip.

In case of intermodality, there is no clear rule how the main mode is defined.

- **Modalities:**
  - `"walking"`
  - `"bicycle:driver"`: driver of a bicycle (traditional or electric)
  - `"bicycle:driver:shared"`: driver of a bicycle (traditional or electric) from a shared service
  - `"bicycle:driver:traditional"`: driver of a traditional bicycle
  - `"bicycle:driver:traditional:shared"`: driver of a traditional bicycle from a shared service
  - `"bicycle:driver:electric"`: driver of an electric bicycle
  - `"bicycle:driver:electric:shared"`: driver of an electric bicycle from a shared service
  - `"bicycle:passenger"`: passenger on a (unspecified) bicycle
  - `"motorcycle:driver"`: driver of a motorcycle (unspecified size)
  - `"motorcycle:passenger"`: passenger on a motorcycle (unspecified size)
  - `"motorcycle:driver:moped"`: driver of a small motorcycle (< 50 cm³)
  - `"motorcycle:passenger:moped"`: passenger on a small motorcycle (< 50 cm³)
  - `"motorcycle:driver:moto"`: driver of a large motorcycle (≥ 50 cm³)
  - `"motorcycle:passenger:moto"`: passenger on a large motorcycle (≥ 50 cm³)
  - `"car:driver"`: driver of a car
  - `"car:passenger"`: passenger in a car
  - `"taxi"`: passenger in a taxi
  - `"VTC"`: passenger in a VTC
  - `"taxi_or_VTC"`: passenger in a taxi or VTC
  - `"public_transit:urban"`: passenger in a (unspecified) public-transit vehicle (in urban context)
  - `"public_transit:urban:bus"`: passenger in a bus
  - `"public_transit:urban:coach"`: passenger in a coach ("autocar"), excluding long-distance trips
  - `"public_transit:urban:tram"`: passenger in a tramway
  - `"public_transit:urban:metro"`: passenger in a metro
  - `"public_transit:urban:funicular"`: passenger in a funicular
  - `"public_transit:urban:rail"`: passenger in an express rail service (e.g., RER)
  - `"public_transit:urban:TER"`: passenger in a TER
  - `"public_transit:urban:demand_responsive"`: passenger in a demand-responsive service
  - `"public_transit:interurban:coach"`: passenger in an interurban coach ("autocar")
  - `"public_transit:interurban:TGV"`: passenger in a TGV
  - `"public_transit:interurban:intercités"`: passenger in an Intercités
  - `"public_transit:interurban:other_train"`: passenger in another train type
  - `"public_transit:school"`: passenger in a school transport line ("ramassage scolaire")
  - `"reduced_mobility_transport"`: passenger in a specialized transport for persons with reduced
    mobility
  - `"employer_transport"`: passenger in a transport service provided by the employer
  - `"truck:driver"`: driver of a truck ("fourgon", "camionnette", "camion")
  - `"truck:passenger"`: passenger of a truck ("fourgon", "camionnette", "camion")
  - `"water_transport"`: waterway or maritime transport
  - `"airplane"`
  - `"wheelchair"`
  - `"personal_transporter:non_motorized"`: non-motorized personal transporter ("trottinette",
    "skateboard", "roller", etc.)
  - `"personal_transporter:motorized"`: motorized personal transporter ("trottinette électrique",
    "segway", "solowheel", etc.)
  - `"personal_transporter:unspecified"`: personal transporter (unspecified motorization)
  - `"other"`: other transport mode
- **Guarantees:**
  - There is at least one leg with that mode for the trip.

### `main_mode_group`

Mode group of the main mode of transportation used for the trip.

- **Modalities:**
  - `"walking"`: walking, excluding wheelchair and personal transporter
  - `"bicycle"`: bicycle (traditional or electric, driver or passenger, personal or shared)
  - `"motorcycle"`: motorcycle (small and large, driver or passenger)
  - `"car_driver"`: car as a driver
  - `"car_passenger"`: car as a passenger (including taxi and VTC)
  - `"public_transit"`: any form of public transit (excluding employer transport)
  - `"other"`: all other modes
- **Guarantees:**
  - The values are consistent with `main_mode`.

### `intermodality`

Whether the trip involved using two different modes of transportation.

Note that combining walking with another transportation mode is not classified as intermodality and
combining various public-transit modes (e.g., bus then metro) is not either.

- **Type:** Boolean
- **Guarantees:**
  - If the value is `true`, then there is at least two legs with different `mode_group` (excluding
    walking legs).

### `public_transit_access_mode`

Mode of transportation used for the access part of the trip (for public-transit trip).

- **Modalities:**
  - Same modalities as [`main_mode`](#main_mode) (excluding all public-transit modes).
- **Guarantees:**
  - If `main_mode_group` is not `"public_transit"`, then the value is null.
  - The value is equal to the [`mode`](legs.md#mode) of the first leg of the trip.

### `public_transit_access_mode_group`

Mode group of the transportation mode used for the access part of the trip (for public-transit
trip).

- **Modalities:**
  - Same modalities as [`main_mode_group`](#main_mode_group) (excluding `"public_transit"`).
- **Guarantees:**
  - If `main_mode_group` is not `"public_transit"`, then the value is null.
  - The value is consistent with `public_transit_access_mode`.

### `public_transit_egress_mode`

Mode of transportation used for the egress part of the trip (for public-transit trip).

- **Modalities:**
  - Same modalities as [`main_mode`](#main_mode) (excluding all public-transit modes).
- **Guarantees:**
  - If `main_mode_group` is not `"public_transit"`, then the value is null.
  - The value is equal to the [`mode`](legs.md#mode) of the last leg of the trip.

### `public_transit_egress_mode_group`

Mode group of the transportation mode used for the egress part of the trip (for public-transit
trip).

- **Modalities:**
  - Same modalities as [`main_mode_group`](#main_mode_group) (excluding `"public_transit"`).
- **Guarantees:**
  - If `main_mode_group` is not `"public_transit"`, then the value is null.
  - The value is consistent with `public_transit_egress_mode`.

## Distances

### `trip_euclidean_distance_km`

Euclidean distance between the trip's origin and destination, in kilometers.

- **Type:** Float64
- **Guarantees:**
  - All values are non-negative.

### `trip_travel_distance_km`

Travel distance of the trip, in kilometers.

This is usually a distance on the road network.
The details regardings how this value is computed depends on the surveys.

- **Type:** Float64
- **Guarantees:**
  - All values are non-negative.

### `intra_municipality`

Whether the INSEE municipality of the trip's origin is equal to the INSEE municipality of the trip's
destination.

- **Type:** Boolean
- **Guarantees:**
  - If the value is `true`, then `origin_insee` is equal to `destination_insee`.

### `intra_aav`

Whether the AAV of the trip's origin is equal to the AAV of the trip's destination.

- **Type:** Boolean
- **Guarantees:**
  - If the value is `true`, then `origin_aav` is equal to `destination_aav`.

### `intra_dep`

Whether the département of the trip's origin is equal to the département of the trip's destination.

- **Type:** Boolean
- **Guarantees:**
  - If the value is `true`, then `origin_dep` is equal to `destination_dep`.

### `trip_perimeter`

Perimiter in which the trip is taking place relative to the survey area.

- **Modalities:**
  - `"internal"`: the trip is starting and ending within the survey area
  - `"crossing"`: the trip is either starting or ending within the survey area
  - `"external"`: the trip is not starting nor ending within the survey area

## Leg / stop counts

### `nb_tour_stops`

Number of stops for trips representing tours.

- **Type:** UInt8
- **Guarantees:**
  - If neither `origin_purpose` nor `destination_purpose` is `"work:professional_tour"` or
    `"shopping:tour_no_purchase"`, then the value is null.

### `nb_legs`

Number of legs that this trip is composed of.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is positive.
  - The value is equal to the number of legs in `legs.parquet` for that trip.

### `nb_legs_walking`

Number of legs with mode group `"walking"` in the trip.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"walking"`.

### `nb_legs_bicycle`

Number of legs with mode group `"bicycle"` in the trip.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"bicycle"`.

### `nb_legs_motorcycle`

Number of legs with mode group `"motorcycle"` in the trip.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"motorcycle"`.

### `nb_legs_car_driver`

Number of legs with mode group `"car_driver"` in the trip.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"car_driver"`.

### `nb_legs_car_passenger`

Number of legs with mode group `"car_passenger"` in the trip.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"car_passenger"`.

### `nb_legs_public_transit`

Number of legs with mode group `"public_transit"` in the trip.

For public-transit trips, the number of transfers is thus `nb_legs_public_transit - 1`.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"public_transit"`.

### `nb_legs_other`

Number of legs with mode group `"other"` in the trip.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null when `main_mode` is not null.
  - The value is equal to the number of legs in the trip whose `mode_group` is `"other"`.
