from zipfile import ZipExtFile

import geopandas as gpd
import pandas as pd
from loguru import logger


def cast_id(s: gpd.GeoSeries):
    # Converts:
    # "ext" -> "ext"
    # 123456.0 -> "123456"
    # "012345" -> "012345"
    # "123 456" -> "123456"
    # "123.456" -> "123456"
    return (
        s.astype(str)
        .str.replace(" ", "")
        .str.replace("[.]0$", "", n=1, regex=True)
        .str.replace(r"(?<=\d)[.](?=\d)", "", n=1, regex=True)
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


def cast_columns(gdf: gpd.GeoDataFrame):
    for col in ("special_location_id", "detailed_zone_id"):
        if col in gdf.columns:
            gdf[col] = cast_id(gdf[col])
    if "draw_zone_id" in gdf.columns:
        # The DTIR columns always have 4 characters in the CSVs.
        gdf["draw_zone_id"] = cast_id(gdf["draw_zone_id"]).str.pad(width=4, fillchar="0")
    if "insee_id" in gdf.columns:
        gdf["insee_id"] = cast_insee(gdf["insee_id"])


def read_file(filename: str | ZipExtFile):
    try:
        gdf = gpd.read_file(filename)
    except UnicodeDecodeError:
        # For some surveys, the encoding needs to be specified.
        gdf = gpd.read_file(filename, encoding="windows-1250")
    gdf.set_geometry(gdf.geometry.make_valid(), inplace=True)
    if gdf.crs is None:
        # Assume WGS84 if crs is missing.
        gdf.set_crs("EPSG:4326", inplace=True)
    if gdf.crs.is_geographic:
        # Convert the appropriate UTM CRS (we could convert to Lambert but that would not work for
        # oversea territories)
        centroid = gdf.geometry.union_all().centroid
        x, y = centroid.x, centroid.y
        zone = int((x + 180) / 6) + 1
        epsg = 32600 + zone if y >= 0 else 32700 + zone
        gdf.to_crs(f"EPSG:{epsg}", inplace=True)
    return gdf


def find_matching_column(name: str, gdf: gpd.GeoDataFrame):
    """Returns the name of the first column in the GeoDataFrame that matches the given name,
    ignoring case.

    Returns None if there is no matching column.
    """
    return next(filter(lambda c: c.lower() == name, gdf.columns), None)


def select_name_column(gdf: gpd.GeoDataFrame, col_names: list[str], name: str):
    for zf_name_col in col_names:
        if matching_col := find_matching_column(zf_name_col, gdf):
            if (
                gdf[matching_col].astype(str).str.len().eq(0).all()
                or gdf[matching_col].nunique() == 1
            ):
                # A matching column was found but it is empty.
                continue
            gdf[name] = gdf[matching_col].astype(str)


def select_columns(gdf: gpd.GeoDataFrame, cols: tuple[str, ...]):
    """Given a tuple of column names, return the list of columns which are present in the
    GeoDataFrame.
    """
    return ["geometry"] + list(filter(lambda c: c in gdf.columns, cols))


class ZonesReader:
    def gt_id_columns(self):
        raise NotImplementedError

    def zf_id_from_gt_columns(self):
        raise NotImplementedError

    def gt_name_columns(self):
        raise NotImplementedError

    def gt_type_columns(self):
        raise NotImplementedError

    def zf_id_columns(self):
        raise NotImplementedError

    def zf_name_columns(self):
        raise NotImplementedError

    def dtir_id_columns(self):
        raise NotImplementedError

    def dtir_name_columns(self):
        raise NotImplementedError

    def insee_id_columns(self):
        raise NotImplementedError

    def select_dtir_column(self, gdf: gpd.GeoDataFrame):
        if "draw_zone_id" in gdf.columns:
            # Column already exists (added by a subclass?).
            return
        for dtir_col in self.dtir_id_columns():
            if matching_col := find_matching_column(dtir_col, gdf):
                gdf["draw_zone_id"] = gdf[matching_col]
                break

    def select_insee_column(self, gdf: gpd.GeoDataFrame):
        if "insee_id" in gdf.columns:
            # Column already exists (added by a subclass?).
            return
        for insee_col in self.insee_id_columns():
            if matching_col := find_matching_column(insee_col, gdf):
                if gdf[matching_col].astype(str).str.len().eq(0).all():
                    # A matching column was found but it is empty.
                    continue
                gdf["insee_id"] = gdf[matching_col]
                break

    def select_zf_column(self, gdf: gpd.GeoDataFrame):
        if "detailed_zone_id" in gdf.columns:
            # Column already exists (added by a subclass?).
            return
        for zf_col in self.zf_id_columns():
            if matching_col := find_matching_column(zf_col, gdf):
                gdf["detailed_zone_id"] = gdf[matching_col]
                # Drop the original column so that it will not be wrongly read when finding the
                # matching ST id column.
                gdf.drop(columns=[matching_col], inplace=True)
                break

    def select_gt_column(self, gdf: gpd.GeoDataFrame):
        if "special_location_id" in gdf.columns:
            # Column already exists (added by a subclass?).
            return
        for gt_col in self.gt_id_columns():
            if matching_col := find_matching_column(gt_col, gdf):
                gdf["special_location_id"] = gdf[matching_col]
                # Drop the original column so that it will not be wrongly read when finding the
                # matching ZF id column.
                gdf.drop(columns=[matching_col], inplace=True)
                break

    def select_zf_from_gt_column(self, gdf: gpd.GeoDataFrame):
        if "detailed_zone_id" in gdf.columns:
            # Column already exists (added by a subclass?).
            return
        for zf_col in self.zf_id_from_gt_columns():
            if matching_col := find_matching_column(zf_col, gdf):
                gdf["detailed_zone_id"] = gdf[matching_col]
                break

    def read_special_locations(self):
        if self.special_locations is not None:
            # Special locations have been read from the common ZF / GT file.
            return
        filenames = self.special_locations_filenames()
        if not any(filenames):
            logger.debug(f"No file with special locations in `{self.source_name()}`")
            return
        gdfs = list()
        for filename in filter(None, filenames):
            logger.debug(f"Reading special locations from `{filename}`")
            gdf = self.process_special_locations(filename)
            if gdf is not None:
                gdfs.append(gdf)
        if gdfs:
            gdf = pd.concat(gdfs)
            if gdf["special_location_id"].nunique() != len(gdf):
                # La Roche-sur-Yon 2013 will hit this case because 2 special locations have the same
                # it. It seems that the special locations never appear in the survey so it's fine if
                # they are discarded here.
                logger.warning("Special location ids are not unique")
            else:
                self.special_locations = gdf

    def process_special_locations(self, filename: str | ZipExtFile):
        gdf = read_file(filename)
        gdf = self.preprocess_special_locations(gdf)
        self.select_gt_column(gdf)
        self.select_zf_from_gt_column(gdf)
        self.select_dtir_column(gdf)
        self.select_insee_column(gdf)
        select_name_column(gdf, self.gt_type_columns(), "special_location_type")
        select_name_column(gdf, self.gt_name_columns(), "special_location_name")
        cast_columns(gdf)
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

    def preprocess_special_locations(self, gdf: gpd.GeoDataFrame):
        # Allows surveys to define their own processing.
        return gdf

    def read_detailed_zones(self):
        if self.detailed_zones is not None:
            # Detailed zones have been read from the common ZF / GT file.
            return
        filenames = self.detailed_zones_filenames()
        if not any(filenames):
            logger.debug(f"No file with detailed zones in `{self.source_name()}`")
            return
        gdfs = list()
        for filename in filter(None, filenames):
            logger.debug(f"Reading detailed zones from `{filename}`")
            gdf = self.process_detailed_zones(filename)
            if gdf is not None:
                gdfs.append(gdf)
        if gdfs:
            gdf = pd.concat(gdfs)
            if gdf["detailed_zone_id"].nunique() != len(gdf):
                logger.warning("Duplicated detailed zone ids in detailed zone file")
                return
            self.detailed_zones = gdf

    def process_detailed_zones(self, filename: str | ZipExtFile):
        gdf = read_file(filename)
        gdf = self.preprocess_detailed_zones(gdf)
        self.select_zf_column(gdf)
        self.select_dtir_column(gdf)
        self.select_insee_column(gdf)
        select_name_column(gdf, self.zf_name_columns(), "detailed_zone_name")
        cast_columns(gdf)
        columns = select_columns(
            gdf, ("detailed_zone_id", "detailed_zone_name", "insee_id", "draw_zone_id")
        )
        # For Saint-Quentin-en-Yvelines, some rows are empty and need to be dropped.
        mask = gdf["detailed_zone_id"] == ""
        if mask.any():
            logger.warning(f"Removing {mask.sum()} detailed zones with no ID")
            gdf = gdf.loc[~mask].copy()
        assert "geometry" in columns
        if "detailed_zone_id" not in columns:
            logger.warning("Missing detailed zone id in detailed zone file")
            return None
        return gdf[columns].copy()

    def preprocess_detailed_zones(self, gdf: gpd.GeoDataFrame):
        # Allows surveys to define their own processing.
        return gdf

    def read_draw_zones(self):
        assert self.draw_zones is None
        filenames = self.draw_zones_filenames()
        if not any(filenames):
            logger.debug(f"No file with draw zones in `{self.source_name()}`")
            return
        gdfs = list()
        for filename in filter(None, filenames):
            logger.debug(f"Reading draw zones from `{filename}`")
            gdf = self.process_draw_zones(filename)
            if gdf is not None:
                gdfs.append(gdf)
        if gdfs:
            self.draw_zones = pd.concat(gdfs)

    def process_draw_zones(self, filename: str | ZipExtFile):
        gdf = read_file(filename)
        gdf = self.preprocess_draw_zones(gdf)
        self.select_dtir_column(gdf)
        cast_columns(gdf)
        select_name_column(gdf, self.dtir_name_columns(), "draw_zone_name")
        columns = select_columns(gdf, ("draw_zone_id", "draw_zone_name"))
        assert "geometry" in columns
        if "draw_zone_id" not in columns:
            logger.warning("Missing draw zone id in draw zone file")
            return None
        if gdf["draw_zone_id"].nunique() != len(gdf):
            logger.warning(
                "Duplicated draw zone ids in draw zone file: zones with identical ids are merged"
            )
            gdf = gdf.dissolve(by="draw_zone_id", as_index=False)
            # Try to clean the dissolve.
            gdf.geometry = gdf.geometry.buffer(10).buffer(-10)
        return gdf[columns].copy()

    def preprocess_draw_zones(self, gdf: gpd.GeoDataFrame):
        # Allows surveys to define their own processing.
        return gdf

    def read_special_locations_and_detailed_zones(self):
        filenames = self.special_locations_and_detailed_zones_filenames()
        if not any(filenames):
            return
        zfs = list()
        gts = list()
        for filename in filter(None, filenames):
            logger.debug(f"Reading special locations and detailed zones from `{filename}`")
            zf, gt = self.process_special_locations_and_detailed_zones(filename)
            if zf is not None:
                zfs.append(zf)
            if gt is not None:
                gts.append(gt)
        if zfs:
            self.detailed_zones = pd.concat(zfs)
        if gts:
            self.special_locations = pd.concat(gts)

    def process_special_locations_and_detailed_zones(self, filename: str | ZipExtFile):
        gdf = read_file(filename)
        gdf = self.preprocess_special_locations_and_detailed_zones(gdf)
        self.select_dtir_column(gdf)
        self.select_insee_column(gdf)
        zfs, gts = self.split_special_locations_and_detailed_zones(gdf)

        self.select_zf_column(zfs)
        select_name_column(zfs, ["nom_fine", "lib_zone_fine"], "detailed_zone_name")
        cast_columns(zfs)
        columns = select_columns(
            zfs, ("detailed_zone_id", "detailed_zone_name", "insee_id", "draw_zone_id")
        )
        if "detailed_zone_id" not in columns:
            logger.warning("Missing detailed zone id in detailed zone file")
            zfs = None
        if zfs["detailed_zone_id"].nunique() != len(zfs):
            logger.warning("Duplicated detailed zone ids in detailed zone file")
            zfs = None
        else:
            assert "geometry" in columns
            zfs = zfs[columns].copy()

        self.select_gt_column(gts)
        self.select_zf_from_gt_column(gts)
        select_name_column(gts, ["nom_fine", "lib_zone_fine"], "special_location_name")
        select_name_column(gts, self.gt_type_columns(), "special_location_type")
        cast_columns(gts)
        columns = select_columns(
            gts,
            (
                "special_location_id",
                "special_location_name",
                "special_location_type",
                "detailed_zone_id",
                "insee_id",
                "draw_zone_id",
            ),
        )
        if "special_location_id" not in columns:
            logger.warning("Missing special location id in special location file")
            gts = None
        if gts["special_location_id"].nunique() != len(gts):
            logger.warning("Duplicated special location ids in special location file")
            gts = None
        else:
            assert "geometry" in columns
            gts = gts[columns].copy()

        zfs, gts = self.postprocess_special_locations_and_detailed_zones(zfs, gts)
        return zfs, gts

    def split_special_locations_and_detailed_zones(self, gdf: gpd.GeoDataFrame):
        # Default is to split based on the geometry type (Point if and only if GT).
        # Surveys can overtwrite that function to split differently.
        zfs = gdf.loc[gdf.geometry.geom_type != "Point"].copy()
        gts = gdf.loc[gdf.geometry.geom_type == "Point"].copy()
        return zfs, gts

    def preprocess_special_locations_and_detailed_zones(self, gdf: gpd.GeoDataFrame):
        # Allows surveys to define their own processing.
        return gdf

    def postprocess_special_locations_and_detailed_zones(
        self, zfs: gpd.GeoDataFrame | None, gts: gpd.GeoDataFrame | None
    ):
        # Allows surveys to define their own processing.
        return zfs, gts
