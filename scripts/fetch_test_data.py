import pathlib
from pathlib import Path
from typing import Annotated

import pooch
import typer
import xarray as xr

from ref_sample_data import CMIP6Request, DataRequest, Obs4MIPsRequest, Obs4REFRequest

OUTPUT_PATH = Path("data")
app = typer.Typer()


def process_sample_data_request(
    request: DataRequest, decimate: bool, output_directory: Path, quiet: bool
) -> None:
    """
    Fetch and create sample datasets

    Parameters
    ----------
    request
        The request to execute

        This may be different types of requests, such as CMIP6Request or Obs4MIPsRequest.
    decimate
        Whether to decimate the datasets
    output_directory
        The directory to write the output to
    quiet
        Whether to suppress progress messages
    """
    datasets = request.fetch_datasets()

    for _, dataset in datasets.iterrows():
        for ds_filename in dataset["files"]:
            ds_orig = xr.open_dataset(ds_filename)

            if decimate:
                ds_decimated = request.decimate_dataset(ds_orig)
            else:
                ds_decimated = ds_orig
            if ds_decimated is None:
                continue

            output_filename = output_directory / request.generate_filename(dataset, ds_decimated, ds_filename)
            output_filename.parent.mkdir(parents=True, exist_ok=True)
            ds_decimated.to_netcdf(output_filename)

    # Regenerate the registry.txt file
    pooch.make_registry(str(OUTPUT_PATH), "registry.txt")


DATASETS_TO_FETCH = [
    # Example metric data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "tas", "tos", "rsut", "rlut", "rsdt"],
            experiment_id=["ssp126", "historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    # ESMValTool ECS data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "rlut", "rsdt", "rsut", "tas"],
            experiment_id=["abrupt-4xCO2", "piControl"],
        ),
        remove_ensembles=True,
        time_span=("0101", "0125"),
    ),
    # ESMValTool TCR data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "tas"],
            experiment_id=["1pctCO2", "piControl"],
        ),
        remove_ensembles=True,
        time_span=("0101", "0180"),
    ),
    # ESMValTool TCRE data
    CMIP6Request(
        facets=dict(
            source_id="MPI-ESM1-2-LR",
            frequency=["fx", "mon"],
            variable_id=["areacella", "fco2antt", "tas"],
            experiment_id=["esm-1pctCO2"],
        ),
        remove_ensembles=True,
        time_span=("1850", "1915"),
    ),
    CMIP6Request(
        facets=dict(
            source_id="MPI-ESM1-2-LR",
            frequency=["fx", "mon"],
            variable_id=["areacella", "tas"],
            experiment_id=["esm-piControl"],
        ),
        remove_ensembles=True,
        time_span=("1850", "1915"),
    ),
    # ESMValTool ZEC data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "tas"],
            experiment_id=["1pctCO2", "esm-1pct-brch-1000PgC"],
        ),
        remove_ensembles=True,
        time_span=("0158", "0268"),
    ),
    # ESMValTool Sea Ice Area Seasonal Cycle data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacello", "siconc"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("1979", "2014"),
    ),
    # ILAMB data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "sftlf", "gpp", "pr"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    # PMP modes of variability data
    CMIP6Request(
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "ts", "psl"],
            experiment_id=["historical", "hist-GHG"],
            variant_label=["r1i1p1f1", "r2i1p1f1"],
        ),
        remove_ensembles=False,
        time_span=("2000", "2025"),
    ),
    # Obs4MIPs AIRS data
    Obs4MIPsRequest(
        facets=dict(
            project="obs4MIPs",
            institution_id="NASA-JPL",
            frequency="mon",
            source_id="AIRS-2-1",
            variable_id="ta",
        ),
        remove_ensembles=False,
        time_span=("2002", "2016"),
    ),
    # All unpublished obs4mips datasets
    Obs4REFRequest(),
]


@app.command()
def create_sample_data(
    decimate: bool = True,
    output: Path = OUTPUT_PATH,
    quiet: Annotated[bool, typer.Argument(envvar="QUIET")] = False,
) -> None:
    """Fetch and create sample datasets"""
    for dataset_requested in DATASETS_TO_FETCH:
        process_sample_data_request(
            dataset_requested, decimate=decimate, output_directory=pathlib.Path(output), quiet=quiet
        )


if __name__ == "__main__":
    app()
