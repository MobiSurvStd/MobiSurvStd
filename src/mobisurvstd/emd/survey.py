import os
import re
from datetime import timedelta
from zipfile import ZipFile

import geopandas as gpd
import polars as pl
from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.common.zones import get_coords
from mobisurvstd.utils import find_file

from .deplacements import standardize_trips
from .menages import (
    main_survey_insee,
    standardize_cars,
    standardize_households,
    standardize_motorcycles,
)
from .personnes import standardize_persons
from .trajets import standardize_legs
from .zones import (
    read_detailed_zones,
    read_draw_zones,
    read_special_locations,
    read_special_locations_and_detailed_zones,
)


def standardize(source: str | ZipFile, skip_spatial: bool = False):
    source_name = source.filename if isinstance(source, ZipFile) else source
    logger.info(f"Standardizing EDVM survey from `{source_name}`")
    if skip_spatial:
        special_locations = None
        detailed_zones = None
        draw_zones = None
    else:
        special_locations, detailed_zones, draw_zones = read_spatial_data(source, source_name)

    if special_locations is not None:
        special_locations_coords = get_coords(special_locations, "special_location")
    else:
        special_locations_coords = None
    if detailed_zones is not None:
        detailed_zones_coords = get_coords(detailed_zones, "detailed_zone")
    else:
        detailed_zones_coords = None

    # Households.
    filename = households_filename(source)
    if filename is None:
        logger.error("Missing households file")
        return None
    main_insee = main_survey_insee(filename)
    households = standardize_households(filename, special_locations_coords, detailed_zones_coords)
    cars = standardize_cars(filename, households)
    motorcycles = standardize_motorcycles(filename, households)
    # Persons.
    filename = persons_filename(source)
    if filename is None:
        logger.error("Missing persons file")
        return None
    persons = standardize_persons(
        filename, households, special_locations_coords, detailed_zones_coords
    )
    # Trips.
    filename = trips_filename(source)
    if filename is None:
        logger.error("Missing trips file")
        return None
    trips = standardize_trips(filename, persons, special_locations_coords, detailed_zones_coords)
    # Legs.
    filename = legs_filename(source)
    if filename is None:
        logger.error("Missing legs file")
        return None
    legs = standardize_legs(
        filename, trips, cars, motorcycles, special_locations_coords, detailed_zones_coords
    )

    households = add_survey_dates(households, persons)

    return clean(
        households=households,
        persons=persons,
        trips=trips,
        legs=legs,
        cars=cars,
        motorcycles=motorcycles,
        special_locations=special_locations,
        detailed_zones=detailed_zones,
        draw_zones=draw_zones,
        survey_type="EMD",
        survey_name=survey_name(source),
        main_insee=main_insee,
    )


def read_spatial_data(source: str | ZipFile, source_name: str):
    if filename := special_locations_and_detailed_zones_filename(source):
        # Special case for Beauvais 2011.
        detailed_zones, special_locations = read_special_locations_and_detailed_zones(filename)
    else:
        # Special locations.
        if filename := special_locations_filename(source):
            logger.debug(f"Reading special locations from `{filename}`")
            special_locations = read_special_locations(filename)
        else:
            special_locations = None
        # Detailed zones.
        if filename := detailed_zones_filename(source):
            logger.debug(f"Reading detailed zones from `{filename}`")
            detailed_zones = read_detailed_zones(filename)
        else:
            logger.debug(f"No file with detailed zones in `{source_name}`")
            detailed_zones = None
    # Draw zones.
    if filename := draw_zones_filename(source):
        logger.debug(f"Reading draw zones from `{filename}`")
        draw_zones = read_draw_zones(filename)
    else:
        logger.debug(f"No file with draw zones in `{source_name}`")
        draw_zones = None

    if special_locations is not None:
        assert (
            detailed_zones is not None
        ), "Special locations are defined but there is no data on detailed zones"
        if "detailed_zone_id" not in special_locations.columns:
            special_locations = identify_detailed_zone_id(special_locations, detailed_zones)

    if special_locations is not None:
        # For Lille 2015, some GT ids also have corresponding zones. We remove these zones to
        # prevent any issue.
        assert detailed_zones is not None
        detailed_zones = detailed_zones.loc[
            ~detailed_zones["detailed_zone_id"].isin(special_locations["special_location_id"])
        ]
        assert (
            len(
                set(special_locations["special_location_id"]).intersection(
                    set(detailed_zones["detailed_zone_id"])
                )
            )
            == 0
        ), "Special locations and detailed zones have common ids"

    return special_locations, detailed_zones, draw_zones


def survey_name(source: str | ZipFile):
    filename = find_file(source, ".*_std_men.csv", subdir="Csv", as_url=True)
    return re.match("(.*)_std_men.csv", os.path.basename(filename)).group(1)


def households_filename(source: str | ZipFile):
    return find_file(source, ".*_std_men.csv", subdir="Csv")


def persons_filename(source: str | ZipFile):
    return find_file(source, ".*_std_pers.csv", subdir="Csv")


def trips_filename(source: str | ZipFile):
    return find_file(source, ".*_std_depl.csv", subdir="Csv")


def legs_filename(source: str | ZipFile):
    return find_file(source, ".*_std_traj.csv", subdir="Csv")


def special_locations_and_detailed_zones_filename(source: str | ZipFile):
    # This should only match the Valenciennes 2011 survey.
    return find_file(source, ".*zf_gt[.]mif", subdir=os.path.join("Doc", "SIG"), as_url=True)


def detailed_zones_filename(source: str | ZipFile):
    return find_file(
        source,
        ".*(_zf|zones?[_ ]?fines?.*)[.](tab|mif)",
        subdir=os.path.join("Doc", "SIG"),
        as_url=True,
    )


def special_locations_filename(source: str | ZipFile):
    return find_file(
        source, ".*(_gt|g.?n.?rateur.*)[.](tab|mif)", subdir=os.path.join("Doc", "SIG"), as_url=True
    )


def draw_zones_filename(source: str | ZipFile):
    return find_file(
        source,
        ".*(_DTIR|secteur_.*)[.](tab|shp|mif)",
        subdir=os.path.join("Doc", "SIG"),
        as_url=True,
    )


def add_survey_dates(households: pl.LazyFrame, persons: pl.LazyFrame):
    # Survey date is specified at the person-level, we create here the household-level
    # `interview_date`.
    household_dates = persons.group_by("household_id").agg(pl.col("trip_date").first())
    households = households.join(
        household_dates, on="household_id", how="left", coalesce=True
    ).with_columns(interview_date=pl.col("trip_date") + timedelta(days=1))
    return households


def fix_special_locations_with_gcd(
    df: pl.LazyFrame, col: str, special_locations: gpd.GeoDataFrame, gcd: int
):
    mask = (pl.col(f"{col}_detailed_zone").cast(pl.Int64) % gcd) == 0
    df = df.with_columns(
        # When the ZF is an actual ZF
        pl.when(mask)
        # Then use that ZF
        .then(f"{col}_detailed_zone")
        # Otherwise try to find the ZF corresponding to that GT and use a null value if there
        # is no such GT.
        .otherwise(
            pl.col(f"{col}_detailed_zone").replace_strict(
                pl.from_pandas(special_locations["special_location_id"].astype(int)),
                pl.from_pandas(special_locations["detailed_zone_id"].astype(int)),
                default=None,
            )
        ).alias(f"{col}_detailed_zone"),
        # When the ZF is an actual ZF
        pl.when(mask)
        # Then the GT is null
        .then(pl.lit(None))
        # Otherwise use that GT as GT.
        .otherwise(f"{col}_detailed_zone").alias(f"{col}_special_location"),
    )
    return df


def fix_special_locations(df: pl.LazyFrame, col: str, special_locations: gpd.GeoDataFrame):
    mask = (
        pl.col(f"{col}_detailed_zone")
        .is_in(special_locations["special_location_id"].astype(int))
        .not_()
    )
    df = df.with_columns(
        # When the ZF is an actual ZF
        pl.when(mask)
        # Then use that ZF
        .then(f"{col}_detailed_zone")
        # Otherwise use the ZF corresponding to that GT.
        .otherwise(
            pl.col(f"{col}_detailed_zone").replace_strict(
                pl.from_pandas(special_locations["special_location_id"].astype(int)),
                pl.from_pandas(special_locations["detailed_zone_id"].astype(int)),
                default=None,
            )
        ).alias(f"{col}_detailed_zone"),
        # When the ZF is an actual ZF
        pl.when(mask)
        # Then the GT is null
        .then(pl.lit(None))
        # Otherwise use that GT as GT.
        .otherwise(f"{col}_detailed_zone").alias(f"{col}_special_location"),
    )
    return df


def identify_detailed_zone_id(
    special_locations: gpd.GeoDataFrame, detailed_zones: gpd.GeoDataFrame
):
    """Adds `detailed_zone_id` column to special_locations by finding the detailed zone in which the
    special location falls.
    """
    orig_crs = special_locations.crs
    special_locations.to_crs(detailed_zones.crs, inplace=True)
    special_locations = special_locations.sjoin(
        detailed_zones[["geometry", "detailed_zone_id"]], predicate="within", how="left"
    )
    special_locations.drop(columns=["index_right"], inplace=True)
    special_locations.drop_duplicates(subset=["special_location_id"])
    special_locations.to_crs(orig_crs, inplace=True)
    return special_locations
