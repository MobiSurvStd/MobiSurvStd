from zipfile import ZipExtFile

import geopandas as gpd
from loguru import logger

# The zone files are not standardized, various column names can be used.
# The following list represent all the possible column names for the different variables.
# The column names are specified in lowercase because we match their name ignoring case.
DTIR_ID_COLUMNS = [
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
DTIR_NAME_COLUMNS = [
    "nom_dtir",
    "nom_dtir_enq",
    "nom_secteurs",
    "nom_d30",
]
INSEE_ID_COLUMNS = [
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
ZF_ID_COLUMNS = [
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
    "id_zfine",
    "zone_f",
    "zone_fine",
    "zf",
    "zone",
]
ZF_NAME_COLUMNS = [
    "lib_dfin",
    "lib_zone_f",
    "libfin",
    "zf_lib",
    "nom_zfine",
    "nom_zf",
    "nom_iris",
    "nom",
]
ZF_ID_FROM_GT_COLUMNS = [
    "zf_2015",
    "zf_rattachement",
    "num_zf_c",
    "code_zone_fine",
    "numero_zone_fine",
    "zone_fine",
    "zf",
]
GT_ID_COLUMNS = [
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
    "zonefine",
    "zone_fine",
    "zf",
]
GT_NAME_COLUMNS = [
    "lib_pgt",
    "name_1",
    "nom_generateur_trafic",
    "nom_generateur",
    "nom_gene",
    "nom_gt",
    "nompgt",
    "nom_court",
    "nom",
    "nom_zf",
]
GT_TYPE_COLUMNS = [
    "descriptio",  # Typo is on purpose.
    "nature_generateur",
    "typepgt",
    "typegt",
    "typologie_gt",
    "lib_theme",
    "nature_zone_fine",
    "type",
]


def cast_id(s: gpd.GeoSeries):
    # Converts:
    # "ext" -> "ext"
    # 123456.0 -> "123456"
    # "012345" -> "12345"
    # "123 456" -> "123456"
    # "123.456" -> "123456"
    # Although it would be cleaner to keep the leading zero, it is safer to remove them because in
    # some cases there is not the same number of leading zeros in the zone files compared to the
    # survey's CSV files.
    return (
        s.astype(str)
        .str.replace(" ", "")
        .str.replace("[.]0$", "", n=1, regex=True)
        .str.replace(r"(?<=\d)[.](?=\d)", "", n=1, regex=True)
        .astype(int, errors="ignore")
        .astype(str)
    )


def cast_insee(s: gpd.GeoSeries):
    # Converts:
    # "01234" -> "01234"
    # 1234 -> "01234"
    # 1234.0 -> "01234"
    # "2B000" -> "2B000"
    # "999999" -> "999999"
    return (
        s.astype(str)
        .str.replace("[.]0$", "", n=1, regex=True)
        .str.pad(5, side="left", fillchar="0")
    )


def find_matching_column(name: str, gdf: gpd.GeoDataFrame):
    """Returns the name of the first column in the GeoDataFrame that matches the given name,
    ignoring case.

    Returns None if there is no matching column.
    """
    return next(filter(lambda c: c.lower() == name, gdf.columns), None)


def select_dtir_column(gdf: gpd.GeoDataFrame):
    for dtir_col in DTIR_ID_COLUMNS:
        if matching_col := find_matching_column(dtir_col, gdf):
            gdf["draw_zone_id"] = gdf[matching_col]
            break
    else:
        # For Creil 2017, La-Roche-sur-Yon 2013, Le Creusot 2012, and Les Sables d'Olonnes 2011, the
        # detailed_zone_id can be read from the first 3 characters of the ZF or GT column.
        for dtir_col in ("zone_fine", "codage", "num_zf", "code_pole_gen"):
            if matching_col := find_matching_column(dtir_col, gdf):
                gdf["draw_zone_id"] = gdf[matching_col].str.slice(0, 3)
    if "draw_zone_id" in gdf.columns:
        gdf["draw_zone_id"] = cast_id(gdf["draw_zone_id"])


def select_insee_column(gdf: gpd.GeoDataFrame):
    for insee_col in INSEE_ID_COLUMNS:
        if matching_col := find_matching_column(insee_col, gdf):
            gdf["insee_id"] = cast_insee(gdf[matching_col])
            break
    else:
        # For Angoulème 2012, the insee_id can be read from the first 5 characters of the DcomIris
        # column.
        if matching_col := find_matching_column("dcomiris", gdf):
            gdf["insee_id"] = gdf[matching_col].str.slice(0, 5)


def select_zf_column(gdf: gpd.GeoDataFrame):
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
    else:
        # Normal case. Find the ZF id column by name.
        for zf_col in ZF_ID_COLUMNS:
            if matching_col := find_matching_column(zf_col, gdf):
                gdf["detailed_zone_id"] = gdf[matching_col]
                break
        else:
            # Special case for Les Sables d'Olonnes 2011: Two zeros must be added before the last
            # number.
            if "codage" in gdf.columns:
                gdf["detailed_zone_id"] = gdf["codage"].str.replace(r"(\d)$", r"00\1", regex=True)
    if "detailed_zone_id" in gdf.columns:
        gdf["detailed_zone_id"] = cast_id(gdf["detailed_zone_id"])


def select_gt_column(gdf: gpd.GeoDataFrame):
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
    else:
        # Normal case. Find the GT id column by name.
        for gt_col in GT_ID_COLUMNS:
            if matching_col := find_matching_column(gt_col, gdf):
                gdf["special_location_id"] = gdf[matching_col]
                # Drop the original column so that it will not be wrongly read when finding the
                # matching ZF id column.
                gdf.drop(columns=[matching_col], inplace=True)
                break
    if "special_location_id" in gdf.columns:
        gdf["special_location_id"] = cast_id(gdf["special_location_id"])


def select_zf_from_gt_column(gdf: gpd.GeoDataFrame):
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
        # For Saintes 2016, the ZF id can be computed by summing three columns.
        if "Pgt" in gdf.columns:
            gdf["detailed_zone_id"] = gdf["Pgt"].astype(int) // 10 * 10
        else:
            # Normal case. Find the ZF id column by name.
            for zf_col in ZF_ID_FROM_GT_COLUMNS:
                if matching_col := find_matching_column(zf_col, gdf):
                    gdf["detailed_zone_id"] = gdf[matching_col]
                    break
    if "detailed_zone_id" in gdf.columns:
        gdf["detailed_zone_id"] = cast_id(gdf["detailed_zone_id"])


def select_name_column(gdf: gpd.GeoDataFrame, col_names: list[str], name: str):
    for zf_name_col in col_names:
        if matching_col := find_matching_column(zf_name_col, gdf):
            gdf[name] = gdf[matching_col].astype(str)


def select_columns(gdf: gpd.GeoDataFrame, cols: tuple[str, ...]):
    """Given a tuple of column names, return the list of columns which are present in the
    GeoDataFrame.
    """
    return ["geometry"] + list(filter(lambda c: c in gdf.columns, cols))


def read_special_locations(source: str | ZipExtFile):
    gdf = gpd.read_file(source)
    select_gt_column(gdf)
    select_zf_from_gt_column(gdf)
    select_dtir_column(gdf)
    select_insee_column(gdf)
    select_name_column(gdf, GT_TYPE_COLUMNS, "special_location_type")
    select_name_column(gdf, GT_NAME_COLUMNS, "special_location_name")
    columns = select_columns(
        gdf,
        (
            "special_location_id",
            "special_location_name",
            "special_location_type",
            "detailed_zone_id",
            "insee_id",
            "draw_zone_id",
        ),
    )
    assert "geometry" in columns
    if "special_location_id" not in columns:
        logger.warning("Missing special location id in special location file")
        return None
    return gdf[columns].copy()


def read_detailed_zones(source: str | ZipExtFile):
    try:
        gdf = gpd.read_file(source)
    except UnicodeDecodeError:
        # For Laval 2011, the encoding needs to be specified.
        gdf = gpd.read_file(source, encoding="windows-1250")
    select_zf_column(gdf)
    select_dtir_column(gdf)
    select_insee_column(gdf)
    select_name_column(gdf, ZF_NAME_COLUMNS, "detailed_zone_name")
    columns = select_columns(
        gdf, ("detailed_zone_id", "detailed_zone_name", "insee_id", "draw_zone_id")
    )
    assert "detailed_zone_id" in columns
    assert "geometry" in columns
    return gdf[columns].copy()


def read_draw_zones(source: str | ZipExtFile):
    gdf = gpd.read_file(source)
    select_dtir_column(gdf)
    select_name_column(gdf, DTIR_NAME_COLUMNS, "draw_zone_name")
    columns = select_columns(gdf, ("draw_zone_id", "draw_zone_name"))
    assert "draw_zone_id" in columns
    assert "geometry" in columns
    return gdf[columns].copy()


def read_special_locations_and_detailed_zones(source: str | ZipExtFile):
    # Read GT and ZF from the same file (for Beauvais 2011).
    gdf = gpd.read_file(source)
    # This function should only be call for Beauvais 2011 so we can assume that the column names are
    # known.
    assert "Type" in gdf.columns
    assert "NumeroZF" in gdf.columns
    assert "NomGT_ZF" in gdf.columns
    assert "NumeroDTIR" in gdf.columns
    assert "INSEE_Commune" in gdf.columns
    assert "geometry" in gdf.columns
    gdf.rename(columns={"NumeroDTIR": "draw_zone_id", "INSEE_Commune": "insee_id"}, inplace=True)

    zfs = gdf.loc[gdf["Type"] == "ZF"].copy()
    zfs.rename(
        columns={"NumeroZF": "detailed_zone_id", "NomGT_ZF": "detailed_zone_name"}, inplace=True
    )
    zfs["detailed_zone_id"] = cast_id(zfs["detailed_zone_id"])
    zfs = zfs.loc[
        :, ["detailed_zone_id", "detailed_zone_name", "draw_zone_id", "insee_id", "geometry"]
    ]

    gts = gdf.loc[gdf["Type"] == "GT"].copy()
    gts.rename(
        columns={"NumeroZF": "special_location_id", "NomGT_ZF": "special_location_name"},
        inplace=True,
    )
    gts["special_location_id"] = cast_id(gts["special_location_id"])
    # The corresponding ZF is the GT id with the last digit replaced by 0.
    gts["detailed_zone_id"] = gts["special_location_id"].str.replace(r"\d$", "0", regex=True)
    gts = gts.loc[
        :,
        [
            "special_location_id",
            "special_location_name",
            "detailed_zone_id",
            "draw_zone_id",
            "insee_id",
            "geometry",
        ],
    ]
    return zfs, gts
