import os
import pathlib
import tempfile
from pathlib import Path

import pandas as pd
import pooch
import requests
import xarray as xr
from loguru import logger

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
    branch_or_tag: str = "main"
    """
    The branch or tag to use for fetching the dataset registry

    This defaults to `main` but can be set to a specific tag or branch name to pin a different
    version of the datasets.
    """

    def fetch_datasets(self) -> pd.DataFrame:
        """
        Fetch the datasets from the source

        Returns a dataframe of the metadata and paths to the fetched datasets.
        """
        # This mimics how a registry is set up in climate_ref_core.dataset_registry
        DATASET_URL = os.environ.get("REF_DATASET_URL", default="https://obs4ref.climate-ref.org")

        registry = pooch.create(
            path=pooch.os_cache("climate_ref"),
            base_url=DATASET_URL,
            retry_if_failed=10,
            env="REF_DATASET_CACHE_DIR",
        )
        registry_url = (
            f"https://raw.githubusercontent.com/Climate-REF/climate-ref/refs/heads/{self.branch_or_tag}"
            f"/packages/climate-ref/src/climate_ref/dataset_registry/obs4ref_reference.txt"
        )
        response = requests.get(registry_url, timeout=30)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as tmpfile:
            tmpfile.write(response.text)
            registry.load_registry(tmpfile.name)
        logger.info(f"Loaded dataset registry from {registry_url}: {len(registry.registry)} entries")
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
