import io

import pandas as pd
import polars as pl

from mobisurvstd.utils import find_file

from .deplacements import SCHEMA as TRIP_SCHEMA
from .menages import SCHEMA as HOUSEHOLD_SCHEMA
from .personnes import SCHEMA as PERSON_SCHEMA
from .survey import CeremaReader
from .trajets import SCHEMA as LEG_SCHEMA

# The anonimized open-data format for Nantes uses a fixed-width text format.
# Implementation draws inspiration from the eqasim implementation of Valentin Le Bescond.
HOUSEHOLD_FORMAT = [
    # position, size, name
    (1, 1, "MP1"),
    (2, 6, "MUnused6"),
    (8, 3, "STM"),
    (8, 6, "ZFM"),
    (14, 4, "ECH"),
    (18, 1, "M1"),
    (19, 1, "M2"),
    (20, 1, "M5"),
    (21, 1, "M6"),
    (22, 1, "M8A"),
    (23, 4, "M9A"),
    (27, 2, "M10A"),
    (29, 1, "M8B"),
    (30, 4, "M9B"),
    (34, 2, "M10B"),
    (36, 1, "M8C"),
    (37, 4, "M9C"),
    (41, 2, "M10C"),
    (43, 1, "M8D"),
    (44, 4, "M9D"),
    (48, 2, "M10D"),
    (50, 1, "M14"),
    (51, 2, "M21"),
    (53, 4, "MUnused1"),
    (57, 2, "MUnused2"),
    (59, 2, "MUnused3"),
    (61, 5, "MUnused4"),
    (66, 1, "MUnused5"),
    (67, 8, "COE0"),
    (75, 1, "MFIN"),
]

PERSON_FORMAT = [
    # position, size, name
    (1, 1, "PP1"),
    (2, 3, "STP"),
    (2, 6, "ZFP"),
    (8, 4, "ECH"),
    (12, 2, "PER"),
    (14, 1, "PENQ"),
    (15, 1, "JOUR"),
    (16, 1, "PUnused1"),
    (17, 1, "P2"),
    (18, 1, "P3"),
    (19, 2, "P4"),
    (21, 1, "P7"),
    (22, 1, "P8"),
    (23, 1, "P9"),
    (24, 1, "PCSC"),
    (25, 1, "P14"),
    (26, 6, "P15"),
    (32, 1, "P16"),
    (33, 1, "P17"),
    (34, 1, "P18"),
    (35, 1, "P19"),
    (36, 1, "P20"),
    (37, 1, "P21"),
    (38, 1, "P22"),
    (39, 1, "P23"),
    (40, 1, "P24"),
    (41, 1, "P25"),
    (42, 1, "P26"),
    (43, 1, "PUnused2"),
    (44, 1, "PUnused3"),
    (45, 1, "PUnused4"),
    (46, 6, "DP15"),
    (52, 8, "COE1"),
    (60, 8, "COEP"),
    (68, 1, "PFIN"),
]

TRIP_FORMAT = [
    (1, 1, "DP1"),
    (2, 3, "STD"),
    (2, 6, "ZFD"),
    (8, 4, "ECH"),
    (12, 2, "PER"),
    (14, 2, "NDEP"),
    (16, 2, "D2A"),
    (18, 2, "D2B"),
    (20, 6, "D3"),
    (26, 4, "D4"),
    (30, 2, "D5A"),
    (32, 2, "D5B"),
    (34, 2, "D6"),
    (36, 6, "D7"),
    (42, 4, "D8"),
    (46, 3, "D9"),
    (49, 1, "D10"),
    (50, 2, "MODP"),
    (52, 2, "DUnused1"),
    (54, 8, "D11"),
    (62, 8, "D12"),
    (70, 8, "DUnused2"),
    (78, 1, "DFIN"),
]

LEG_FORMAT = [
    (1, 1, "TP1"),
    (2, 3, "STT"),
    (2, 6, "ZFT"),
    (8, 4, "ECH"),
    (12, 2, "PER"),
    (14, 2, "NDEP"),
    (16, 1, "T1"),
    (17, 2, "T2"),
    (19, 2, "T3"),
    (21, 6, "T4"),
    (27, 6, "T5"),
    (33, 2, "T6"),
    (35, 1, "T7"),
    (36, 1, "T8"),
    (37, 1, "T8A"),
    (38, 1, "T9"),
    (39, 1, "T10"),
    (40, 2, "T11"),
    (42, 8, "T12"),
    (50, 8, "T13"),
    (58, 8, "TDIP"),
    (66, 8, "TUnused1"),
    (74, 8, "TUnused2"),
    (82, 1, "TFIN"),
]


class OpenDataReader(CeremaReader):
    SURVEY_TYPE = "EDGT-opendata"

    def households_filenames(self):
        return [find_file(self.source, ".*_EDGT_44_MENAGE_FAF_TEL_.*.txt")]

    def persons_filenames(self):
        return [find_file(self.source, ".*_EDGT_44_PERSO_FAF_TEL_.*.txt")]

    def trips_filenames(self):
        return [find_file(self.source, ".*_EDGT_44_DEPLA_FAF_TEL_.*.txt")]

    def legs_filenames(self):
        return [find_file(self.source, ".*_EDGT_44_TRAJET_FAF_TEL_.*.txt")]

    def survey_name(self):
        return "nantes_2015_opendata"

    def main_insee(self):
        return "44109"

    def scan_households(self):
        lf = scan_fwf(self.households_filenames()[0], HOUSEHOLD_FORMAT, HOUSEHOLD_SCHEMA)
        # Column METH / IDM2 does not exist.
        lf = lf.with_columns(METH=pl.lit(None, dtype=pl.UInt8))
        lf = lf.sort(self.get_household_index_cols())
        return lf

    def scan_persons(self):
        lf = scan_fwf(self.persons_filenames()[0], PERSON_FORMAT, PERSON_SCHEMA)
        # Column METH / IDM2 does not exist.
        lf = lf.with_columns(METH=pl.lit(None, dtype=pl.UInt8))
        lf = lf.sort(self.get_person_index_cols())
        return lf

    def scan_trips(self):
        lf = scan_fwf(self.trips_filenames()[0], TRIP_FORMAT, TRIP_SCHEMA)
        # Column METH / IDM2 does not exist.
        lf = lf.with_columns(METH=pl.lit(None, dtype=pl.UInt8))
        lf = lf.sort(self.get_trip_index_cols())
        return lf

    def scan_legs(self):
        lf = scan_fwf(self.legs_filenames()[0], LEG_FORMAT, LEG_SCHEMA)
        # Column METH / IDM2 does not exist.
        lf = lf.with_columns(METH=pl.lit(None, dtype=pl.UInt8))
        lf = lf.sort(self.get_leg_index_cols())
        return lf


def scan_fwf(
    f: str | io.BytesIO,
    format: list[tuple[int, int, str]],
    schema: dict[str, pl.DataType],
):
    # Decrease `start` by 1 because pandas starts counting at 0 but the survey document starts
    # counting at 1.
    colspecs = [(start - 1, start - 1 + length) for start, length, _ in format]
    names = [name for _, _, name in format]
    df_pd = pd.read_fwf(f, colspecs=colspecs, dtype_backend="pyarrow", names=names)
    df = pl.from_pandas(df_pd, schema_overrides=schema)
    # Add missing columns.
    for col, dtype in schema.items():
        if col not in df.columns:
            df = df.with_columns(pl.lit(None, dtype=dtype).alias(col))
    return df.lazy()
