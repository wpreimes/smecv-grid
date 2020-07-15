# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2020, TU Wien
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import pygeogrids.netcdf as ncgrid
from pygeogrids.grids import BasicGrid, CellGrid, lonlat2cell
import numpy as np
import warnings

def get_grid_definition_filename(version:str) -> str:
    """
    Get file path of netcdf for the passed version as in the file name.
    """
    grid_info_path = os.path.join(os.path.dirname(__file__),
                                  'definition_files')
    return os.path.join(grid_info_path,
                        'ESA-CCI-SOILMOISTURE-LAND_AND_RAINFOREST_MASK-fv{}.nc'.format(version))

def safe_arange(start:float, stop:float, step:float) -> np.array:
    """ Version of np.aranage that can handle small step sizes """

    f_step = (1. / float(step))
    vals = np.arange(float(start) * f_step, float(stop) * f_step, float(step) * f_step)

    return vals / f_step

def meshgrid(resolution=0.25, cellsize=5., flip_lats=False):
    """
    Create arrays that are used as input to create a global smecv_grid.

    Parameters
    ----------
    resolution : float, optional (default: 0.25)
        Grid resolution in lon/lat dimension, degrees
    cellsize : float, optional (default: 0.25)
        Cell resolution in lon/lat dimension, degrees
    flip_lats : bool, optional (default: False)
        Flip the lats, gpis and cells stored in the grid. This means that
        each lonlat will still have the correct gpi/cell number, but self.arrgpi[gpi]
        will NOT return the correct gpi, i.e the gpi can't be used to index the
        arrays. This option was used in grid v4 and changed afterwards and is
        kept for backwards compatibility. Should NOT be used anymore.
        ------------------------------------------------------------------------
        e.g. SMECV_Grid_v042(None).activegpis[0] is 1035360
        and SMECV_Grid_v042(None).activearrlat[0] is 89.875
        but SMECV_Grid_v052(None).activegpis[0] is 0,
        and SMECV_Grid_v052(None).activearrlat[0] is -89.875
        e.g. grid.find_nearest_gpi(-100.375,38.375) will return in both versions
        (739038, 0.0) but SMECV_Grid_v042(None).arrlat[739038] is -38.375 and
        not 38.375 as it is in v5.

    Returns
    -------
    lon : np.array
        Global flattened longitudes for ALL gpis
    lat : np.array
        Global flattened latitudes for ALL gpis
    gpis : np.array
        Global gpis, with gpi 0 close to (-180,-90)
    cells : np.array
        Global cells, with cell 0 starting close to (-180,-90)
    shape : tuple
        rows and columns, i.e. unique lats, lons in the global grid
    """

    glob_lons = safe_arange(-180 + resolution / 2, 180 + resolution / 2, resolution)
    glob_lats = safe_arange(-90 + resolution / 2, 90 + resolution / 2, resolution)

    lon, lat = np.meshgrid(glob_lons, glob_lats)

    shape = (len(glob_lats), len(glob_lons))

    gpis = np.arange(shape[0]*shape[1]).reshape(shape)

    if flip_lats:
        lat = np.flipud(lat)
        gpis = np.flipud(gpis)

    lat = lat.flatten()
    lon = lon.flatten()
    gpis = gpis.flatten()

    cells = lonlat2cell(lon.flatten(), lat.flatten(), cellsize, None, None)

    return lon, lat, gpis, cells, shape

def SMECV_Grid_v042(subset_flag='land'):
    """
    Load a SMECV Grid as used in the production of ESA CCI SM v4.
    This grid has 2D shape information, also a rainforest mask is included.

    Parameters
    ----------
    subset_flag : str or None, optional (default: 'land')
        Select a subset that should be loaded, e.g. 'land' or 'rainforest'

    Returns
    -------
    grid : pygeogrids.CellGrid
        CellGrid object of the selected subset. In Quarter Degree resolution.
    """

    warnings.warn("SMECV Grid v4 is deperecated. Please use a newer grid version.",
                  DeprecationWarning)


    lon, lat, gpis, cells, shape = meshgrid(resolution=0.25, cellsize=5.,
                                        flip_lats=True)

    if subset_flag is not None:
        subset_grid = ncgrid.load_grid(get_grid_definition_filename(version='04.2'),
                                   subset_flag=subset_flag, subset_value=1.)
        subset = subset_grid.subset
        shape = (len(subset),)
    else:
        subset = None

    return CellGrid(lon, lat, gpis=gpis, subset=subset, cells=cells, shape=shape)


class SMECV_Grid_v052(CellGrid):
    """
    Create global SMECV Grid.
    This grid has 2D shape information, also a rainforest mask is included.
    The land mask is the same that is defined in gridv4. This version contains
    land cover information as well, that can be used for filtering.

    Parameters
    ----------

    subset_flag : str or None, optional (default: 'land')
        Select a subset that should be loaded, e.g. land, high_vod, rainforest, cci_lc
    subset_value : float or list, optional (default: 1.)
        Select one or more values of the variable that defines the subset,
        i.e 1. for masks (high_vod, land) or a float or list of floats for one or
        multiple ESA CCI Landcover classes (e.g 190 to load urban points only)
    origin: {'bl', 'tl'}, optional (default: 'tl')
        Wheather the grid point index starts in the top left (tl) or the bottom
        left ('bl') corner
    """

    def __init__(self, subset_flag='land', subset_value=1., cellsize=5.):

        self.resolution = 0.25
        self.cellsize = cellsize

        lon, lat, gpis, cells, shape = \
            meshgrid(resolution=self.resolution, cellsize=self.cellsize,
                     flip_lats=False)

        if subset_flag is not None:
            subset_grid = ncgrid.load_grid(get_grid_definition_filename(version='05.2'),
                                           subset_flag=subset_flag, subset_value=subset_value)

            if isinstance(subset_grid.activegpis, np.ma.masked_array):
                subset = subset_grid.activegpis.data
            else:
                subset = subset_grid.activegpis
            shape = (len(subset),)
        else:
            subset = None

        super(SMECV_Grid_v052, self).__init__(lon=lon, lat=lat, gpis=gpis,
                                              cells=cells, subset=subset,
                                              shape=shape)

    def subgrid_from_bbox(self, min_lon, min_lat, max_lon, max_lat):
        """
        Create a subgrid from points within a given bounding box.

        Parameters
        ----------
        min_lon : float
            Lower left corner longitude
        min_lat: float
            Lower left corner latitude
        max_lon : float
            Upper right corner longitude
        max_lat : float
            Upper right corner latitude

        Returns
        -------
        subgrid : {BasicGrid,CellGrid}
            Subgrid of the global grid within the bounding box.
        """

        bbox_gpis = self.get_bbox_grid_points(min_lat, max_lat,
                                              min_lon, max_lon)

        bbox_grid = self.subgrid_from_gpis(bbox_gpis) # type: {BasicGrid,CellGrid}

        return bbox_grid