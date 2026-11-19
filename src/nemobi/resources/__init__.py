import shutil
from pathlib import Path

import humanize
from loguru import logger
from platformdirs import user_cache_dir

CACHE_DIR = user_cache_dir("nemobi")


def _migrate_legacy_cache():
    """Reuses the cache directory of MobiSurvStd (the former name of Nemobi), if any, so that the
    IGN / INSEE data does not have to be downloaded again."""
    legacy_dir = Path(user_cache_dir("mobisurvstd"))
    if legacy_dir.is_dir() and not Path(CACHE_DIR).exists():
        try:
            Path(CACHE_DIR).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(legacy_dir, CACHE_DIR)
            logger.debug(f"Moved legacy MobiSurvStd cache from `{legacy_dir}` to `{CACHE_DIR}`")
        except OSError:
            # Not a problem: the data will be downloaded again.
            pass


_migrate_legacy_cache()


def clear_cache():
    from .admin_express import load_insee_geometries

    dir_size = sum(f.stat().st_size for f in Path(CACHE_DIR).glob("**/*") if f.is_file())
    try:
        shutil.rmtree(CACHE_DIR)
        logger.success(f"Removed {humanize.naturalsize(dir_size)} from the cache directory")
    except FileNotFoundError:
        logger.warning("Cache directory is already empty")
    except PermissionError:
        logger.error("Failed to clear cache directory: permission denied")
    except Exception as e:
        logger.error(f"Failed to clear cache directory: {e}")
    # Also invalidate the cached `load_insee_geometries` function.
    load_insee_geometries.cache_clear()
