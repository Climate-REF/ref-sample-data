import pathlib
from typing import Protocol

import pandas as pd
import xarray as xr
from intake_esgf import ESGFCatalog


class DataRequest(Protocol):
    """
    Represents a request for a dataset

    A polymorphic association is used to capture the different types of datasets as each
    dataset type may have different metadata fields and may need to be handled
    differently to generate the sample data.
    """

    def fetch_datasets(self) -> pd.DataFrame:
        """
        Fetch the datasets from the source

        Returns a dataframe of the metadata and paths to the fetched datasets.
        """
        ...

    def decimate_dataset(self, dataset: xr.Dataset) -> xr.Dataset | None:
        """Downscale the dataset to a smaller size."""
        ...

    def generate_filename(
        self, metadata: pd.Series, ds: xr.Dataset, ds_filename: pathlib.Path
    ) -> pathlib.Path:
        """Create the output filename for the dataset."""
        ...


class IntakeESGFDataRequest(DataRequest):
    """
    A data request that fetches datasets from ESGF using intake-esgf.
    """

    facets: dict[str, str | tuple[str, ...]]
    remove_ensembles: bool
    time_span: tuple[str, str]

    def fetch_datasets(self) -> pd.DataFrame:
        """Fetch the datasets from the ESGF."""
        cat = ESGFCatalog()

        cat.search(**self.facets)
        if self.remove_ensembles:
            cat.remove_ensembles()

        path_dict = cat.to_path_dict(prefer_streaming=False, minimal_keys=False, quiet=True)
        merged_df = cat.df.merge(pd.Series(path_dict, name="files"), left_on="key", right_index=True)
        if self.time_span:
            merged_df["time_start"] = self.time_span[0]
            merged_df["time_end"] = self.time_span[1]
        return merged_df
