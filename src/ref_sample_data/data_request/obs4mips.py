import os.path
import pathlib
from pathlib import Path
from typing import Any

import pandas as pd

from ref_sample_data.data_request.base import DecimateMixin, IntakeESGFMixin
from ref_sample_data.data_request.cmip6 import timerange_from_filename


class Obs4MIPsRequest(IntakeESGFMixin, DecimateMixin):
    """
    Represents a Obs4MIPs dataset request
    """

    source_type = "obs4MIPs"

    obs4mips_path_items = (
        "activity_id",
        "institution_id",
        "source_id",
        "variable_id",
        "grid_label",
    )

    obs4mips_filename_paths = (
        "variable_id",
        "source_id",
        "grid_label",
    )

    def __init__(self, facets: dict[str, Any], remove_ensembles: bool, time_span: tuple[str, str] | None):
        self.avail_facets = [
            "activity_id",
            "institution_id",
            "source_id",
            "frequency",
            "variable_id",
            "grid_label",
            "version",
            "data_node",
        ]

        self.facets = facets
        self.remove_ensembles = remove_ensembles
        self.time_span = time_span

        super().__init__(remove_ensembles, time_span)

        self.obs4mips_path_items = [
            "activity_id",
            "institution_id",
            "source_id",
            "variable_id",
            "grid_label",
        ]

        self.obs4mips_filename_paths = [
            "variable_id",
            "source_id",
            "grid_label",
        ]

        assert all(key in self.avail_facets for key in self.obs4mips_path_items), "Error message"
        assert all(key in self.avail_facets for key in self.obs4mips_filename_paths), "Error message"

    def generate_filename(self, metadata: pd.Series, ds_filename: pathlib.Path) -> Path:
        """
        Create the output filename for the dataset.

        Parameters
        ----------
        ds
            Loaded dataset
        ds_filename
            Filename of the dataset

        Returns
        -------
            The output filename
        """
        output_path = (
            Path(os.path.join(*[metadata[item] for item in self.obs4mips_path_items]))
            / f"v{metadata['version']}"
        )
        if ds_filename.name.split("_")[0] == ds.variable_id:
            filename_prefix = "_".join([metadata[item] for item in self.obs4mips_filename_paths])
        else:
            filename_prefix = ds_filename.name.split("_")[0] + "_"
            filename_prefix += "_".join(
                [metadata[item] for item in self.obs4mips_filename_paths if item != "variable_id"]
            )
        timerange = timerange_from_filename(ds_filename, metadata)
        if timerange:
            filename_prefix = f"{filename_prefix}_{timerange}"
        return output_path / f"{filename_prefix}.nc"
