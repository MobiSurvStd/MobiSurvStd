import os
import re

import geopandas as gpd

from mobisurvstd.cerema.survey import CeremaReader
from mobisurvstd.utils import find_file

from .zones import find_matching_column


class EDVMReader(CeremaReader):
    SURVEY_TYPE = "EDVM"

    def households_filenames(self) -> list[str | bytes]:
        # The filenames are usually stored in "Csv/Fichiers_Standard/[SURVEY_NAME]_std_[NAME].csv"
        # but in some cases (e.g., Ajaccio 2017) the directory "Fichiers_Standard" is # named based
        # on the survey name (e.g., Ajaccio_2017_Standard).
        return [find_file(self.source, ".*_std_men.csv", subdir="Csv")]

    def persons_filenames(self) -> list[str | bytes]:
        return [find_file(self.source, ".*_std_pers.csv", subdir="Csv")]

    def trips_filenames(self) -> list[str | bytes]:
        return [find_file(self.source, ".*_std_depl.csv", subdir="Csv")]

    def legs_filenames(self) -> list[str | bytes]:
        return [find_file(self.source, ".*_std_traj.csv", subdir="Csv")]

    def special_locations_and_detailed_zones_filenames(self):
        # This should only match the Beauvais 2011 survey.
        return [
            find_file(
                self.source,
                ".*beauvais.*_dfin[.](tab|shp|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def detailed_zones_filenames(self):
        return [
            find_file(
                self.source,
                ".*(_zf_.*|_zf|zones?[_ ]?fines?.*|_dfin)[.](tab|shp|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def special_locations_filenames(self):
        return [
            find_file(
                self.source,
                ".*(_gt_.*|_gt|_pgt|_pg|g.?n.?rateur.*)[.](tab|shp|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def draw_zones_filenames(self):
        return [
            find_file(
                self.source,
                ".*_DTIR[.](tab|shp|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def survey_name(self):
        filename = find_file(self.source, ".*_std_men.csv", subdir="Csv", as_url=True)
        return re.match("(.*)_std_men.csv", os.path.basename(filename)).group(1)

    def gt_id_columns(self):
        return [
            "code_pgt",
            "pgt",
            "code_gt",
            "code_pole_gen",
            "dfin_smart",
            "numgener_1",
            "num_gt",
            "num_gene2013",
            "num_gene",
            "num_zone_fine",
            "num_zf",
            "codage",
            "numerozf",
            "zonefine",
            "zone_fine",
            "zf",
        ]

    def zf_id_from_gt_columns(self):
        return [
            "zf_2015",
            "zf_rattachement",
            "num_zf_c",
            "code_zone_fine",
            "numero_zone_fine",
            "numerozf",
            "zone_fine",
            "zf",
        ]

    def gt_name_columns(self):
        return [
            "lib_pgt",
            "name_1",
            "nom_generateur_trafic",
            "nom_generateur",
            "nom_gene",
            "nom_gt",
            "nompgt",
            "nomgt_zf",
            "nom_court",
            "nom",
            "nom_zf",
        ]

    def gt_type_columns(self):
        return [
            "descriptio",  # Typo is on purpose.
            "nature_generateur",
            "typepgt",
            "typegt",
            "typologie_gt",
            "lib_theme",
            "nature_zone_fine",
            "type",
        ]

    def zf_id_columns(self):
        return [
            "num_zf_2013",
            "zf_2015",
            "code_zone_fine",
            "dfin_smart",
            "id_dfin",
            "dfin",
            "code_zf",
            "zf_format",
            "id_zf",
            "num_zf",
            "numerozf",
            "id_zfine",
            "zone_f",
            "zone_fine",
            "zf",
            "zone",
        ]

    def zf_name_columns(self):
        return [
            "lib_dfin",
            "lib_zone_f",
            "libfin",
            "zf_lib",
            "nomgt_zf",
            "nom_zfine",
            "nom_zf",
            "nom_iris",
            "nom",
        ]

    def dtir_id_columns(self):
        return [
            "id_dtir",
            "num_dtir",
            "numerodtir",
            "dtir",
            "code_secteur_de_tirage",
            "numtirage",
            "secteur_emd2012",
            "num_secteur",
            "num_secteurs",
            "numero_secteur",
            "numsec",
            "secteur",
            "secteurs",
            "sec",
        ]

    def dtir_name_columns(self):
        return ["nom_dtir", "nom_dtir_enq", "nom_secteurs", "nom_d30"]

    def insee_id_columns(self):
        return [
            "code_insee",
            "insee_commune",
            "insee_comm",
            "code_com",
            "num_com",
            "depcom",
            "id_com",
            "commune",
            "cog",
        ]

    def select_gt_column(self, gdf: gpd.GeoDataFrame):
        # For Albi 2011, Angoulème 2012 and La Rochelle 2011, the GT id can be computed by summing
        # two columns.
        pairs = (
            ("Secteur", "ZFPP"),  # Albi 2011.
            ("Secteur", "ZF_PG"),  # Angoulème 2012.
            ("Secteurs", "ZF311"),  # La Rochelle 2011.
        )
        for sec_col, gt_num_col in pairs:
            if sec_col in gdf.columns and gt_num_col in gdf.columns:
                # The `gt_num_col` is cast to int then str to handle the Angoulème 2012 survey where the
                # column is of dtype float.
                gdf["special_location_id"] = gdf[sec_col] + gdf[gt_num_col].astype(int).astype(str)
                break
        # Normal case. Find the GT id column by name.
        super().select_gt_column(gdf)

    def select_zf_column(self, gdf: gpd.GeoDataFrame):
        # For Albi 2011, Angoulème 2012 and La Rochelle 2011, the ZF id can be computed by summing
        # two columns.
        pairs = (
            ("Sec", "Z_Fines"),  # Albi 2011.
            ("Secteur", "Zone_Fine"),  # Angoulème 2012.
            ("NumSec", "Zone_F"),  # La Rochelle 2011.
        )
        for sec_col, zf_num_col in pairs:
            if sec_col in gdf.columns and zf_num_col in gdf.columns:
                gdf["detailed_zone_id"] = gdf[sec_col] + gdf[zf_num_col]
                break
        # Normal case. Find the ZF id column by name.
        super().select_zf_column(gdf)
        if "detailed_zone_id" not in gdf.columns:
            # Special case for Les Sables d'Olonnes 2011: Two zeros must be added before the last
            # number.
            if "codage" in gdf.columns:
                gdf["detailed_zone_id"] = gdf["codage"].str.replace(r"(\d)$", r"00\1", regex=True)

    def select_dtir_column(self, gdf: gpd.GeoDataFrame):
        # This is the standard case.
        super().select_dtir_column(gdf)
        if "draw_zone_id" not in gdf.columns:
            # For Creil 2017, La-Roche-sur-Yon 2013, Le Creusot 2012, and Les Sables d'Olonnes 2011,
            # the draw_zone_id can be read from the first 3 characters of the ZF or GT column.
            for dtir_col in ("zone_fine", "codage", "num_zf", "code_pole_gen"):
                if matching_col := find_matching_column(dtir_col, gdf):
                    gdf["draw_zone_id"] = gdf[matching_col].str.slice(0, 3)
            # For Saint-Louis 2011, the draw_zone_id can be read from the first 4 characters of the
            # ZF column.
            if matching_col := find_matching_column("zone", gdf):
                gdf["draw_zone_id"] = gdf[matching_col].str.slice(0, 4)

    def select_insee_column(self, gdf: gpd.GeoDataFrame):
        # This is the standard case.
        super().select_insee_column(gdf)
        if "insee_id" not in gdf.columns:
            # For Angoulème 2012, the insee_id can be read from the first 5 characters of the
            # DcomIris column.
            if matching_col := find_matching_column("dcomiris", gdf):
                gdf["insee_id"] = gdf[matching_col].str.slice(0, 5)

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

    def postprocess_special_locations_and_detailed_zones(
        self, zfs: gpd.GeoDataFrame, gts: gpd.GeoDataFrame
    ):
        # This function should only be call for Beauvais 2011.
        assert "detailed_zone_id" not in gts.columns
        # The corresponding ZF is the GT id with the last digit replaced by 0.
        gts["detailed_zone_id"] = gts["special_location_id"].str.replace(r"\d$", "0", regex=True)
        return zfs, gts
