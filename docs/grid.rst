Loading and using the smecv grid
================================

The smecv_grid package contains the global quarter degree (0.25x0.25 DEG) grid
definition, used for organising the ESA CCI SM and C3S SM data products.
It contains masks for:

 - Land Points (default)
 - Dense Vegetation (AMSR-E LPRMv6 VOD>0.526),
 - Rainforest Areas
 - One or multiple ESA CCI LC classes (reference year 2010)
 - One or multiple Koeppen-Geiger climate classes (`Peel et al. 2007 <https://www.hydrol-earth-syst-sci.net/11/1633/2007/>`_, DOI:10.5194/hess-11-1633-2007).

Grid points are arranged in 5x5 degree cells with 400 grid points per cell.

  .. image:: 5x5_cell_partitioning_cci.png
     :target: 5x5_cell_partitioning_cci.png

For more information on grid definitions, and the usage of grids,we refer to
the `pygeogrids package <https://github.com/TUW-GEO/pygeogrids>`_ in the background.


Loading the grid
----------------

For loading the grid, simply run the following code. Then use it as described
in `pygeogrids <https://github.com/TUW-GEO/pygeogrids>`_

.. code-block:: python

    from smecv_grid import SMECV_Grid_v052
    # Load a global grid
    glob_grid = SMECV_Grid_v052(subset_flag=None)
    # Load a land grid
    land_grid = SMECV_Grid_v052(subset_flag='land')
    # Load a rainforest grid
    rainforest_grid = SMECV_Grid_v052(subset_flag='rainforest')
    # Load grid with points where VOD > 0.526 (based on AMSR-E VOD)
    dense_vegetation_grid = SMECV_Grid_v052(subset_flag='high_vod')
    # Load a grid with points over urban areas
    urban_grid = SMECV_Grid_v052(subset_flag='landcover_class', subset_value=190.)
    # Load a landcover with points over grassland areas
    grassland_grid = SMECV_Grid_v052(subset_flag='landcover_class',
        subset_value=[120., 121., 122., 130., 180.])
    # Load a climate grid with points over tropical areas
    tropical_grid = SMECV_Grid_v052(subset_flag='climate_class',
        subset_value=[0., 1., 2.])