from datetime import timedelta
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd
import polars as pl
from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.common.zones import get_coords

from .common import EMC2_MODE_MAP, MODE_MAP
from .deplacements import TripsReader
from .menages import HouseholdsReader
from .personnes import PersonsReader
from .trajets import LegsReader
from .zones import ZonesReader

LOCATION_COLUMNS = (
    ("households", ("home",)),
    ("persons", ("work", "study")),
    ("trips", ("origin", "destination")),
    ("legs", ("start", "end")),
)


class CeremaReader(HouseholdsReader, PersonsReader, TripsReader, LegsReader, ZonesReader):
    SURVEY_TYPE = ""

    def __init__(self, source: str | ZipFile):
        self.source = source
        self.special_locations = None
        self.detailed_zones = None
        self.draw_zones = None
        self.special_locations_coords = None
        self.detailed_zones_coords = None

    def source_name(self) -> str:
        return self.source.filename if isinstance(self.source, ZipFile) else self.source

    def households_filenames(self):
        raise NotImplementedError

    def persons_filenames(self):
        raise NotImplementedError

    def trips_filenames(self):
        raise NotImplementedError

    def legs_filenames(self):
        raise NotImplementedError

    def special_locations_and_detailed_zones_filenames(self):
        return [None]

    def special_locations_filenames(self):
        return [None]

    def detailed_zones_filenames(self):
        return [None]

    def draw_zones_filenames(self):
        return [None]

    def survey_name(self):
        raise NotImplementedError

    def standardize(self, skip_spatial: bool = False):
        logger.info(f"Standardizing {self.SURVEY_TYPE} survey from `{self.source_name()}`")
        if not self.validate():
            return None

        if not skip_spatial:
            self.read_spatial_data()

        self.standardize_households()
        self.standardize_cars()
        self.standardize_motorcycles()
        self.standardize_persons()
        self.standardize_trips()
        self.standardize_legs()

        self.finish()

        return clean(
            households=self.households,
            persons=self.persons,
            trips=self.trips,
            legs=self.legs,
            cars=self.cars,
            motorcycles=self.motorcycles,
            special_locations=self.special_locations,
            detailed_zones=self.detailed_zones,
            draw_zones=self.draw_zones,
            survey_type=self.SURVEY_TYPE,
            survey_name=self.survey_name(),
            main_insee=self.main_insee(),
        )

    def validate(self):
        if not all(self.households_filenames()):
            logger.error("Missing households file")
            return False
        if not all(self.persons_filenames()):
            logger.error("Missing persons file")
            return False
        if not all(self.trips_filenames()):
            logger.error("Missing trips file")
            return False
        if not all(self.legs_filenames()):
            logger.error("Missing legs file")
            return False
        return True

    def read_spatial_data(self):
        self.read_special_locations_and_detailed_zones()
        self.read_special_locations()
        self.read_detailed_zones()
        self.read_draw_zones()

        if self.detailed_zones is not None and "draw_zone_id" in self.detailed_zones.columns:
            if self.draw_zones is None:
                # The draw zones are unknown but they can be inferred from the detailed zones.
                self.draw_zones = generate_draw_zones_from_detailed_zones(self.detailed_zones)
            elif not set(self.draw_zones["draw_zone_id"]).intersection(
                set(self.detailed_zones["draw_zone_id"])
            ):
                # Special case for Bayonne 2010: the draw zones read are for the phone survey only,
                # while the detailed zones are for the face-to-face survey only.
                # We can add to the draw zones the ones from the face-to-face survey.
                face_to_face_draw_zones = generate_draw_zones_from_detailed_zones(
                    self.detailed_zones
                )
                self.draw_zones = pd.concat([self.draw_zones, face_to_face_draw_zones])
        if self.special_locations is not None:
            self.special_locations_coords = get_coords(self.special_locations, "special_location")
        if self.detailed_zones is not None:
            self.detailed_zones_coords = get_coords(self.detailed_zones, "detailed_zone")

    def get_mode_map(self):
        """The mode classes have changed with the EMC2 surveys so there are two different mode maps
        that can be used to map categories to MobiSurvStd modes.
        """
        if self.SURVEY_TYPE == "EMC2":
            return EMC2_MODE_MAP
        else:
            return MODE_MAP

    def get_household_index_cols(self):
        """Returns the list of columns that must be used to uniquely define each household.
        Note that columns "ZFM" is usually not required (i.e., households are uniquely defined just
        with "ECH" and "STM") but in some cases it is required.
        """
        cols = ["ECH", "STM", "ZFM"]
        if self.SURVEY_TYPE == "EMC2":
            return ["METH"] + cols
        else:
            return cols

    def get_person_index_cols(self):
        cols = ["ECH", "STP", "ZFP", "PER"]
        if self.SURVEY_TYPE == "EMC2":
            return ["PMET"] + cols
        else:
            return cols

    def get_household_index_cols_from_persons(self):
        cols = {"ECH": "ECH", "STM": "STP", "ZFM": "ZFP"}
        if self.SURVEY_TYPE == "EMC2":
            return {"METH": "PMET"} | cols
        else:
            return cols

    def get_trip_index_cols(self):
        cols = ["ECH", "STD", "ZFD", "PER", "NDEP"]
        if self.SURVEY_TYPE == "EMC2":
            return ["DMET"] + cols
        else:
            return cols

    def get_person_index_cols_from_trips(self):
        cols = {"ECH": "ECH", "STP": "STD", "ZFP": "ZFD", "PER": "PER"}
        if self.SURVEY_TYPE == "EMC2":
            return {"PMET": "DMET"} | cols
        else:
            return cols

    def get_leg_index_cols(self):
        cols = ["ECH", "STT", "ZFT", "PER", "NDEP"]
        if self.SURVEY_TYPE == "EMC2":
            return ["TMET"] + cols
        else:
            return cols

    def get_trip_index_cols_from_legs(self):
        cols = {"ECH": "ECH", "STD": "STT", "ZFD": "ZFT", "PER": "PER", "NDEP": "NDEP"}
        if self.SURVEY_TYPE == "EMC2":
            return {"DMET": "TMET"} | cols
        else:
            return cols

    def clean_detailed_zone(self, col: str):
        # Usually, the detailed zone ids in the CSVs have two leading zeros that need to be removed
        # to match the ids in the spatial files.
        return (
            pl.when(pl.col(col).str.slice(0, 2) == "00")
            .then(pl.col(col).str.slice(2))
            .otherwise(col)
        )

    def finish(self):
        self.add_survey_dates()
        self.fix_main_mode()
        self.fix_special_locations()

    def add_survey_dates(self):
        # Survey date is specified at the person-level, we create here the household-level
        # `interview_date`.
        household_dates = (
            self.persons.group_by("household_id").agg(pl.col("trip_date").first()).collect()
        )
        self.households = self.households.join(
            household_dates.lazy(), on="household_id", how="left", coalesce=True
        ).with_columns(interview_date=pl.col("trip_date") + timedelta(days=1))

    def fix_main_mode(self):
        # Special case for Douai 2012: The motorcycle trips have "motorcycle" leg but their
        # `main_mode` is set to "car_driver".
        invalid_trips = (
            self.legs.select("trip_id", "mode_group")
            .join(self.trips.select("trip_id", "main_mode_group"), on="trip_id")
            .filter(pl.col("mode_group").eq(pl.col("main_mode_group")).any().over("trip_id").not_())
            .select("trip_id")
            .collect()
            .to_series()
            .unique()
        )
        n = len(invalid_trips)
        if n > 0:
            fixed_main_modes = (
                self.legs.filter(
                    pl.col("trip_id").is_in(invalid_trips), pl.col("mode_group") != "walking"
                )
                .group_by("trip_id", "mode")
                .agg(
                    dist=pl.col("leg_euclidean_distance_km").sum(),
                    mode_group=pl.col("mode_group").first(),
                )
                .sort("trip_id", "dist")
                .group_by("trip_id")
                .agg(main_mode=pl.col("mode").last(), main_mode_group=pl.col("mode_group").last())
                .collect()
            )
            logger.warning(
                f"For {n} trips, `main_mode_group` value does not appear in any legs'`mode_group`. "
                f"The `main_mode_group` value is automatically fixed."
            )
            self.trips = (
                self.trips.with_columns(
                    main_mode_group=pl.when(pl.col("trip_id").is_in(invalid_trips)).then(
                        pl.col("trip_id").replace_strict(
                            fixed_main_modes["trip_id"],
                            fixed_main_modes["main_mode_group"],
                            default=None,
                        )
                    ),
                    main_mode=pl.when(pl.col("trip_id").is_in(invalid_trips)).then(
                        pl.col("trip_id").replace_strict(
                            fixed_main_modes["trip_id"], fixed_main_modes["main_mode"], default=None
                        )
                    ),
                )
                .collect()
                .lazy()
            )

    def fix_special_locations(self):
        # Fix the special locations which are being used as detailed zones.
        if self.special_locations is not None:
            assert self.detailed_zones is not None, (
                "Special locations are defined but there is no data on detailed zones"
            )
            special_locations_ids = set(self.special_locations["special_location_id"])
            detailed_zones_ids = set(self.detailed_zones["detailed_zone_id"])
            assert not special_locations_ids.intersection(detailed_zones_ids), (
                "Special locations and detailed zones have common ids"
            )
            assert len(special_locations_ids) == len(self.special_locations), (
                "Special locations ids are not unique"
            )
            assert len(detailed_zones_ids) == len(self.detailed_zones), (
                "Detailed zones ids are not unique"
            )
            if "detailed_zone_id" not in self.special_locations.columns:
                self.identify_detailed_zone_ids()
            self.apply_function_to_location_columns(
                lambda df, col: fix_locations(df, col, self.special_locations)
            )
        elif self.detailed_zones is not None and self.SURVEY_TYPE == "EDGT":
            # Only Angers 2012 and Bayonne 2010 should match this case.
            # For Bayonne 2010, there is no GT so there is nothing to do.
            # For Angers 2012, the GT ids all have 5, 6, 7, 8, or 9 as the second digit.
            assert (self.detailed_zones["detailed_zone_id"].str.slice(-2, -1).astype(int) < 5).all()
            self.apply_function_to_location_columns(
                lambda df, col: fix_locations_for_angers_2012(df, col, self.draw_zones)
            )

    def apply_function_to_location_columns(self, func):
        """Applies the function `func` to all the location columns (households' `home_*`, persons'
        `work_*`, etc.

        The function takes two arguments: the DataFrame and the column prefix.
        """
        for df_name, prefixes in LOCATION_COLUMNS:
            for prefix in prefixes:
                # Get "self.df_name".
                df = getattr(self, df_name)
                # Set "self.df_name" to "func(self.df_name)".
                setattr(self, df_name, func(df, prefix))

    def identify_detailed_zone_ids(self):
        """Adds `detailed_zone_id` column to special_locations by finding the detailed zone in which
        the special location falls.
        """
        orig_crs = self.special_locations.crs
        self.special_locations.to_crs(self.detailed_zones.crs, inplace=True)
        cols = ["geometry", "detailed_zone_id"]
        for col in ("draw_zone_id", "insee_id"):
            if col in self.detailed_zones.columns and col not in self.special_locations.columns:
                cols.append(col)
        self.special_locations = self.special_locations.sjoin_nearest(
            self.detailed_zones[cols], how="left", distance_col="dist"
        )
        mask = self.special_locations["dist"] > 0.0
        if mask.any():
            n = mask.sum()
            max_dist = self.special_locations["dist"].max()
            logger.warning(
                f"{n} special locations are not within a detailed zone (maximum distance: {max_dist:.2f}m)"
            )
        self.special_locations.drop(columns=["index_right", "dist"], inplace=True)
        self.special_locations.drop_duplicates(subset=["special_location_id"], inplace=True)
        self.special_locations.to_crs(orig_crs, inplace=True)


def fix_locations(lf: pl.LazyFrame, col: str, special_locations: gpd.GeoDataFrame):
    """Fix the special locations and detailed zones columns."""
    mask = (
        pl.col(f"{col}_detailed_zone")
        .is_in(special_locations["special_location_id"].to_list())
        .not_()
    )
    lf = lf.with_columns(
        # When the ZF is an actual ZF
        pl.when(mask)
        # Then use that ZF
        .then(f"{col}_detailed_zone")
        # Otherwise use the ZF corresponding to that GT.
        .otherwise(
            pl.col(f"{col}_detailed_zone").replace_strict(
                pl.from_pandas(special_locations["special_location_id"]),
                pl.from_pandas(special_locations["detailed_zone_id"]),
                default=None,
            )
        )
        .alias(f"{col}_detailed_zone"),
        # When the ZF is an actual ZF
        pl.when(mask)
        # Then the GT is null
        .then(pl.lit(None))
        # Otherwise use that GT as GT.
        .otherwise(f"{col}_detailed_zone")
        .alias(f"{col}_special_location"),
    )
    return lf.collect().lazy()


def fix_locations_for_angers_2012(df: pl.LazyFrame, col: str, draw_zones: gpd.GeoDataFrame):
    # The ZF id is actually a GT id when the penultimate digit is 5+ AND when this is not an
    # external zone (i.e., the draw zone is known).
    st_ids = set(draw_zones["draw_zone_id"].astype(int))
    mask = pl.col(f"{col}_detailed_zone").cast(pl.String).str.slice(-2, 1).cast(pl.UInt8).ge(
        5
    ) & pl.col(f"{col}_draw_zone").cast(pl.Int64).is_in(st_ids)
    df = df.with_columns(
        # When the ZF is actually a GT.
        pl.when(mask)
        # Then the actual ZF is unknown.
        .then(None)
        # Otherwise use the ZF.
        .otherwise(f"{col}_detailed_zone")
        .alias(f"{col}_detailed_zone"),
        # When the ZF is actually a GT.
        pl.when(mask)
        # Then use that GT.
        .then(f"{col}_detailed_zone")
        # Otherwise there is no GT.
        .otherwise(None)
        .alias(f"{col}_special_location"),
    )
    return df


def generate_draw_zones_from_detailed_zones(detailed_zones: gpd.GeoDataFrame):
    logger.debug("Inferring draw zones from detailed zones")
    draw_zones = detailed_zones[["draw_zone_id", "geometry"]].dissolve(
        "draw_zone_id", as_index=False
    )
    # Try to clean the disolve.
    draw_zones.geometry = draw_zones.geometry.buffer(10).buffer(-10)
    return draw_zones
