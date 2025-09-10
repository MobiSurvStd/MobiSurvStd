import polars as pl

from .common import CURRENT_YEAR, PARKING_LOCATION_ENUM, PARKING_TYPE_ENUM, Variable
from .guarantees import (
    Bounded,
    Defined,
    Indexed,
    LargerThan,
    NonDecreasing,
    Null,
    SmallerThan,
)

MOTORCYCLE_SCHEMA = [
    # Identifier of the motorcycle.
    Variable("motorcycle_id", pl.UInt32, [Indexed()]),
    # Identifier of the household the motorcycle belongs to.
    Variable("household_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Index of the motorcycle within the household's motorcycles.
    Variable("motorcycle_index", pl.UInt8, [Defined(), Indexed(over=pl.col("household_id"))]),
    # Identifier of the motorcycle in the original survey data.
    Variable("original_motorcycle_id", pl.Struct),
    # Type of the motorcycle.
    Variable("type", pl.Enum(["moped", "scooter", "motorbike", "motorized_tricycle", "other"])),
    # Fuel type used by the motorcycle.
    Variable("fuel_type", pl.Enum(["thermic", "electric", "other"])),
    # Year the motorcycle was first used.
    Variable("year", pl.UInt16, [Bounded(1900, CURRENT_YEAR)]),
    # Type of engine for the motorcycle (if thermic).
    Variable(
        "thermic_engine_type",
        pl.Enum(["two_stroke", "four_stroke"]),
        [Null(when=pl.col("fuel_type") != "thermic")],
    ),
    # Lower bound for the cubic capacity of the motorcycle in cm3 (if thermic).
    Variable("cm3_lower_bound", pl.UInt16, [Null(when=pl.col("fuel_type") != "thermic")]),
    # Upper bound for the cubic capacity of the motorcycle in cm3 (if thermic).
    Variable(
        "cm3_upper_bound",
        pl.UInt16,
        [
            Null(when=pl.col("fuel_type") != "thermic"),
            LargerThan(pl.col("cm3_lower_bound"), strict=False),
        ],
    ),
    # Lower bound for the energy power of the motorcycle in kw (if electric).
    Variable("kw_lower_bound", pl.UInt16, [Null(when=pl.col("fuel_type") != "electric")]),
    # Upper bound for the energy power of the motorcycle in kw (if electric).
    Variable(
        "kw_upper_bound",
        pl.UInt16,
        [
            Null(when=pl.col("fuel_type") != "electric"),
            LargerThan(pl.col("kw_lower_bound"), strict=False),
        ],
    ),
    # Annual mileage of the car in kilometers.
    Variable("annual_mileage", pl.UInt32),
    # Lower bound for the annual mileage of the car in kilometers.
    Variable(
        "annual_mileage_lower_bound",
        pl.UInt32,
        [SmallerThan(pl.col("annual_mileage"), strict=False)],
    ),
    # Upper bound for the annual mileage of the car in kilometers.
    Variable(
        "annual_mileage_upper_bound",
        pl.UInt32,
        [
            LargerThan(pl.col("annual_mileage"), strict=False),
            LargerThan(pl.col("annual_mileage_lower_bound"), strict=False),
        ],
    ),
    # Type of location used to park the motorcycle overnight.
    Variable("parking_location", PARKING_LOCATION_ENUM),
    # Type of parking (paid or free) used to park the motorcycle overnight.
    Variable("parking_type", PARKING_TYPE_ENUM),
]
