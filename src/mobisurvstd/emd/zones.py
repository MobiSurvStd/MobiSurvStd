from zipfile import ZipExtFile

import geopandas as gpd
from loguru import logger

# The zone files are not standardized, various column names can be used.
# The following list represent all the possible column names for the different variables.
# The column names are specified in lowercase because we match their name ignoring case.
DTIR_ID_COLUMNS = [
    "numsecteur2011",
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
DTIR_NAME_COLUMNS = ["nom_secteur2011", "nom_dtir"]
INSEE_ID_COLUMNS = ["cod_com", "codeinseecommune", "insee_comm", "numerocom", "com"]
ZF_ID_COLUMNS = [
    "zfin2016f",
    "numzonefine2011",
    "num_zf_def",
    "dfin_smart",
    "num_zf_2013",
    "_2017_zf",
    "idzfin2010",
    "zf_sec_emd2013",
    "code_sec_1",
]
ZF_NAME_COLUMNS = ["nom_zf_def", "nom_zf", "libelle_zf", "n_zfin2010", "libelle", "nom"]
ZF_ID_FROM_GT_COLUMNS = ["numzonefine2011appartenance", "zf_rattachement"]
GT_ID_COLUMNS = ["gt2016f", "numgenerateur2011", "zf_gt_def", "num_gene2013", "_2017_zf"]
GT_NAME_COLUMNS = ["nom_gene", "libelle_zf", "libelle", "nom", "generateur"]
GT_TYPE_COLUMNS = ["famille", "type", "nature_generateur"]


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
    if "draw_zone_id" in gdf.columns:
        gdf["draw_zone_id"] = cast_id(gdf["draw_zone_id"])


def select_insee_column(gdf: gpd.GeoDataFrame):
    for insee_col in INSEE_ID_COLUMNS:
        if matching_col := find_matching_column(insee_col, gdf):
            gdf["insee_id"] = cast_insee(gdf[matching_col])
            break
    else:
        # For Lille 2016, the insee_id can be read from the first 5 characters of the IRIS
        # column.
        if matching_col := find_matching_column("iris", gdf):
            gdf["insee_id"] = gdf[matching_col].str.slice(0, 5)


def select_zf_column(gdf: gpd.GeoDataFrame):
    for zf_col in ZF_ID_COLUMNS:
        if matching_col := find_matching_column(zf_col, gdf):
            gdf["detailed_zone_id"] = gdf[matching_col]
            break
    if "detailed_zone_id" in gdf.columns:
        gdf["detailed_zone_id"] = cast_id(gdf["detailed_zone_id"])


def select_gt_column(gdf: gpd.GeoDataFrame):
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
    # Read GT and ZF from the same file (for Valenciennes 2011).
    gdf = gpd.read_file(source)
    # This function should only be call for Valenciennes 2011 so we can assume that the column names are
    # known.
    assert "NumZoneFine2010" in gdf.columns
    assert "NumSecteur2010" in gdf.columns
    assert "Insee" in gdf.columns
    assert "geometry" in gdf.columns
    gdf.rename(columns={"NumSecteur2010": "draw_zone_id", "Insee": "insee_id"}, inplace=True)

    zfs = gdf.loc[gdf.geometry.geom_type != "Point"].copy()
    zfs.rename(columns={"NumZoneFine2010": "detailed_zone_id"}, inplace=True)
    zfs["detailed_zone_id"] = cast_id(zfs["detailed_zone_id"])
    zfs = zfs.loc[:, ["detailed_zone_id", "draw_zone_id", "insee_id", "geometry"]]

    gts = gdf.loc[gdf.geometry.geom_type == "Point"].copy()
    gts.rename(columns={"NumZoneFine2010": "special_location_id"}, inplace=True)
    gts["special_location_id"] = cast_id(gts["special_location_id"])
    gts = gts.loc[:, ["special_location_id", "draw_zone_id", "insee_id", "geometry"]]
    return zfs, gts
