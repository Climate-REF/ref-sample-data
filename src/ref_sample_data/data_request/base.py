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

    source_type: str
    time_span: tuple[str, str] | None = None

    def fetch_datasets(self) -> pd.DataFrame:
        """
        Fetch the datasets from the source

        Returns a dataframe of the metadata and paths to the fetched datasets.
        This dataframe must contain at minimimum the following columns:
        * key: A unique identifier for the dataset
        * files: A list of files for the dataset
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


def _deduplicate_datasets(datasets: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate a dataset collection.

    Uses the metadata from the first dataset in each group,
    but expands the time range to the min/max timespan of the group.

    Parameters
    ----------
    datasets
        The dataset collection

    Returns
    -------
    pd.DataFrame
        The deduplicated dataset collection spanning the times requested
    """

    def _deduplicate_group(group: pd.DataFrame) -> pd.DataFrame:
        first = group.iloc[0].copy()
        first.time_start = group.time_start.min()
        first.time_end = group.time_end.max()

        return first

    return datasets.groupby("key").apply(_deduplicate_group, include_groups=False).reset_index()


class IntakeESGFDataRequest(DataRequest):
    """
    A data request that fetches datasets from ESGF using intake-esgf.
    """

    facets: dict[str, str | tuple[str, ...]]
    remove_ensembles: bool

    def fetch_datasets(self) -> pd.DataFrame:
        """Fetch the datasets from the ESGF."""
        cat = ESGFCatalog()

        opts = {}
        if self.time_span:
            opts["file_start"] = self.time_span[0]
            opts["file_end"] = self.time_span[1]
        cat.search(**(opts | self.facets))
        if self.remove_ensembles:
            cat.remove_ensembles()

        path_dict = cat.to_path_dict(prefer_streaming=False, minimal_keys=False, quiet=True)
        merged_df = cat.df.merge(pd.Series(path_dict, name="files"), left_on="key", right_index=True)
        if self.time_span:
            merged_df["time_start"] = self.time_span[0]
            merged_df["time_end"] = self.time_span[1]
        return _deduplicate_datasets(merged_df)
