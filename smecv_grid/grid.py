import os
import pygeogrids.netcdf as ncgrid
from pygeogrids.grids import BasicGrid
import numpy as np


def get_grid_definition_filename(version):
    """
    Get file path of netcdf for the passed version as in the file name.
    """
    grid_info_path = os.path.join(os.path.dirname(__file__),
                                  'definition_files')
    return os.path.join(grid_info_path,
                        'ESA-CCI-SOILMOISTURE-LAND_AND_RAINFOREST_MASK-fv{}.nc'.format(version))


def glob_cci_grid(subset_gpis=None):
    """
    The original cci grid, based on the implementation from v4.2.
    This grid is filted, e.g. based on landcover classes, by gpis (subset)

    Parameters
    ---------
    subset_gpis : np.array
        Subset array that the global grid is filted by.

    Returns:
    -------
    grid : CellGrid
        The (filtered) ESA CCI SM grid
    """
    glob_grid = ncgrid.load_grid(get_grid_definition_filename(version='04.2'),
                               subset_flag=None, subset_value=1.)

    glob_gpis, glob_lons, glob_lats, glob_cells = glob_grid.get_grid_points()

    if isinstance(glob_gpis, np.ma.masked_array):
        glob_gpis = glob_gpis.filled()
    if isinstance(glob_lons, np.ma.masked_array):
        glob_lons = glob_lons.filled()
    if isinstance(glob_lats, np.ma.masked_array):
        glob_lats = glob_lats.filled()


    return BasicGrid(glob_lons, glob_lats, glob_gpis, shape=glob_grid.shape,
                     subset=subset_gpis).to_cell_grid(5.)


def SMECV_Grid_v042(subset_flag='land'):
    """
    Load ECV grid from netcdf file.
    This grid has 2D shape information, also a rainforest mask is included.

    Parameters
    -------
    subset_flag : str or None, optional (default: 'land')
        Select a subset that should be loaded, e.g. 'land' or 'rainforest'

    Returns
    -------
    grid : pygeogrids.CellGrid
        CellGrid object of the selected subset. In Quarter Degree
    """
    if subset_flag is not None:
        subgrid = ncgrid.load_grid(get_grid_definition_filename(version='04.2'),
                                   subset_flag=subset_flag, subset_value=1.)

        subset = subgrid.subset
    else:
        subset = None

    return glob_cci_grid(subset_gpis=subset)


def SMECV_Grid_v052(subset_flag='land', subset_value=1.):
    """
    Load ECV grid from netcdf file.
    This grid has 2D shape information, also a rainforest mask is included.
    The land mask is the same that is defined in gridv4. This version contains
    land cover information as well that can be used for filtering.

    Parameters
    -------
    subset_flag : str or None, optional (default: 'land')
        Select a subset that should be loaded, e.g. land, high_vod, rainforest, cci_lc
    subset_value : float or list, optional (default: 1.)
        Select one or more values of the variable that defines the subset,
        i.e 1. for masks (high_vod, land) or a float or list of floats for one or
        multiple ESA CCI Landcover classes (e.g 190 to load urban points only)

    Returns
    -------
    grid : pygeogrids.CellGrid
        CellGrid object of the selected subset. In Quarter Degree
    """
    if subset_flag is not None:
        subgrid = ncgrid.load_grid(get_grid_definition_filename(version='05.2'),
                                   subset_flag=subset_flag, subset_value=subset_value)

        subset = subgrid.subset
    else:
        subset = None

    return glob_cci_grid(subset_gpis=subset)