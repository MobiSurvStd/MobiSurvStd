import os
import re

from mobisurvstd.cerema.survey import CeremaReader
from mobisurvstd.utils import find_file


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
        return ["zf", "num_gt", "codegt"]

    def zf_id_from_gt_columns(self):
        return ["zfrat", "num_zf_rat", "cd_zf", "num_zf_19", "zf_rattach", "zf_160"]

    def gt_name_columns(self):
        return ["nom_gt", "nom_gen", "libelle", "nom", "rem"]

    def gt_type_columns(self):
        # TODO
        return []

    def zf_id_columns(self):
        return ["zf_ini", "num_zf", "zf_fusion", "cod_zf", "zf_160", "zf"]

    def zf_name_columns(self):
        return ["zf_nom", "nom_zf", "lib_zf", "libelle", "rem"]

    def dtir_id_columns(self):
        return [
            "dtir_160",
            "codsect",
            "ztir",
            "num_dtir_f",
            "num_dtir",
            "dtir",
        ]

    def dtir_name_columns(self):
        return ["nom_dtir"]

    def insee_id_columns(self):
        return [
            "code_insee",
            "insee_com",
            "insee_commune",
            "insee",
            "code_com",
            "insee_gen",
            "num_com",
        ]
