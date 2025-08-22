import inspect
import logging
import pathlib
from pathlib import Path

import joblib
import pandas as pd
import pooch
import typer
import xarray as xr
from loguru import logger

from ref_sample_data import CMIP6Request, DataRequest, Obs4MIPsRequest, Obs4REFRequest

OUTPUT_PATH = Path("data")
app = typer.Typer()


def _get_match(dataset: pd.DataFrame, source_type: str, key: str) -> pd.Series | None:
    """
    Get the matching dataset from the processed datasets

    Parameters
    ----------
    dataset
        The dataset to match against
    source_type
        The source type to match against
    key
        The key to match against

    Returns
    -------
        The matching dataset
    """
    matches = dataset.loc[(dataset.source_type == source_type) & (dataset.key == key)]
    if len(matches) > 1:
        raise ValueError(f"Found multiple datasets with the same key: {key}")

    if len(matches) == 0:
        return None
    return matches.iloc[0]


def _process_dataset(
    processed_datasets: pd.DataFrame,
    dataset: pd.Series,
    request: DataRequest,
    decimate: bool,
    output_directory: Path,
) -> list[dict[str, str]]:
    match = _get_match(processed_datasets, request.source_type, dataset.key)

    # Check if the dataset has already been processed and can be skipped
    if match is not None and request.time_span is not None:
        # Dataset has already been processed and a time span was specified
        # Check if the dataset already covers the requested time span
        if int(match.time_start) <= int(dataset["time_start"]) and int(match.time_end) >= int(
            dataset["time_end"]
        ):
            # Already have a dataset that covers the requested time span
            logger.info(f"Skipping regenerating {dataset.key} as it already covers the requested time span")
            return []

        # Update the request to match the superset of the time spans
        time_start = dataset["time_start"] if dataset["time_start"] < match.time_start else match.time_start
        time_end = dataset["time_end"] if dataset["time_end"] > match.time_end else match.time_end
        request.time_span = (str(time_start), str(time_end))

        logger.info(f"Regenerating dataset with new time span: {dataset.key} {request.time_span}")
        for file in match.files:
            file_path = pathlib.Path(file)
            if file_path.exists():
                logger.info(f"Removing existing file: {file}")
                file_path.unlink()

    output_filenames = []
    for ds_filename in dataset["files"]:
        try:
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
            output_filenames.append(output_filename)
        except:
            logger.exception(f"Failed to process dataset {ds_filename}")
            raise

    item = {
        "source_type": request.source_type,
        "key": dataset.key,
        "files": output_filenames,
    }
    if request.time_span is not None:
        item["time_start"] = request.time_span[0]
        item["time_end"] = request.time_span[1]

    return [item]


def process_sample_data_request(
    processed_datasets: pd.DataFrame,
    request: DataRequest,
    decimate: bool,
    output_directory: Path,
    n_jobs: int | None = -1,
) -> pd.DataFrame:
    """
    Fetch and create sample datasets

    Parameters
    ----------
    processed_datasets
        The datasets that have already been processed
    request
        The request to execute

        This may be different types of requests, such as CMIP6Request or Obs4MIPsRequest.
    decimate
        Whether to decimate the datasets
    output_directory
        The directory to write the output to
    n_jobs
        Number of jobs to run in parallel
        If None, run sequentially.

    Returns
    -------
        The processed datasets from this request
    """
    logger.info(f"Resolving request: {request.id}")
    datasets = request.fetch_datasets()

    # Process all the datasets in parallel
    if n_jobs is None:
        logger.info("Processing datasets sequentially as n_jobs is None")
        items = [
            _process_dataset(processed_datasets, dataset, request, decimate, output_directory)
            for _, dataset in datasets.iterrows()
        ]
    else:
        items = joblib.Parallel(n_jobs=n_jobs)(
            joblib.delayed(_process_dataset)(processed_datasets, dataset, request, decimate, output_directory)
            for _, dataset in datasets.iterrows()
        )
    # Flatten the list of lists
    items = [item for sublist in items for item in sublist]

    # Regenerate the registry.txt file
    pooch.make_registry(str(OUTPUT_PATH), "registry.txt")
    return pd.DataFrame(items)


DATASETS_TO_FETCH = [
    # Example metric data
    CMIP6Request(
        id="example-metric",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=[
                "areacella",
                "tas",
                "tos",
                "rsut",
                "rsdt",
            ],
            experiment_id=["ssp126", "historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    CMIP6Request(
        id="example-metric",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["mon"],
            variable_id=["rlut"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    # ESMValTool Climate at global warmings levels data
    CMIP6Request(
        id="esmvaltool-climate-at-global-warmings-levels",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "pr", "tas"],
            experiment_id=["ssp126", "historical"],
        ),
        remove_ensembles=True,
        time_span=("1850", "2100"),
    ),
    # ESMValTool Cloud radiative effects
    CMIP6Request(
        id="esmvaltool-cloud-radiative-effects",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "rlut", "rlutcs", "rsut", "rsutcs"],
            experiment_id="historical",
        ),
        remove_ensembles=True,
        time_span=("2005", "2014"),
    ),
    # ESMValTool cloud scatterplots
    CMIP6Request(
        id="esmvaltool-cloud-scatterplots-cmip6",
        facets=dict(
            source_id="CESM2",
            table_id=["fx", "Amon"],
            variable_id=[
                "areacella",
                "cli",
                "clivi",
                "clt",
                "clwvi",
                "pr",
                "rlut",
                "rlutcs",
                "rsut",
                "rsutcs",
                "ta",
            ],
            experiment_id="historical",
        ),
        remove_ensembles=True,
        time_span=("2007", "2014"),
    ),
    Obs4MIPsRequest(
        id="esmvaltool-cloud-scatterplots-obs4mips",
        facets=dict(
            project="obs4MIPs",
            source_id="ERA-5",
            frequency="mon",
            variable_id="ta",
        ),
        remove_ensembles=False,
        time_span=("2007", "2015"),
    ),
    # ESMValTool ECS data
    CMIP6Request(
        id="esmvaltool-ecs",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "rlut", "rsdt", "rsut", "tas"],
            experiment_id=["abrupt-4xCO2", "piControl"],
        ),
        remove_ensembles=True,
        time_span=("0101", "0125"),
    ),
    # ESMValTool ENSO data
    CMIP6Request(
        id="esmvaltool-enso",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=[
                "areacello",
                "pr",
                "tos",
                "tauu",
            ],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("1850", "2014"),
    ),
    # ESMValTool Historical data
    CMIP6Request(
        id="esmvaltool-historical-cmip6",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=[
                "areacella",
                "hus",
                "pr",
                "psl",
                "tas",
                "ua",
            ],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("1980", "2014"),
    ),
    Obs4MIPsRequest(
        id="esmvaltool-historical-obs4mips",
        facets=dict(
            project="obs4MIPs",
            source_id="ERA-5",
            variable_id=[
                "psl",
                "tas",
                "ua",
            ],
        ),
        remove_ensembles=False,
        time_span=("1980", "2014"),
    ),
    # ESMValTool TCR data
    CMIP6Request(
        id="esmvaltool-tcr",
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
        id="esmvaltool-tcre",
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
        id="esmvaltool-tcre-mpi",
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
        id="esmvaltool-zec",
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
        id="esmvaltool-sea-ice-area-seasonal-cycle",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacello", "siconc"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("1979", "2014"),
    ),
    # ESMValTool Sea Ice Sensitivity data
    CMIP6Request(
        id="esmvaltool-sea-ice-sensitivity",
        facets=dict(
            source_id=["ACCESS-ESM1-5", "CanESM5", "HadGEM3-GC31-LL"],
            frequency=["fx", "mon"],
            variable_id=["areacella", "areacello", "siconc", "tas"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("1979", "2014"),
    ),
    CMIP6Request(
        id="esmvaltool-sea-ice-sensitivity",
        facets=dict(
            source_id=["HadGEM3-GC31-LL"],
            frequency=["fx"],
            variable_id=["areacella", "areacello"],
            experiment_id=["piControl"],
        ),
        remove_ensembles=False,
        time_span=None,
    ),
    # ILAMB data
    CMIP6Request(
        id="ilamb-data",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacella", "sftlf", "gpp", "pr", "tas", "mrro", "mrsos", "cSoil", "lai"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    # ILAMB data, but a model that has a fire and snow model
    CMIP6Request(
        id="ilamb-data-fire-snow",
        facets=dict(
            source_id="CESM2",
            frequency=["mon"],
            variable_id=["areacella", "burntFractionAll", "snc"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    # ILAMB data, nbp requires a longer time span
    CMIP6Request(
        id="ilamb-data-nbp",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["mon"],
            variable_id=["nbp"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("1850", "2015"),
    ),
    # IOMB data
    CMIP6Request(  # Already provided by the ESMValTool ENSO request.
        id="iomb-data",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["areacello", "tos"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    CMIP6Request(
        id="iomb-data-2",
        facets=dict(
            source_id="ACCESS-ESM1-5",
            frequency=["fx", "mon"],
            variable_id=["sftof", "sos", "msftmz"],
            experiment_id=["historical"],
        ),
        remove_ensembles=True,
        time_span=("2000", "2025"),
    ),
    # PMP modes of variability data
    CMIP6Request(
        id="pmp-modes-of-variability",
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
    # # Obs4MIPs AIRS data
    # Obs4MIPsRequest(
    #     facets=dict(
    #         project="obs4MIPs",
    #         institution_id="NASA-JPL",
    #         frequency="mon",
    #         source_id="AIRS-2-1",
    #         variable_id="ta",
    #     ),
    #     remove_ensembles=False,
    #     time_span=("2002", "2016"),
    # ),
    # All unpublished obs4mips datasets
    Obs4REFRequest(),
]


# Copied from https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    """Intercepts standard logging messages and redirects them to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record."""
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth + 2, exception=record.exc_info).log(level, record.getMessage())


@app.command()
def create_sample_data(
    decimate: bool = True,
    output: Path = OUTPUT_PATH,
    only: list[str] | None = None,
    n_jobs: int = -1,
    run_sequentially: bool = False,
) -> None:
    """Fetch and create sample datasets"""
    logging.basicConfig(handlers=[InterceptHandler()], force=True)
    processed_datasets = pd.DataFrame(columns=["source_type", "key", "files", "time_start", "time_end"])

    if run_sequentially:
        n_jobs = None
        logger.info("Running in sequential mode, setting n_jobs to None")

    for dataset_requested in DATASETS_TO_FETCH:
        if only:
            if dataset_requested.id not in only:
                logger.info(f"Skipping dataset {dataset_requested.id} as it is not in the 'only' list")
                continue
        # Process the request
        new_datasets = process_sample_data_request(
            processed_datasets,
            dataset_requested,
            decimate=decimate,
            output_directory=pathlib.Path(output),
            n_jobs=n_jobs,
        )
        # Remove duplicate source_type and key values, but keep the latest one
        processed_datasets = (
            pd.concat([processed_datasets, new_datasets], ignore_index=True)
            .drop_duplicates(subset=["source_type", "key"], keep="last")
            .reset_index(drop=True)
        )


if __name__ == "__main__":
    app()
