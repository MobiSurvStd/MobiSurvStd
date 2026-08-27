import shutil
from pathlib import Path

import humanize
from loguru import logger
from platformdirs import user_cache_dir

CACHE_DIR = user_cache_dir("mobisurvstd")


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
