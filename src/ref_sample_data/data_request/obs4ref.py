import pathlib
from pathlib import Path

import climate_ref  # noqa
import pandas as pd
import xarray as xr
from climate_ref_core.dataset_registry import dataset_registry_manager

from ref_sample_data.data_request.base import DataRequest
from ref_sample_data.resample import decimate_curvilinear, decimate_rectilinear


class Obs4REFRequest(DataRequest):
    """
    Fetch the unpublished Obs4MIPs datasets from the PMP registry

    This includes all files that would be downloaded if you ran:
    ```
    ref datasets fetch-obs4ref-data --output-data ...
    ```
    """

    source_type = "obs4REF"

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

    def decimate_dataset(self, dataset: xr.Dataset) -> xr.Dataset | None:
        """
        Downscale the dataset to a smaller size.

        Parameters
        ----------
        dataset
            The dataset to downscale

        Returns
        -------
        xr.Dataset
            The downscaled dataset
        """
        has_latlon = "lat" in dataset.dims and "lon" in dataset.dims
        has_ij = "i" in dataset.dims and "j" in dataset.dims

        if has_latlon:
            assert len(dataset.lat.dims) == 1 and len(dataset.lon.dims) == 1

            result = decimate_rectilinear(dataset)
        elif has_ij:
            # 2d curvilinear grid (generally ocean variables)
            result = decimate_curvilinear(dataset)
        else:
            raise ValueError("Cannot decimate this grid: too many dimensions")

        return result

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
