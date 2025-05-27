import os.path
import pathlib
from pathlib import Path
from typing import Any

import pandas as pd
import xarray as xr

from ref_sample_data.data_request.base import DecimateMixin, IntakeESGFMixin


def prefix_to_filename(ds, filename_prefix: str) -> str:
    """
    Create a filename from a dataset and a prefix.

    Optionally includes the time range of the dataset if it has a time dimension.

    Parameters
    ----------
    ds
        Dataset
    filename_prefix
        Prefix for the filename

        This includes the different facets of the dataset

    Returns
    -------
        Filename for the dataset
    """
    if "time" in ds.dims:
        time_range = f"{ds.time.min().dt.strftime('%Y%m').item()}-{ds.time.max().dt.strftime('%Y%m').item()}"
        filename = f"{filename_prefix}_{time_range}.nc"
    else:
        filename = f"{filename_prefix}.nc"
    return filename


class CMIP6Request(IntakeESGFMixin, DecimateMixin):
    """
    Represents a CMIP6 dataset request

    These data are fetched from ESGF and decimated according to their grid type
    """

    source_type = "CMIP6"

    cmip6_path_items = (
        "mip_era",
        "activity_drs",
        "institution_id",
        "source_id",
        "experiment_id",
        "member_id",
        "table_id",
        "variable_id",
        "grid_label",
    )

    cmip6_filename_paths = (
        "variable_id",
        "table_id",
        "source_id",
        "experiment_id",
        "member_id",
        "grid_label",
    )

    def __init__(self, facets: dict[str, Any], remove_ensembles: bool, time_span: tuple[str, str] | None):
        self.avail_facets = [
            "mip_era",
            "activity_drs",
            "institution_id",
            "source_id",
            "experiment_id",
            "member_id",
            "table_id",
            "variable_id",
            "grid_label",
            "version",
            "data_node",
        ]

        self.facets = facets
        self.remove_ensembles = remove_ensembles
        self.time_span = time_span

        assert all(key in self.avail_facets for key in self.cmip6_path_items), "Error message"
        assert all(key in self.avail_facets for key in self.cmip6_filename_paths), "Error message"

    def generate_filename(self, metadata: pd.Series, ds: xr.Dataset, ds_filename: pathlib.Path) -> Path:
        """
        Create the output filename for the dataset.

        Parameters
        ----------
        ds
            Loaded dataset

        ds_filename:
            Filename of the dataset (Unused)

        Returns
        -------
            The output filename
        """
        output_path = (
            Path(os.path.join(*[metadata[item] for item in self.cmip6_path_items]))
            / f"v{metadata['version']}"
        )
        filename_prefix = "_".join([metadata[item] for item in self.cmip6_filename_paths])

        return output_path / prefix_to_filename(ds, filename_prefix)
