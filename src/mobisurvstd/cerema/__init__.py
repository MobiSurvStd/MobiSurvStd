from zipfile import ZipFile

from .edgt import EDGTReader
from .edvm import EDVMReader
from .emc2 import EMC2Reader
from .emd import EMDReader


def standardize(source: str | ZipFile, survey_type: str, skip_spatial: bool = False):
    if survey_type == "EMC2":
        reader = EMC2Reader(source)
    elif survey_type == "EDGT":
        reader = EDGTReader(source)
    elif survey_type == "EDVM":
        reader = EDVMReader(source)
    elif survey_type == "EMD":
        reader = EMDReader(source)
    else:
        raise NotImplementedError
    return reader.standardize(skip_spatial)
