#!/usr/bin/env python
# -*- coding: utf-8 -*-
from smecv_grid.grid import SMECV_Grid_v042


def test_SMECV_Grid_v042():
    grid = SMECV_Grid_v042()
    gp, dist = grid.find_nearest_gpi(-99.87, 38.37)
    assert gp == 739040
    lon, lat = grid.gpi2lonlat(739040)
    assert lon == -99.875
    assert lat == 38.375
    assert grid.gpi2cell(739040) == 601
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 244243
    assert grid.gpis[0] == 1035360
