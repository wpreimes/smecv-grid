Loading and using the smecv grid
================================


The smecv_grid package contains the global quarter degree (0.25x0.25 DEG) grid
definition, used for organising the ESA CCI SM and C3S SM data products.
It contains masks for land points (default) and dense vegetation.
Grid points are arranged in 5x5 degree cells with 400 grid points per cell.

  .. image:: 5x5_cell_partitioning_cci.png
     :target: 5x5_cell_partitioning_cci.png

For more information on grid definitions, and the usage of grids,we refer to the `pygeogrids package
<https://github.com/TUW-GEO/pygeogrids>`_ in the background.

Loading the grid
----------------

For loading the grid, simply run the following code. Then use it as described
in `pygeogrids <https://github.com/TUW-GEO/pygeogrids>`_

.. code-block:: python

    from smecv_grid.grid import SMECV_Grid_v042
    land_grid = SMECV_Grid_v042(subset_flag='land')
    rainforest_grid = SMECV_Grid_v024(subset_flag='rainforest')

