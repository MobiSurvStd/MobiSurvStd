import polars as pl

from .common import CURRENT_YEAR, PARKING_LOCATION_ENUM, PARKING_TYPE_ENUM, Variable
from .guarantees import (
    Bounded,
    Defined,
    EqualTo,
    Indexed,
    LargerThan,
    NonDecreasing,
    SmallerThan,
)

CAR_SCHEMA = [
    # Identifier of the car.
    Variable("car_id", pl.UInt32, [Indexed()]),
    # Identifier of the household the car belongs to.
    Variable("household_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Index of the car within the household's cars.
    Variable("car_index", pl.UInt8, [Defined(), Indexed(over=pl.col("household_id"))]),
    # Identifier of the car in the original survey data.
    Variable("original_car_id", pl.Struct),
    # Type of the car.
    Variable(
        "type",
        pl.Enum(["passenger_car", "recreational_vehicle", "utility_vehicle", "license_free_car"]),
    ),
    # Fuel type of the car.
    Variable(
        "fuel_type",
        pl.Enum(
            [
                "thermic:petrol",
                "thermic:diesel",
                "thermic:gas",
                "electric",
                "hybrid:regular",
                "hybrid:regular:petrol",
                "hybrid:regular:diesel",
                "hybrid:plug-in",
                "hybrid:unspecified",
                "other",
            ]
        ),
    ),
    # Fuel type of the car in groups.
    Variable(
        "fuel_type_group",
        pl.Enum(["thermic", "electric", "hybrid", "other"]),
        [
            EqualTo(
                pl.col("fuel_type").cast(pl.String).str.extract(r"(\w+):?"), '"fuel_type" group'
            ),
        ],
    ),
    # Year the car was first used.
    Variable("year", pl.UInt16, [Bounded(1900, CURRENT_YEAR)]),
    # Tax horsepower of the car.
    Variable("tax_horsepower", pl.UInt16),
    # Crit'Air vignette of the vehicle.
    Variable("critair", pl.Enum(["E", "1", "2", "3", "4", "5", "N"])),
    # Total mileage of the car in kilometers.
    Variable("total_mileage", pl.UInt32),
    # Lower bound for the total mileage of the car in kilometers.
    Variable(
        "total_mileage_lower_bound", pl.UInt32, [SmallerThan(pl.col("total_mileage"), strict=False)]
    ),
    # Upper bound for the total mileage of the car in kilometers.
    Variable(
        "total_mileage_upper_bound", pl.UInt32, [LargerThan(pl.col("total_mileage"), strict=False)]
    ),
    # Annual mileage of the car in kilometers.
    Variable("annual_mileage", pl.UInt32),
    # Lower bound for the annual mileage of the car in kilometers.
    Variable(
        "annual_mileage_lower_bound",
        pl.UInt32,
        [SmallerThan(pl.col("annual_mileage_lower_bound"), strict=False)],
    ),
    # Upper bound for the annual mileage of the car in kilometers.
    Variable(
        "annual_mileage_upper_bound",
        pl.UInt32,
        [
            LargerThan(pl.col("annual_mileage"), strict=False),
            LargerThan(pl.col("annual_mileage_upper_bound"), strict=False),
        ],
    ),
    # Type of ownership of the car.
    Variable(
        "ownership",
        pl.Enum(
            [
                "personal",
                "employer:full_availability",
                "employer:limited_availability",
                "leasing",
                "shared",
                "other",
            ]
        ),
    ),
    # Type of location used to park the car overnight.
    Variable("parking_location", PARKING_LOCATION_ENUM),
    # Type of parking (paid or free) used to park the car overnight.
    Variable("parking_type", PARKING_TYPE_ENUM),
]
