import re
from zipfile import ZipFile

import geopandas as gpd
import polars as pl
from loguru import logger

from .common import EMC2_MODE_MAP, MODE_MAP, NANTES_MODE_MAP


class CeremaReader:
    SURVEY_TYPE = ""
    source: str | ZipFile
    households: pl.LazyFrame
    persons: pl.LazyFrame
    trips: pl.LazyFrame
    legs: pl.LazyFrame
    cars: pl.LazyFrame
    motorcycles: pl.LazyFrame
    special_locations: gpd.GeoDataFrame | None
    detailed_zones: gpd.GeoDataFrame | None
    draw_zones: gpd.GeoDataFrame | None
    special_locations_coords: pl.DataFrame | None
    detailed_zones_coords: pl.DataFrame | None

    def __init__(self, source: str | ZipFile):
        self.source = source
        self.special_locations = None
        self.detailed_zones = None
        self.draw_zones = None
        self.special_locations_coords = None
        self.detailed_zones_coords = None

    def source_name(self) -> str:
        if isinstance(self.source, ZipFile):
            return self.source.filename or "unknown zipfile"
        else:
            return self.source

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

    def survey_year(self):
        """Extracts the year at which the survey was conducted from the survey name."""
        name = self.survey_name()
        matches = re.findall(r"_(\d{4})$", name)
        return int(matches[0]) if matches else None

    def validate(self):
        is_valid = True
        households_filenames = self.households_filenames()
        if not all(households_filenames):
            err = next(filter(lambda f: not f, households_filenames))
            logger.error(f"Missing households file: {err}")
            is_valid = False
        persons_filenames = self.persons_filenames()
        if not all(persons_filenames):
            err = next(filter(lambda f: not f, persons_filenames))
            logger.error(f"Missing persons file: {err}")
            is_valid = False
        trips_filenames = self.trips_filenames()
        if not all(trips_filenames):
            err = next(filter(lambda f: not f, trips_filenames))
            logger.error(f"Missing trips file: {err}")
            is_valid = False
        legs_filenames = self.legs_filenames()
        if not all(legs_filenames):
            err = next(filter(lambda f: not f, legs_filenames))
            logger.error(f"Missing legs file: {err}")
            is_valid = False
        return is_valid

    def get_mode_map(self):
        """The mode classes have changed with the EMC2 surveys so there are two different mode maps
        that can be used to map categories to MobiSurvStd modes.
        """
        if self.SURVEY_TYPE == "EMC2":
            return EMC2_MODE_MAP
        elif self.SURVEY_TYPE == "EDGT-opendata":
            return NANTES_MODE_MAP
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
