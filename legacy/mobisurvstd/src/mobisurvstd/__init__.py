"""Deprecated alias of `nemobi` (MobiSurvStd was renamed to Nemobi in v2.0.0)."""

import importlib
import importlib.abc
import importlib.util
import sys
import warnings

import nemobi
from nemobi import *  # noqa: F403
from nemobi import __version__ as __version__

_MESSAGE = (
    "MobiSurvStd has been renamed to Nemobi: the `mobisurvstd` package is deprecated and will not "
    "receive updates. Run `pip install nemobi` and replace `mobisurvstd` with `nemobi` in your "
    "code "
    "(see https://nemobi.lucasjavaudin.com/migration.html)."
)

warnings.warn(_MESSAGE, DeprecationWarning, stacklevel=2)


class _AliasFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Makes `import mobisurvstd.x.y` return the module `nemobi.x.y`."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith("mobisurvstd."):
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return importlib.import_module("nemobi" + spec.name.removeprefix("mobisurvstd"))

    def exec_module(self, module):
        pass


sys.meta_path.insert(0, _AliasFinder())


def __getattr__(name):
    return getattr(nemobi, name)


def _cli():
    from loguru import logger

    from nemobi.cli import app

    logger.warning(
        "The `mobisurvstd` command is deprecated, use `nemobi` instead "
        "(see https://nemobi.lucasjavaudin.com/migration.html)."
    )
    app()
