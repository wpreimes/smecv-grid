import os
import pygeogrids.netcdf as ncgrid


def get_grid_definition_filename():
    """
    Get file path of netcdf
    """
    grid_info_path = os.path.join(os.path.dirname(__file__),
                                  'definition_files')
    return os.path.join(grid_info_path,
                        'ESA-CCI-SOILMOISTURE-LAND_AND_RAINFOREST_MASK-fv04.2.nc')


def SMECV_Grid_v042(subset_flag='land'):
    """
    Load ECV grid from netcdf file.
    This grid has 2D shape information, also a rainforest mask is included.
    The land mask is the same that is defined in gridv4.
    Returns
    -------
    grid : pygeogrids.CellGrid
        CellGrid object
    """
    return ncgrid.load_grid(get_grid_definition_filename(),
                            subset_flag=subset_flag)
