# -*- coding: utf-8 -*-
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'

from smecv_grid.grid import SMECV_Grid_v042, SMECV_Grid_v052