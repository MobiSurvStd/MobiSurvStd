import os
import re
from datetime import timedelta
from zipfile import ZipFile

import geopandas as gpd
import numpy as np
import polars as pl
from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.common.zones import get_coords
from mobisurvstd.utils import find_file

from .deplacements import standardize_trips
from .menages import (
    standardize_cars,
    standardize_households,
    standardize_motorcycles,
)
from .personnes import standardize_persons
from .trajets import standardize_legs
from .zones import read_detailed_zones, read_draw_zones, read_special_locations


def standardize(source: str | ZipFile, skip_spatial: bool = False):
    source_name = source.filename if isinstance(source, ZipFile) else source
    logger.info(f"Standardizing EDGT survey from `{source_name}`")
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
    filenames = households_filename(source)
    if not all(filenames):
        logger.error("Missing households file")
        return None
    main_insee = survey_main_insee(filenames[0])
    households = standardize_households(*filenames, special_locations_coords, detailed_zones_coords)
    cars = standardize_cars(*filenames, households)
    motorcycles = standardize_motorcycles(*filenames, households)
    # Persons.
    filenames = persons_filename(source)
    if not all(filenames):
        logger.error("Missing persons file")
        return None
    persons = standardize_persons(
        *filenames, households, special_locations_coords, detailed_zones_coords
    )
    # Trips.
    filenames = trips_filename(source)
    if not all(filenames):
        logger.error("Missing trips file")
        return None
    trips = standardize_trips(*filenames, persons, special_locations_coords, detailed_zones_coords)
    # Legs.
    filenames = legs_filename(source)
    if not all(filenames):
        logger.error("Missing legs file")
        return None
    legs = standardize_legs(
        *filenames, trips, cars, motorcycles, special_locations_coords, detailed_zones_coords
    )

    households = add_survey_dates(households, persons)

    # Fix the special locations which are being used as detailed zones.
    if special_locations is not None:
        assert (
            len(
                set(special_locations["special_location_id"]).intersection(
                    set(detailed_zones["detailed_zone_id"])
                )
            )
            == 0
        ), "Special locations and detailed zones have common ids"
        # Note. ZF ids usually ends with 2 or 3 zeros. Special locations (GT) have the same first
        # digits as the corresponding ZF.
        # Example: ZF: 70100 ; GTs: 70101, 70102, 70105, etc.
        # In some cases, not all GTs are defined.
        # For example, `origin_detailed_zone` can be defined as 70103 but there is no special
        # location with that id. In this case, we can guess that the ZF id is 70100.
        if np.log10(sl_gcd).is_integer() and sl_gcd > 1:
            # All ZF ids are ending with zeros. In principle, all GT ids do _not_ end with zeros.
            # We raise an error if at least 2 GT ids end with zeros.
            # (In the Tours survey, there is a "Unknown" zone whose id ends with zero.)
            assert (
                (special_locations["special_location_id"].astype(int) % sl_gcd) == 0
            ).sum() <= 1, "Unsupported ZF / GT id system"
            households = fix_special_locations_with_gcd(
                households, "home", special_locations, sl_gcd
            )
            persons = fix_special_locations_with_gcd(persons, "work", special_locations, sl_gcd)
            persons = fix_special_locations_with_gcd(persons, "study", special_locations, sl_gcd)
            trips = fix_special_locations_with_gcd(trips, "origin", special_locations, sl_gcd)
            trips = fix_special_locations_with_gcd(trips, "destination", special_locations, sl_gcd)
            legs = fix_special_locations_with_gcd(legs, "start", special_locations, sl_gcd)
            legs = fix_special_locations_with_gcd(legs, "end", special_locations, sl_gcd)
        else:
            # GT and ZF use a different system (e.g., Besançon 2018: GTs end with 5x, ZF ends with
            # 0x).
            # In this case, we hope that all special locations are correctly defined.
            households = fix_special_locations(households, "home", special_locations)
            persons = fix_special_locations(persons, "work", special_locations)
            persons = fix_special_locations(persons, "study", special_locations)
            trips = fix_special_locations(trips, "origin", special_locations)
            trips = fix_special_locations(trips, "destination", special_locations)
            legs = fix_special_locations(legs, "start", special_locations)
            legs = fix_special_locations(legs, "end", special_locations)

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
        survey_type="EDGT",
        survey_name=survey_name(source),
        main_insee=main_insee,
    )


def read_spatial_data(source: str | ZipFile, source_name: str):
    # Special locations.
    filename = special_locations_filename(source)
    if filename is None:
        special_locations = None
    elif "EDGT_SCOTAM_2017" in source_name or "Angers12" in source_name or "EDGTFVG2016":
        # Note. Special case for Metz 2017 and Angers 2012: I cannot figure out the ids in the GT
        # and ZF files.
        # For Annemasse 2016, the GT id does not seem to be specified.
        logger.warning("Cannot read special locations: ids are invalid")
        special_locations = None
    else:
        logger.debug(f"Reading special locations from `{filename}`")
        special_locations = read_special_locations(filename)
    # Detailed zones.
    filename = detailed_zones_filename(source)
    if filename is None:
        logger.debug(f"No file with detailed zones in `{source_name}`")
        detailed_zones = None
    elif "EDGT_SCOTAM_2017" in source_name or "Angers12" in source_name or "FaF_Zones_fines":
        # Note. Special case for Metz 2017 and Angers 2012: I cannot figure out the ids in the GT
        # and ZF files.
        # For Bayonne 2010, the ids are missing.
        logger.warning("Cannot read detailed zones: ids are invalid")
        detailed_zones = None
    else:
        logger.debug(f"Reading detailed zones from `{filename}`")
        detailed_zones = read_detailed_zones(filename)
    # Draw zones.
    filename = draw_zones_filename(source)
    if filename is None:
        logger.debug(f"No file with draw zones in `{source_name}`")
        draw_zones = None
    else:
        logger.debug(f"Reading draw zones from `{filename}`")
        draw_zones = read_draw_zones(filename)

    if special_locations is not None:
        # For the Angers 2022 survey, the ids in the detailed zones shapefile have 3 zeros removed
        # compared to the ids in the special locations shapefile.
        assert (
            detailed_zones is not None
        ), "Special locations are defined but there is no data on detailed zones"
        if "detailed_zone_id" not in special_locations.columns:
            special_locations = identify_detailed_zone_id(special_locations, detailed_zones)
        dz_gcd = np.gcd.reduce(detailed_zones["detailed_zone_id"].astype(int))
        sl_gcd = np.gcd.reduce(special_locations["detailed_zone_id"].astype(int))
        if dz_gcd < sl_gcd and np.log10(sl_gcd).is_integer():
            detailed_zones["detailed_zone_id"] = (
                detailed_zones["detailed_zone_id"].astype(int) * sl_gcd
            ).astype(str)

    return special_locations, detailed_zones, draw_zones


def survey_main_insee(source: str | bytes):
    return pl.scan_csv(source, separator=";").select("IDM4").first().collect().item()


def survey_name(source: str | ZipFile):
    filename = find_file(source, ".*_std_faf_men.csv", subdir="Csv", as_url=True)
    return re.match("(.*)_std_faf_men.csv", os.path.basename(filename)).group(1)


def get_files(source: str | ZipFile, name: str):
    return [
        find_file(source, f".*_std_faf_{name}.csv", subdir="Csv"),
        find_file(source, f".*_std_tel_{name}.csv", subdir="Csv"),
    ]


def households_filename(source: str | ZipFile):
    return get_files(source, "men")


def persons_filename(source: str | ZipFile):
    return get_files(source, "pers")


def trips_filename(source: str | ZipFile):
    return get_files(source, "depl")


def legs_filename(source: str | ZipFile):
    return get_files(source, "traj")


def detailed_zones_filename(source: str | ZipFile):
    return find_file(
        source,
        r".*_(ZF|Zones_Fines|Zones fines|ZInterne)(.*)?\.(TAB|shp|MIF)",
        subdir=os.path.join("Doc", "SIG"),
        as_url=True,
    )


def special_locations_filename(source: str | ZipFile):
    # Note. Basically, the regex will match all "*_GT*" or "*Gener*"" files but not the "*ZF_GT"
    # files. (In the Lyon 2015 survey, there is a "ZF_GT" file with both special locations and
    # detailed zones. As # we cannot manage this file properly we consider that all GTs are special
    # locations for Lyon.)
    return find_file(
        source,
        r"(?!.*ZF_GT).*(_GT|Gener)(.*)?\.(TAB|shp|MIF)",
        subdir=os.path.join("Doc", "SIG"),
        as_url=True,
    )


def draw_zones_filename(source: str | ZipFile):
    return find_file(
        source, r".*_DTIR(_.*)?\.(TAB|shp|MIF)", subdir=os.path.join("Doc", "SIG"), as_url=True
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
