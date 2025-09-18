import os
import re
from zipfile import ZipFile

import geopandas as gpd

from mobisurvstd.utils import find_file

from .survey import CeremaReader
from .zones import find_matching_column


class EDGTReader(CeremaReader):
    SURVEY_TYPE = "EDGT"

    def households_filenames(self):
        return get_files(self.source, "men")

    def persons_filenames(self):
        return get_files(self.source, "pers")

    def trips_filenames(self):
        return get_files(self.source, "depl")

    def legs_filenames(self):
        return get_files(self.source, "traj")

    def special_locations_and_detailed_zones_filenames(self):
        # This should match the Amiens 2010, Clermont-Ferrand 2012, and Lyon 2015 surveys.
        subdir = os.path.join("Doc", "SIG")
        faf_filename = find_file(
            self.source, ".*_faf_d.?coupagefin[.](tab|shp|mif)", subdir=subdir, as_url=True
        )
        tel_filename = find_file(
            self.source, ".*_tel_d.?coupagefin[.](tab|shp|mif)", subdir=subdir, as_url=True
        )
        if faf_filename is not None and tel_filename is not None:
            # Amiens 2010 has two files.
            return [faf_filename, tel_filename]
        else:
            return [
                find_file(
                    self.source,
                    ".*(_zf_gt|zinterne_gen_.*)[.](tab|shp|mif)",
                    subdir=subdir,
                    as_url=True,
                )
            ]

    def special_locations_filenames(self):
        subdir = os.path.join("Doc", "SIG")
        faf_filename = find_file(
            self.source, ".*_faf_.*g.?n.?rateur.*[.](tab|shp|mif)", subdir=subdir, as_url=True
        )
        tel_filename = find_file(
            self.source, ".*_tel_.*g.?n.?rateur.*[.](tab|shp|mif)", subdir=subdir, as_url=True
        )
        if faf_filename is not None and tel_filename is not None:
            # Saint-Quentin-en-Yvelines has two files, for phone and face-to-face surveys.
            return [faf_filename, tel_filename]
        else:
            return [
                find_file(
                    self.source,
                    ".*(_gt_.*|_gt|g.?n.?rateur.*)[.](tab|shp|mif)",
                    subdir=subdir,
                    as_url=True,
                )
            ]

    def detailed_zones_filenames(self):
        subdir = os.path.join("Doc", "SIG")
        faf_filename = find_file(
            self.source, ".*_faf_zones_fines[.](tab|shp|mif)", subdir=subdir, as_url=True
        )
        tel_filename = find_file(
            self.source, ".*_tel_zones_fines[.](tab|shp|mif)", subdir=subdir, as_url=True
        )
        if faf_filename is not None and tel_filename is not None:
            # Nice 2009 and Saint-Quentin-en-Yvelines have two files, for phone and face-to-face
            # surveys.
            return [faf_filename, tel_filename]
        else:
            return [
                find_file(
                    self.source,
                    ".*(_zf|_zf_.*|zf08_.*|(?<!tel_)zones[_ ]fines)[.](tab|shp|mif)",
                    subdir=subdir,
                    as_url=True,
                )
            ]

    def draw_zones_filenames(self):
        return [
            find_file(
                self.source,
                ".*(_dtir|_secteurstirage)[.](tab|shp|mif)",
                subdir=os.path.join("Doc", "SIG"),
                as_url=True,
            )
        ]

    def survey_name(self):
        filename = find_file(self.source, ".*_std_faf_men.csv", subdir="Csv", as_url=True)
        return re.match("(.*)_std_faf_men.csv", os.path.basename(filename)).group(1)

    def gt_id_columns(self):
        return [
            "pôle_génér",  # Thanks Saint-Quentin-en-Yvelines for this monstrosity.
            "num_generateurs08",
            "num_generateur08",
            "num_gene2013",
            "num_gene_2015",
            "cod_pgt_2",
            "zone_fine_gt",
            "zf2015_nouveau_codage",
            "code_gt",
            "gt",
            "zonefine",
            "dfin",
            "zf",
            "num_zone_fine",
            "num_zf",
            "code",
        ]

    def zf_id_from_gt_columns(self):
        return ["zf_rattachement", "rattacheme", "num_zf_2015", "zone_fine", "z_fine", "zf"]

    def gt_name_columns(self):
        return [
            "pôles_gén",  # Thanks again Saint-Quentin-en-Yvelines for this monstrosity.
            "nom_generateur",
            "nom_gt",
            "nom_gene",
            "nom_zone_fine",
            "nom_zonefine",
            "nom_zf",
            "nom",
        ]

    def gt_type_columns(self):
        return [
            "typegd",
            "nature_generateur",
            "nom_type_gt",
            "nom_type",
            "catégorietxt",
            "descriptif",
            "nature",
            "categorie",
            "type_zonefine",
        ]

    def zf_id_columns(self):
        return [
            "num_zf_2013",
            "num_zf_2015",
            "zf2015_nouveau_codage",
            "num_zf08",
            "num_zf08_2",
            "id_zf_cerema",
            "zonefine",
            "zone_fine",
            "zf",
            "dfin",
            "num_zf",
            "code",
        ]

    def zf_name_columns(self):
        return ["zone_fin1", "nom_zonefine", "nom_zfine", "nom_zf", "nom"]

    def dtir_id_columns(self):
        return [
            "bayonne_dtir",  # Special case for Bayonne 2010 when reading the detailed zones.
            "id_st",
            "dtir_2016",
            "dtir_s",
            "num_dtir",
            "num_tirage",
            "num_secteur",
            "num_secteurs",
            "dtir",
            "code",
        ]

    def dtir_name_columns(self):
        return ["nom_dtir", "nom_dtir_enq", "nom_secteur"]

    def insee_id_columns(self):
        return [
            "insee_commune",
            "code_insee",
            "codinsee",
            "depcom",
            "insee",
            "id_commune",
            "com_2",
            "codcomm",
        ]

    def select_zf_column(self, gdf: gpd.GeoDataFrame):
        # For Bayonne 2010 and Metz 2017, the ZF id can be computed by summing two columns.
        pairs = (
            ("bayonne_dtir", "CODE_ZF_VALIDE"),  # Bayonne 2010.
            ("Dtir", "Num_zfin"),  # Metz 2017.
        )
        for sec_col, zf_num_col in pairs:
            if sec_col in gdf.columns and zf_num_col in gdf.columns:
                gdf["detailed_zone_id"] = gdf[sec_col].astype(str) + gdf[zf_num_col].astype(str)
                break
        # Normal case. Find the ZF id column by name.
        super().select_zf_column(gdf)

    def select_dtir_column(self, gdf: gpd.GeoDataFrame):
        if "Z_fine" in gdf.columns and "NUM_DTIR" in gdf.columns:
            # For Nantes 2015, there is 1 typo in NUM_DTIR so it is better to read the draw zone id
            # from the first 3 characters of Z_fine instead.
            gdf["draw_zone_id"] = gdf["Z_fine"].astype(str).str.slice(0, 3)
            assert (gdf["draw_zone_id"].astype(int) != gdf["NUM_DTIR"].astype(int)).sum() <= 1
        # This is the standard case.
        super().select_dtir_column(gdf)
        if "draw_zone_id" not in gdf.columns:
            # For Nice 2009, Saint-Denis-de-la-Réunion 2016, and Saint-Quentin-en-Yvelines 2010,
            # the draw_zone_id can be read from the first 3 characters of the GT column.
            # For Angers 2012, it can be read from the first 3 characters of the ZF column.
            for dtir_col in ("num_generateur08", "num_gene_2015", "pôle_génér", "code"):
                if matching_col := find_matching_column(dtir_col, gdf):
                    gdf["draw_zone_id"] = gdf[matching_col].astype(str).str.slice(0, 3)

    def select_zf_from_gt_column(self, gdf: gpd.GeoDataFrame):
        # For Metz 2017, the ZF id can be computed by summing two columns.
        if "Num_dtir" in gdf.columns and "Num_zfin" in gdf.columns:
            gdf["detailed_zone_id"] = gdf["Num_dtir"].astype(str) + gdf["Num_zfin"].astype(str)
        # Normal case. Find the ZF id column by name.
        super().select_zf_from_gt_column(gdf)

    def preprocess_special_locations(self, gdf: gpd.GeoDataFrame):
        # Very very special case for Metz 2017, GT 003003 is actually 003301 (don't ask me why).
        if "Code_gt" in gdf.columns and "Nom_gt" in gdf.columns:
            match = gdf.loc[(gdf["Code_gt"] == "003003") & (gdf["Nom_gt"] == "Aldi")].index
            if not match.empty:
                assert len(match) == 1
                gdf.loc[match, "Code_gt"] = "003301"
        return gdf

    def preprocess_detailed_zones(self, gdf: gpd.GeoDataFrame):
        # For Bayonne 2010, column "CODE_ZONE_VALIDE" contains the draw zone id but there is a type:
        # all values are "EMDxxx" where "xxx" is the draw zone id, except for one row where the
        # value is "004007" while it should be "EMD004" (don't ask why).
        if "CODE_ZONE_VALIDE" in gdf.columns:
            gdf["bayonne_dtir"] = gdf["CODE_ZONE_VALIDE"].astype(str).str.slice(-3)
            mask = gdf["CODE_ZONE_VALIDE"].astype(str).str.slice(0, 3) != "EMD"
            assert mask.sum() <= 1
            gdf.loc[mask, "bayonne_dtir"] = gdf["CODE_ZONE_VALIDE"].astype(str).str.slice(0, 3)
        # For Montpellier 2014, the external zones are included in the ZF file. We remove them.
        if "ID_ENQ" in gdf.columns:
            gdf = gdf.loc[gdf["ID_ENQ"] == 1].copy()
        if "ZONE_FINE" in gdf.columns and (gdf["ZONE_FINE"].str.len() == 7).all():
            # For Saint-Quentin-en-Yvelines 2010, there is a leading zero that needs to be removed.
            gdf["ZONE_FINE"] = gdf["ZONE_FINE"].str.slice(1)
        return gdf

    def postprocess_special_locations_and_detailed_zones(
        self, zfs: gpd.GeoDataFrame | None, gts: gpd.GeoDataFrame | None
    ):
        if gts is None:
            return zfs, gts
        # Special case for Amiens 2010, the insee_id (from column CODE_INSEE) is not valid for GTs.
        if "CODE_INSEE" in gts.columns and (gts["insee_id"].str.len() > 5).all():
            gts.drop(columns=["insee_id"], inplace=True)
        return zfs, gts


def get_files(source: str | ZipFile, name: str):
    # In the EDGT surveys, there are two directories with "standardized" data in the Csv directory,
    # usually "Fichiers_Standard_Face_a_face" and "Fichiers_Standard_Telephone" but it can be
    # something else.
    # Within these two directories, the CSV files to read are always
    # "[SURVEY_NAME]_std_faf_[NAME].csv" and "[SURVEY_NAME]_std_tel_[NAME].csv" where NAME is either
    # "men", "pers", "depl", or "traj".
    return [
        find_file(source, f".*_std_faf_{name}.csv", subdir="Csv"),
        find_file(source, f".*_std_tel_{name}.csv", subdir="Csv"),
    ]
