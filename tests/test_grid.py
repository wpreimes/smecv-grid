#!/usr/bin/env python
# -*- coding: utf-8 -*-
from smecv_grid.grid import SMECV_Grid_v042
from smecv_grid.grid import SMECV_Grid_v043

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

def test_SMECV_Grid_v043():
    grid = SMECV_Grid_v043()
    gp, dist = grid.find_nearest_gpi(-175.0, -15.0)
    assert gp == 427697
    lon, lat = grid.gpi2lonlat(427697)
    assert lon == -175.625
    assert lat == -15.625
    assert grid.gpi2cell(427697) == 14
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 244243
    assert grid.gpis[0] == 1035360

def test_SMECV_Grid_v043(subset_flag='rainforest'):
    grid = SMECV_Grid_v043(subset_flag=subset_flag)
    gp, dist = grid.find_nearest_gpi(-57.1, 0.1)
    assert gp == 518891
    lon, lat = grid.gpi2lonlat(518891)
    assert lon == -57.125
    assert lat == 0.125
    assert grid.gpi2cell(518891) == 882
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 14851
    assert grid.gpis[0] == 1035360

def test_SMECV_Grid_v043(subset_flag='antarctica'):
    grid = SMECV_Grid_v043(subset_flag=subset_flag)
    gp, dist = grid.find_nearest_gpi(53.3, -67.5)
    assert gp == 129093
    lon, lat = grid.gpi2lonlat(129093)
    assert lon == 53.375
    assert lat == -67.625
    assert grid.gpi2cell(129093) == 1660
    assert grid.gpis.size == 1036800
    assert grid.activegpis.size == 39204
    assert grid.gpis[0] == 1035360
