==========
smecv_grid
==========

.. image:: https://travis-ci.org/TUW-GEO/smecv-grid.svg?branch=master
    :target: https://travis-ci.org/TUW-GEO/smecv-grid

.. image:: https://coveralls.io/repos/github/TUW-GEO/smecv-grid/badge.svg?branch=master
    :target: https://coveralls.io/github/TUW-GEO/smecv-grid?branch=master

.. image:: https://readthedocs.org/projects/smecv-grid/badge/?version=latest
    :target: http://smecv-grid.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/smecv-grid.svg
    :target: https://badge.fury.io/py/smecv-grid

Grid definition of the Discrete Global Grid (DGG) used for the creation of the CCI soil moisture products and
the Copernicus Climate Change Service products.

Full Documentation
==================
For the full documentation, click `here <http://smecv-grid.readthedocs.io/en/latest>`_,
or follow the docs-badge at the top.

Installation
============

The package is available on pypi and can be installed via pip:

.. code::

    pip install ecmwf_models


Loading and using the smecv grid
================================


The smecv_grid package contains the global quarter degree (0.25x0.25 DEG) grid
definition, used for organising the ESA CCI SM and C3S SM data products.
It contains masks for land points (default), dense vegetation (VOD>0.526),
rainforest areas and one or multiple ESA CCI LC classes (reference year 2010).
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
    # Load a land grid
    land_grid = SMECV_Grid_v052(subset_flag='land')
    # Load a rainforest grid
    rainforest_grid = SMECV_Grid_v052(subset_flag='rainforest')
    # Load grid with points where VOD > 0.526
    dense_vegetation_grid = SMECV_Grid_v052(subset_flag='high_vod')
    # Load a grid with points over urban areas
    urban_grid = SMECV_Grid_v052(subset_flag='landcover_class', subset_value=190.)
    # Load a grid with points over grassland areas
    grassland_grid = SMECV_Grid_v052(subset_flag='landcover_class',
        subset_value=[120., 121., 122., 130., 180.])

Description
===========

The DGG is a regular 0.25 degree grid utilizing cell partitioning.


Note
====

This project has been set up using PyScaffold 2.5.11. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
