import os
import re

import geopandas as gpd

from mobisurvstd.cerema.survey import CeremaReader
from mobisurvstd.utils import find_file

from .zones import find_matching_column


class EMC2Reader(CeremaReader):
    SURVEY_TYPE = "EMC2"

    def households_filenames(self) -> list[str | bytes]:
        return [
            find_file(
                self.source, ".*_std_men.csv", subdir=os.path.join("Csv", "Fichiers_Standard")
            )
        ]

    def persons_filenames(self) -> list[str | bytes]:
        return [
            find_file(
                self.source, ".*_std_pers.csv", subdir=os.path.join("Csv", "Fichiers_Standard")
            )
        ]

    def trips_filenames(self) -> list[str | bytes]:
        return [
            find_file(
                self.source, ".*_std_depl.csv", subdir=os.path.join("Csv", "Fichiers_Standard")
            )
        ]

    def legs_filenames(self) -> list[str | bytes]:
        return [
            find_file(
                self.source, ".*_std_traj.csv", subdir=os.path.join("Csv", "Fichiers_Standard")
            )
        ]

    def detailed_zones_filenames(self):
        return [
            find_file(
                self.source,
                r".*_ZF(_.*)?\.(TAB|shp)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def special_locations_filenames(self):
        return [
            find_file(
                self.source,
                r".*_GT(_.*)?\.(TAB|shp)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def draw_zones_filenames(self):
        return [
            find_file(
                self.source,
                r".*_DTIR(_.*)?\.(TAB|shp)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def survey_name(self):
        filename = find_file(
            self.source,
            ".*_std_men.csv",
            subdir=os.path.join("Csv", "Fichiers_Standard"),
            as_url=True,
        )
        return re.match("(.*)_std_men.csv", os.path.basename(filename)).group(1)

    def gt_id_columns(self):
        return ["zf_160", "zf_fusion", "codegt", "zf", "num_gt"]

    def zf_id_from_gt_columns(self):
        return ["zfrat_f", "num_zf_rat", "cd_zf", "num_zf_19", "zf_rattach", "zfrat"]

    def gt_name_columns(self):
        return ["nom_gt", "nom_gen", "nom_genera", "libelle", "nom", "rem"]

    def gt_type_columns(self):
        # Note that Bouzonville 2019 has some GT type data in MACRO but the MACRO column represents
        # something else in the other surveys so it is not never.
        return ["nature", "nom_typo", "theme_gt", "type"]

    def zf_id_columns(self):
        return ["zf_fusion", "zf_160", "zf", "num_zf"]

    def zf_name_columns(self):
        return ["zf_nom", "nom_zf", "lib_zf", "libelle", "rem"]

    def dtir_id_columns(self):
        return ["dtir_160", "codsect", "ztir", "num_dtir_f", "num_dtir", "dtir"]

    def dtir_name_columns(self):
        return ["nomdtir", "nom_dtir"]

    def insee_id_columns(self):
        return ["insee_com", "insee_commune", "insee_gen", "insee", "code_com", "num_com"]

    def select_dtir_column(self, gdf: gpd.GeoDataFrame):
        # This is the standard case.
        super().select_dtir_column(gdf)
        if "draw_zone_id" not in gdf.columns:
            # For many surveys, the draw_zone_id can be read from the first 3 characters of the ZF
            # column.
            # For Rennes 2018, only the first 2 characters must be read.
            if "INSEE" in gdf.columns and gdf.loc[0, "INSEE"] == "35225":
                gdf["draw_zone_id"] = gdf["ZFRAT"].str.slice(0, 2)
            else:
                for dtir_col in ("zfrat", "zf"):
                    if matching_col := find_matching_column(dtir_col, gdf):
                        gdf["draw_zone_id"] = gdf[matching_col].str.slice(0, 3)

    def select_zf_column(self, gdf: gpd.GeoDataFrame):
        # For Angers 2022, three trailing zeros need to be added to the ZF id column.
        if "COD_ZF" in gdf.columns:
            gdf["detailed_zone_id"] = gdf["COD_ZF"] + "000"
        # Normal case. Find the ZF id column by name.
        super().select_zf_column(gdf)

    def select_gt_column(self, gdf: gpd.GeoDataFrame):
        # For Bordeaux 2021, the correspond ZF id column can be read from the GT id column (ZF_160),
        # with the three last characters replaced by zeros.
        # We create the ZFRAT column now that will be read in the `select_zf_from_gt_column`
        # because the ZF_160 will be automatically dropped by the call to `select_gt_column`.
        if "ZF_160" in gdf.columns:
            gdf["ZFRAT"] = gdf["ZF_160"].str.slice(0, -3) + "000"
        super().select_gt_column(gdf)

    def select_zf_from_gt_column(self, gdf: gpd.GeoDataFrame):
        # For Albi 2011 and Angoulème 2012, the ZF id can be computed by summing two columns.
        pairs = (
            ("Secteur", "ZF149"),  # Albi 2011.
            ("Secteur", "Zone_Fine"),  # Angoulème 2012.
        )
        for sec_col, zf_num_col in pairs:
            if sec_col in gdf.columns and zf_num_col in gdf.columns:
                gdf["detailed_zone_id"] = gdf[sec_col] + gdf[zf_num_col]
                break
        else:
            # Special case for Saintes 2016.
            if "Pgt" in gdf.columns:
                gdf["detailed_zone_id"] = gdf["Pgt"].astype(int) // 10 * 10
        # Normal case. Find the ZF id column by name.
        super().select_zf_from_gt_column(gdf)
