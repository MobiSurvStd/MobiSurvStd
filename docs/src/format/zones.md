# Zones

Special locations, detailed zones and draw zones are all stored in similar GeoParquet files whose
variables are described below.

The Coordinate Reference System (CRS) of the GeoParquet files is the one from the survey.

## Identifiers

### `special_location_id`

Identifier of the special location.

- **Type:** String
- Mandatory for `special_locations.geo.parquet`, missing for the other

### `detailed_zone_id`

Identifier of the detailed zone.

- **Type:** String
- Mandatory for `detailed_zones.geo.parquet`, optional for `special_locations.geo.parquet`, missing
  for `draw_zones.geo.parquet`

### `draw_zone_id`

Identifier of the draw zone.

- **Type:** String
- Mandatory for `draw_zones.geo.parquet`, optional for the other

### `insee_id`

INSEE code of the municipality within which the location / zone is.

- **Type:** String
- Optional for all files

## Geometry

### `geometry`

Geometry representing the location / zone.

- **Type:** Geometry (Point for special locations, Polygon for detailed / draw zones)

## Counts

### `nb_homes`

Number of households whose home location is equal to the given location / zone.

- **Type:** UInt32

### `nb_work_locations`

Number of persons whose work location is equal to the given location / zone.

- **Type:** UInt32

### `nb_study_locations`

Number of persons whose study location is equal to the given location / zone.

- **Type:** UInt32

### `nb_trip_origins`

Number of trips whose origin is equal to the given location / zone.

- **Type:** UInt32

### `nb_trip_destinations`

Number of trips whose destination is equal to the given location / zone.

- **Type:** UInt32

### `nb_leg_starts`

Number of legs whose start point is equal to the given location / zone.

- **Type:** UInt32

### `nb_leg_ends`

Number of legs whose end point is equal to the given location / zone.

- **Type:** UInt32
