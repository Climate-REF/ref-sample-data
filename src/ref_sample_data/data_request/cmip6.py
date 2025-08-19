import os.path
import pathlib
import re
from pathlib import Path
from typing import Any

import pandas as pd

from ref_sample_data.data_request.base import DecimateMixin, IntakeESGFMixin


def to_pandas_time(timestamp: str) -> pd.Timestamp:
    """Convert a string to a pandas timestamp.

    timestamp
        The timestamp

    Returns
    -------
        The timestamp
    """
    year_end = 4
    month_end = 6
    day_end = 8
    year = int(timestamp[:year_end])
    month = int(timestamp[year_end:month_end]) if len(timestamp) > year_end else 1
    day = int(timestamp[month_end:day_end]) if len(timestamp) > month_end else 1
    return pd.Timestamp(year=year, month=month, day=day)


def timerange_from_filename(ds_filename: Path, metadata: pd.Series) -> str:
    """
    Extract a timerange from a filename and adjust it based on the request.

    Parameters
    ----------
    ds_filename
        Input filename
    metadata
        Metadata describing the start and end time of the request

    Returns
    -------
        A timerange string
    """
    date = "[0-9]{4}([01][0-9]([0-3][0-9])?)?"
    match = re.search(f"(?P<start>{date})-(?P<end>{date})", ds_filename.stem.split("_")[-1])
    if match:
        start_date, end_date = match.group("start"), match.group("end")
        start = max(to_pandas_time(start_date), to_pandas_time(metadata.time_start))
        end = min(to_pandas_time(end_date), to_pandas_time(metadata.time_end))
        timerange = f"{start.strftime("%Y%m")}-{end.strftime("%Y%m")}"
    else:
        timerange = ""
    return timerange


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

    def generate_filename(self, metadata: pd.Series, ds_filename: pathlib.Path) -> Path:
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
        timerange = timerange_from_filename(ds_filename, metadata)
        if timerange:
            filename_prefix = f"{filename_prefix}_{timerange}"
        return output_path / f"{filename_prefix}.nc"
