import pathlib
from pathlib import Path

import pandas as pd
import pooch
import typer
import xarray as xr
from loguru import logger

from ref_sample_data import CMIP6Request, DataRequest, Obs4REFRequest

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


def process_sample_data_request(
    processed_datasets: pd.DataFrame,
    request: DataRequest,
    decimate: bool,
    output_directory: Path,
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

    Returns
    -------
        The processed datasets from this request
    """
    logger.info(f"Resolving request: {request.id}")
    datasets = request.fetch_datasets()
    items = []

    for _, dataset in datasets.iterrows():
        match = _get_match(processed_datasets, request.source_type, dataset.key)

        # Check if the dataset has already been processed and can be skipped
        if match is not None and request.time_span is not None:
            # Dataset has already been processed and a time span was specified
            # Check if the dataset already covers the requested time span
            if int(match.time_start) <= int(dataset["time_start"]) and int(match.time_end) >= int(
                dataset["time_end"]
            ):
                # Already have a dataset that covers the requested time span
                logger.info(
                    f"Skipping regenerating {dataset.key} as it already covers the requested time span"
                )
                continue

            # Update the request to match the superset of the time spans
            time_start = (
                dataset["time_start"] if dataset["time_start"] < match.time_start else match.time_start
            )
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

        item = {
            "source_type": request.source_type,
            "key": dataset.key,
            "files": output_filenames,
        }
        if request.time_span is not None:
            item["time_start"] = request.time_span[0]
            item["time_end"] = request.time_span[1]

        items.append(item)

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
            variable_id=["areacella", "tas", "tos", "rsut", "rlut", "rsdt"],
            experiment_id=["ssp126", "historical"],
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


@app.command()
def create_sample_data(
    decimate: bool = True,
    output: Path = OUTPUT_PATH,
    only: list[str] | None = None,
) -> None:
    """Fetch and create sample datasets"""
    processed_datasets = pd.DataFrame(columns=["source_type", "key", "files", "time_start", "time_end"])

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
        )
        # Remove duplicate source_type and key values, but keep the latest one
        processed_datasets = (
            pd.concat([processed_datasets, new_datasets], ignore_index=True)
            .drop_duplicates(subset=["source_type", "key"], keep="last")
            .reset_index(drop=True)
        )


if __name__ == "__main__":
    app()
