import numpy as np
import xarray as xr
import xcdat
import xesmf


def _calculate_2d_cell_bounds(
    points: np.ndarray,
    i: int,
    j: int,
) -> list[float]:
    cell_center = points[j, i]
    if i == 0:
        di = points[j, i + 1] - cell_center
    else:
        di = cell_center - points[j, i - 1]
    if j == 0:
        dj = points[j + 1, i] - cell_center
    else:
        dj = cell_center - points[j - 1, i]

    return np.asarray(
        [
            cell_center - dj / 2 - di / 2,
            cell_center - dj / 2 + di / 2,
            cell_center + dj / 2 + di / 2,
            cell_center + dj / 2 - di / 2,
        ]
    ).tolist()


def decimate_rectilinear(dataset: xr.Dataset) -> xr.Dataset:
    """
    Decimate a rectilinear gridded dataset.

    Parameters
    ----------
    dataset
        Dataset to decimate

    Returns
    -------
        Resampled dataset with a 10x10 degree grid
    """
    # Decimate the dataset, but update the bounds
    # 10x10 degree grid
    output_grid = xcdat.create_uniform_grid(-90, 90, 10, 0, 359, 10)
    regrid = xesmf.Regridder(dataset, output_grid, "bilinear", periodic=True)
    result = regrid(dataset.copy())
    result = result.bounds.add_bounds("Y").bounds.add_bounds("X")
    # Restore attributes and add dataarrays that have not been regridded.
    for k, v in dataset.data_vars.items():
        if k in result:
            result[k].attrs = v.attrs
        else:
            result[k] = v
    for k, v in dataset.coords.items():
        result[k].attrs = v.attrs
    result.attrs = dataset.attrs
    return result


def decimate_curvilinear(dataset: xr.Dataset, factor: int = 10) -> xr.Dataset:
    """
    Decimate a curvilinear gridded dataset.

    Generally ocean variables use a curvilinear grid where the lat/lon coordinates are 2D arrays.

    Parameters
    ----------
    dataset
        Dataset to decimate
    factor
        Factor to decimate the dataset

        10 would result in a dataset with 1/10th the resolution

    Returns
    -------
        Resampled dataset
    """
    assert factor >= 1
    result = dataset.interp(i=dataset.i[::factor]).interp(j=dataset.j[::factor])
    result.coords["i"].values[:] = np.arange(len(result.i))
    result.coords["j"].values[:] = np.arange(len(result.j))

    # Update the bounds of the cells
    latitude_points = result.latitude.values
    longitude_points = result.longitude.values
    for j in result.j:
        for i in result.i:
            result.vertices_latitude[j, i] = _calculate_2d_cell_bounds(latitude_points, i, j)
            result.vertices_longitude[j, i] = _calculate_2d_cell_bounds(longitude_points, i, j)

    return result
