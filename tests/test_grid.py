#!/usr/bin/env python
# -*- coding: utf-8 -*-
from smecv_grid import SMECV_Grid_v042, SMECV_Grid_v052


def test_SMECV_Grid_land():
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
    assert SMECV_Grid_v052() == grid

def test_SMECV_Grid_global():
    grid = SMECV_Grid_v042(subset_flag=None)
    gp, dist = grid.find_nearest_gpi(-99.87, 38.37)
    assert gp == 739040
    lon, lat = grid.gpi2lonlat(739040)
    assert lon == -99.875
    assert lat == 38.375
    assert grid.gpi2cell(739040) == 601
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 1036800
    assert SMECV_Grid_v052(subset_flag=None) == grid

def test_SMECV_Grid_rainforest():
    grid = SMECV_Grid_v042(subset_flag='rainforest')
    gp, dist = grid.find_nearest_gpi(27.44, -0.33)
    assert gp == 516349
    lon, lat = grid.gpi2lonlat(516349)
    assert lon == 27.375
    assert lat == -0.375
    assert grid.gpi2cell(516349) == 1493
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 14851
    assert SMECV_Grid_v052(subset_flag='rainforest') == grid

def test_SMECV_Grid_v052_denseveg():
    grid = SMECV_Grid_v052(subset_flag='high_vod')
    gp, dist = grid.find_nearest_gpi(27.44, -0.33)
    assert gp == 516349
    lon, lat = grid.gpi2lonlat(516349)
    assert lon == 27.375
    assert lat == -0.375
    assert grid.gpi2cell(516349) == 1493
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 33082
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 272127

def test_SMECV_Grid_v052_urban():
    grid = SMECV_Grid_v052(subset_flag='landcover_class', subset_value=190.)
    gp, dist = grid.find_nearest_gpi(139.65, 35.68)
    assert gp == 724158
    lon, lat = grid.gpi2lonlat(724158)
    assert lon == 139.625
    assert lat == 35.625
    assert grid.gpi2cell(724158) == 2293
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 421
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 300820

def test_SMECV_Grid_v052_desert():
    grid = SMECV_Grid_v052(subset_flag='landcover_class', subset_value=[190., 200.])
    gp, dist = grid.find_nearest_gpi(9.375, 24.125)
    assert dist == 0.
    assert gp == 657397
    lon, lat = grid.gpi2lonlat(657397)
    assert lon == 9.375
    assert lat == 24.125
    assert grid.gpi2cell(657397) == 1354
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 421+31162
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 232835

def test_SMECV_Grid_v052_tropical():
    grid = SMECV_Grid_v052(subset_flag='climate_class', subset_value=[0., 1., 2.])
    gp, dist = grid.find_nearest_gpi(-66.125, -8.125)
    assert gp == 471335
    assert dist == 0.
    lon, lat = grid.gpi2lonlat(471335)
    assert lon == -66.125
    assert lat == -8.125
    assert grid.gpi2cell(471335) == 808
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 36949
    assert grid.gpis[0] == 0
    assert grid.activegpis[0] == 366610
