import pathlib
from pathlib import Path

import climate_ref  # noqa
import pandas as pd
import xarray as xr
from climate_ref_core.dataset_registry import dataset_registry_manager

from ref_sample_data.data_request.base import DecimateMixin


class Obs4REFRequest(DecimateMixin):
    """
    Fetch the unpublished Obs4MIPs datasets from the PMP registry

    This includes all files that would be downloaded if you ran:
    ```
    ref datasets fetch-obs4ref-data --output-data ...
    ```
    """

    id = "obs4ref"
    source_type = "obs4REF"
    time_span = None

    def fetch_datasets(self) -> pd.DataFrame:
        """
        Fetch the datasets from the source

        Returns a dataframe of the metadata and paths to the fetched datasets.
        """
        registry = dataset_registry_manager["obs4ref"]

        datasets = []
        for key in registry.registry.keys():
            dataset_path = registry.fetch(key)
            datasets.append(
                {
                    "key": key,
                    "files": [dataset_path],
                }
            )
        return pd.DataFrame(datasets)

    def generate_filename(self, metadata: pd.Series, ds: xr.Dataset, ds_filename: pathlib.Path) -> Path:
        """
        Create the output filename for the dataset.

        Parameters
        ----------
        metadata
            Metadata from the file
        ds
            Loaded dataset

        ds_filename:
            Filename of the dataset (Unused)

        Returns
        -------
            The output filename
        """
        return Path("obs4REF") / metadata.key
