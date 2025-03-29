"""
REF sample data
"""

import importlib.metadata

__version__ = importlib.metadata.version("ref_sample_data")


from .data_request.base import DataRequest
from .data_request.cmip6 import CMIP6Request
from .data_request.obs4mips import Obs4MIPsRequest
from .data_request.obs4ref import Obs4REFRequest

__all__ = ["CMIP6Request", "DataRequest", "Obs4MIPsRequest", "Obs4REFRequest"]
