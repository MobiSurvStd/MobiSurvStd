import os
import re

import geopandas as gpd

from mobisurvstd.cerema.survey import CeremaReader
from mobisurvstd.utils import find_file

from .zones import find_matching_column


class EMDReader(CeremaReader):
    SURVEY_TYPE = "EMD"

    def households_filenames(self) -> list[str | bytes]:
        # The filenames are usually stored in "Csv/Fichiers_Standard/[SURVEY_NAME]_std_[NAME].csv"
        # but in some cases (e.g., Strasbourg 2009, Rouen 2017) the directory "Fichiers_Standard" is
        # named based on the survey name (e.g., Rouen_2017_Standard).
        return [find_file(self.source, ".*_std_men.csv", subdir="Csv")]

    def persons_filenames(self) -> list[str | bytes]:
        return [find_file(self.source, ".*_std_pers.csv", subdir="Csv")]

    def trips_filenames(self) -> list[str | bytes]:
        return [find_file(self.source, ".*_std_depl.csv", subdir="Csv")]

    def legs_filenames(self) -> list[str | bytes]:
        return [find_file(self.source, ".*_std_traj.csv", subdir="Csv")]

    def special_locations_and_detailed_zones_filenames(self):
        # This should only match the Valenciennes 2011 survey.
        return [
            find_file(self.source, ".*zf_gt[.]mif", subdir=os.path.join("Doc", "SIG"), as_url=True)
        ]

    def detailed_zones_filenames(self):
        return [
            find_file(
                self.source,
                ".*(_zf|zones?[_ ]?fines?.*)[.](tab|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def special_locations_filenames(self):
        return [
            find_file(
                self.source,
                ".*(_gt|g.?n.?rateur.*)[.](tab|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def draw_zones_filenames(self):
        return [
            find_file(
                self.source,
                ".*(_DTIR|secteur_.*)[.](tab|shp|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def survey_name(self):
        filename = find_file(self.source, ".*_std_men.csv", subdir="Csv", as_url=True)
        return re.match("(.*)_std_men.csv", os.path.basename(filename)).group(1)

    def gt_id_columns(self):
        return [
            "gt2016f",
            "numgenerateur2011",
            "zf_gt_def",
            "num_gene2013",
            "_2017_zf",
            "numzonefine2010",
        ]

    def zf_id_from_gt_columns(self):
        return ["numzonefine2011appartenance", "zf_rattachement"]

    def gt_name_columns(self):
        return ["nom_gene", "libelle_zf", "libelle", "nom", "generateur"]

    def gt_type_columns(self):
        return ["famille", "type", "nature_generateur"]

    def zf_id_columns(self):
        return [
            "zfin2016f",
            "numzonefine2011",
            "numzonefine2010",
            "num_zf_def",
            "dfin_smart",
            "num_zf_2013",
            "_2017_zf",
            "idzfin2010",
            "zf_sec_emd2013",
            "code_sec_1",
        ]

    def zf_name_columns(self):
        return ["nom_zf_def", "nom_zf", "libelle_zf", "n_zfin2010", "libelle", "nom"]

    def dtir_id_columns(self):
        return [
            "numsecteur2011",
            "numsecteur2010",
            "secteur_emd2013",
            "dtir2010",
            "dtir_définitif",
            "secteur_ti",
            "code_secte",
            "num_secteur",
            "num_dtir",
            "dtir",
            "st",
        ]

    def dtir_name_columns(self):
        return ["nom_secteur2011", "nom_dtir"]

    def insee_id_columns(self):
        return ["cod_com", "codeinseecommune", "insee_comm", "insee_id", "numerocom", "com"]

    def select_insee_column(self, gdf: gpd.GeoDataFrame):
        # This is the standard case.
        super().select_dtir_column(gdf)
        if "insee_id" not in gdf.columns:
            # For Lille 2016, the insee_id can be read from the first 5 characters of the IRIS
            # column.
            if matching_col := find_matching_column("iris", gdf):
                gdf["insee_id"] = gdf[matching_col].str.slice(0, 5)

    def preprocess_detailed_zones(self, gdf: gpd.GeoDataFrame):
        if "Famille" in gdf.columns and "ZFIN2016F" in gdf.columns:
            # Special case for Lille 2015: 110 ZFs are also GTs (they have the same id, the GT Points
            # are within the ZF Polygons).
            # We don't want to drop these "duplicate" ZFs (because other GTs are within these ZFs).
            # So we create fake ID for them (by adding 50 to their ID).
            mask = gdf["Famille"] != ""
            gdf.loc[mask, "ZFIN2016F"] = gdf.loc[mask, "ZFIN2016F"] + 50
        return gdf
