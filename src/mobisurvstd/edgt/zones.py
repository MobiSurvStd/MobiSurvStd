from zipfile import ZipExtFile

import geopandas as gpd

# The zone files are not standardized, various column names can be used.
ST_ID_COLUMNS = [
    "DTIR",
    "Dtir",
    "Id_st",
    "NUM_DTIR",
    "Num_dtir",
    "num_dtir",
    "NUM_DTIR_F",
    "NUM_SECTEURS",
    "Ztir",
    "CODSECT",
    "DTIR_160",
    "Secteur",
]
INSEE_ID_COLUMNS = [
    "INSEE",
    "CODE_INSEE",
    "CODE_COM",
    "Insee_com",
    "insee_com",
    "INSEE_COM",
    "INSEE_Commune",
    "Insee",
    "Insee_gen",
    "NUM_COM",
]


def cast_str(s: gpd.GeoSeries):
    # In some cases the ids are reported with a trailing ".0" (because they are stored as floats) or
    # with whitespaces (e.g., "183 011 000"). The code below ensure that all ids are strings
    # representing valid integers.
    # Id an id is alphanumeric (e.g., "ext" or "2B000"), then the id is kept as it is.
    return (
        s.astype(str)
        .str.replace(" ", "")
        .str.replace(".0", "")
        .astype(int, errors="ignore")
        .astype(str)
    )


def select_column(
    gdf: gpd.GeoDataFrame,
    col_name: str,
    valid_columns: list[str],
    columns_to_select: list[str],
    cast: bool,
):
    for col in valid_columns:
        if col in gdf.columns:
            if cast:
                gdf[col_name] = cast_str(gdf[col])
            else:
                gdf[col_name] = gdf[col]
            if not gdf[col_name].isnull().all():
                columns_to_select.append(col_name)
            break


def read_special_locations(source: str | ZipExtFile):
    gt_id_columns = [
        "GT",
        "num_GT",
        "ZF",
        "NUM_GT",
        "Zf",
        "ZoneFine",
        "CodeGT",
        "cod_PGT_2",
        "NUM_GENE2013",
        "num_generateurs08",
        "ID",
        "Id",
    ]  # The order is important here.
    gt_name_columns = [
        "NOM_GT",
        "nom_GT",
        "Nom_gen",
        "Nom_ZoneFine",
        "NOM",
        "LIBELLE",
        "Libelle",
        "Nom",
        "REM",
        "Rem",
        "NOM_GENE",
        "nom_generateur",
    ]
    zf_id_columns = [
        "ZFRAT",
        "Zfrat",
        "NUM_ZF_Rat",
        "Cd_zf",
        "NUM_ZF_19",
        "Zf_rattach",
        "ZF_rattachement",
        "ZF_160",
        "Z_fine",
        "NUM_ZF",
        "ZF",
    ]
    gdf = gpd.read_file(
        source,
        columns=gt_id_columns + gt_name_columns + zf_id_columns + INSEE_ID_COLUMNS + ST_ID_COLUMNS,
    )
    # Note. For some surveys, the dots need to be removed to match what is set in the CSVs.
    for col in ("ZoneFine",):
        if col in gdf.columns:
            gdf[col] = gdf[col].str.replace(".", "")
    columns = list()
    select_column(gdf, "special_location_id", gt_id_columns, columns, cast=True)
    select_column(gdf, "special_location_name", gt_name_columns, columns, cast=False)
    select_column(gdf, "detailed_zone_id", zf_id_columns, columns, cast=True)
    select_column(gdf, "draw_zone_id", ST_ID_COLUMNS, columns, cast=True)
    select_column(gdf, "insee_id", INSEE_ID_COLUMNS, columns, cast=False)
    columns.append("geometry")
    assert "special_location_id" in columns
    if "Caen2011" in source:
        # Very special case, detailed_zone_id is not available for Caen 2011 (altough the ZF
        # variable exists).
        columns.remove("detailed_zone_id")
    return gdf[columns].copy()


def read_detailed_zones(source: str | ZipExtFile):
    zf_id_columns = [
        "IdSectZF",
        "ZF",
        "Zf",
        "NUM_ZF_2013",
        "NUM_ZF_2015",
        "NUM_ZF08",
        "NUM_ZF",
        "ZoneFine",
        "ZONE_FINE",
        "ZF_Fusion",
        "COD_ZF",
        "CODE_ZF_VALIDE",
        "ZF_160",
        "ZF__2015",
        "Id_zf_cerema",
        "DFIN",
        "CODE",
    ]
    zf_name_columns = [
        "Zf_nom",
        "Nom_ZoneFine",
        "Nom_zf",
        "NOM_ZF",
        "Lib_ZF",
        "Nomiris",
        "LIBELLE",
        "Libelle",
        "Nom",
        "NOM",
        "REM",
        "Lib_Zone_fine",
        "ZONE_FIN1",
        "ZF",
    ]
    gdf = gpd.read_file(
        source, columns=zf_id_columns + zf_name_columns + INSEE_ID_COLUMNS + ST_ID_COLUMNS
    )
    # Note. For some surveys, the dots need to be removed to match what is set in the CSVs.
    for col in ("CODE", "DFIN"):
        if col in gdf.columns:
            gdf[col] = gdf[col].str.replace(".", "")
    columns = list()
    select_column(gdf, "detailed_zone_id", zf_id_columns, columns, cast=True)
    select_column(gdf, "detailed_zone_name", zf_name_columns, columns, cast=False)
    select_column(gdf, "draw_zone_id", ST_ID_COLUMNS, columns, cast=True)
    select_column(gdf, "insee_id", INSEE_ID_COLUMNS, columns, cast=False)
    columns.append("geometry")
    assert "detailed_zone_id" in columns
    return gdf[columns].copy()


def read_draw_zones(source: str | ZipExtFile):
    st_name_columns = ["NOM_DTIR"]
    gdf = gpd.read_file(source, columns=ST_ID_COLUMNS + st_name_columns + INSEE_ID_COLUMNS)
    columns = list()
    select_column(gdf, "draw_zone_id", ST_ID_COLUMNS, columns, cast=True)
    select_column(gdf, "draw_zone_name", st_name_columns, columns, cast=False)
    select_column(gdf, "insee_id", INSEE_ID_COLUMNS, columns, cast=False)
    columns.append("geometry")
    assert "draw_zone_id" in columns
    return gdf[columns].copy()
