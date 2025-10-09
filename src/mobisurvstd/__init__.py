from importlib.metadata import version

from .classes import SurveyDataReader as SurveyDataReader
from .classes import read_many as read_many
from .logger import setup as setup
from .main import bulk_standardize as bulk_standardize
from .main import standardize as standardize

__version__ = version("mobisurvstd")

# Initialize logging.
setup()
