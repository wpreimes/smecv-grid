import numpy as np
import numpy.testing as nptest
import warnings
try:
    from osgeo import ogr

    ogr_installed = True
except ImportError:
    ogr_installed = False

try:
    from itertools import izip as zip
except ImportError:
    pass  # python3

import pygeogrids.nearest_neighbor as NN
from pygeogrids.geodetic_datum import GeodeticDatum
from pygeogrids.subset import SubsetCollection, Subset
from netCDF4 import Dataset
from pygeogrids.netcdf import load_grid_definition, filled_no_mask, save_lonlat
import warnings

class MetaGrid:
    """
    MetaGrid is a version of a Basic or CellGrid that contains a subset collection
    to quickly create, activate, combine and store multiple subsets.
    """

    # todo: shape is not intuitive should be (lat,lon(, but is (lon,lat)... this is a BasicGrid Problme
    #

    def __init__(self, lon, lat, cells=None, gpis=None, geodatum='WGS84',
                 setup_kdTree=True, shape=None, subsets=None):
        """

        Parameters
        ----------
        lon : numpy.ndarray
            Longitudes of the points in the grid.
        lat : numpy.ndarray
            Latitudes of the points in the grid.
        cells : numpy.ndarray, optional (default: None)
            Of same shape as lon and lat, containing the cell number of each gpi.
            If None is given, a 5x5 deg cell sampling is chosen.
        gpis : numpy.array, optional
            if the gpi numbers are in a different order than the
            lon and lat arrays an array containing the gpi numbers
            can be given
            if no array is given here the lon lat arrays are given
            gpi numbers starting at 0
        geodatum : basestring
            Name of the geodatic datum associated with the grid
        setup_kdTree : boolean, optional
            if set (default) then the kdTree for nearest neighbour
            search will be built on initialization
        shape : tuple, optional
            The shape of the grid array in 2-d space.
            e.g. for a 1x1 degree global regular grid the shape would be (180,360).
            if given the grid can be reshaped into the given shape
            this indicates that it is a regular grid and fills the
            attributes self.lon2d and self.lat2d which
            define the grid only be the meridian coordinates(self.lon2d) and
            the coordinates of the circles of latitude(self.lat2d).
            The shape has to be given as (lat2d, lon2d) # todo: this is wrong?
            It it is not given the shape is set to the length of the input
            lon and lat arrays.
            # todo: shape is not intuitive....

        shape : tuple, optional (default: None)
            Number of elements in the grid in a 2d array. Order: (lon, lat)
        subsets : list, optional (default: None)
            A list of pygeogrids.subset.Subsets that are assigned to the grid
            upon initialisation or a pygeogrids.subset.SubsetCollection.
        """

        if cells is None:
            self.base = BasicGrid(lon=lon, lat=lat, gpis=gpis,
                                  geodatum=geodatum, setup_kdTree=setup_kdTree,
                                  subset=None, shape=shape)
        else:
            self.base = CellGrid(lon=lon, lat=lat, gpis=gpis, cells=cells,
                                 geodatum=geodatum, setup_kdTree=setup_kdTree,
                                 subset=None, shape=shape)

        self.active_subset = None  # active_subset subset, set by activate()

        if isinstance(subsets, SubsetCollection):
            self.subsets = subsets
        else:
            self.subsets = SubsetCollection(subsets=subsets)

        # fill value has to match with the value from save_lonlat(), i.e. 0!
        # Therefore this can't be changed for now.
        self.subsets_fill_value = 0

    def __eq__(self, other):
        """ Compare grids and subset collections """
        basicsame = self.base == other
        subsetsame = self.subsets == other.subset_coll
        return all([basicsame, subsetsame])

    @property
    def subset_names(self):
        return self.subsets.names

    @classmethod
    def load_grid(cls, filename, location_var_name='gpi', subsets='all'):
        """
        Load meta grid with the selected subsets from file.

        Parameters
        ----------
        filename : str
            Path to the grid nc file.
        location_var_name : str, optional (default: 'gpi')
            Name of the index variable
        subsets : dict or list, optional (default: 'all')
            as dict: {name1: [values1], ...}
            as list: [name1, name2,...]
            Subset names or subset names and a list of values to consider.
            If 'all' is passed, all variables (except the reserved_names) are
            interpreted as subsets.

        Returns
        -------
        grid : MetaGrid
            A MetaGrid with a subset collection loaded from file
        """

        # Variables and variable values that are always ignored
        reserved_names = ['lon', 'lat', location_var_name, 'crs', 'cells']
        fill_value = 0

        def subset_defs(filter_subsets=()) -> dict:
            definitions = {}
            with Dataset(filename, 'r') as nc_data:
                for var in nc_data.variables:
                    if var in reserved_names: continue
                    if var in filter_subsets: continue
                    subset = filled_no_mask(np.unique(nc_data.variables[var][:]))
                    definitions[var] = np.delete(subset, fill_value)
            return definitions

        if subsets is None:
            definitions = None
        elif subsets.lower() == 'all':
            definitions = subset_defs()
        else:
            filter_subsets = subsets
            definitions = subset_defs(filter_subsets=filter_subsets)

        lons, lats, gpis, arrcell, subsets_kwargs, geodatumName, shape = \
            load_grid_definition(filename, location_var_name, subsets=definitions)

        subsets = []
        for name, kwargs in subsets_kwargs.items():
            subsets.append(Subset(name, **kwargs))

        return cls(lons,
                   lats,
                   gpis=gpis,
                   cells=arrcell,
                   geodatum=geodatumName,
                   setup_kdTree=True,
                   shape=shape,
                   subsets=subsets)

    @classmethod
    def from_grid(cls, grid, input_subset_name='input_subset', subsets=None):
        """
        Create a MetaGrid object from a passed BasicGrid or CellGrid

        Parameters
        ----------
        grid : BasicGrid or CellGrid
            The grid to use as the basis for coords and gpis in the MetaGrid.
        input_subset_name : str, optional (default: 'input_subset')
            If there is already a subset active in the passed grid, then the
            subset will have this name in the MetaGrid SubetCollection. If there
            is no subset, this is ignored.
        subsets : dict or list, optional (default: 'all')
            as dict: {name1: [values1], ...}
            as list: [name1, name2,...]
            Subset names or subset names and a list of values to consider.
            If 'all' is passed, all variables (except the reserved_names) are
            interpreted as subsets.

        Returns
        -------
        grid : MetaGrid
            A MetaGrid with a subset collection loaded from file
        """

        lons = grid.arrlon
        lats = grid.arrlat
        gpis = grid.gpis

        try:
            cells = grid.arrcell
        except AttributeError:
            cells = None

        if not grid.allpoints:
            meaning = 'Subset from grid used in creation of Metagrid'
            oss = Subset(name=input_subset_name, gpis=grid.gpis, meaning=meaning)
        else:
            oss = None

        if subsets is None:
            subsets = oss
        elif isinstance(subsets, SubsetCollection):
            if oss is not None: subsets.add(oss)
        else:
            subsets = subsets + oss if oss is not None else subsets

        subsets = None if len(subsets) == 0 else subsets

        return cls(lons,
                   lats,
                   gpis=gpis,
                   cells=cells,
                   geodatum=grid.geodatum.name,
                   setup_kdTree=True,
                   shape=grid.shape,
                   subsets=subsets)

    def subsets_as_dicts(self, format='all'):
        """
        Return subset points as a dictionary.

        Parameters
        ----------
        format : str
            See the description of Subset.to_dict()
            one of: all, save_lonlat, gpis

        Returns
        -------
        subset_dict : dict
            Dict of subset points in the selected format.
        """

        subset_dicts = {}
        for subset in self.subsets:
            subset_dicts.update(subset.as_dict(format))

        return subset_dicts

    def save_grid(self, filename, global_attrs=None):
        """
        Save MetaGrid and all subsets to netcdf file.

        Parameters
        ----------
        filename : str
            Path where the .nc file is created.
        global_attrs : dict, optional (default: None)
            Additional global attributes that are passed when writing the nc
            file.
        """

        try:
            arrcell = self.base.arrcell
        except AttributeError:
            arrcell = None

        gpis = self.base.gpis

        if self.base.shape is not None:
            if global_attrs is None:
                global_attrs = {}
            global_attrs['shape'] = self.base.shape

        global_attrs['grid_type'] = self.__class__.__name__  # MetaGrid

        subset_dicts = None
        if not self.subsets.empty:
            subset_dicts = self.subsets_as_dicts(format='save_lonlat')

        var_attrs = {subset.name: subset.attrs for subset in self.subsets}

        save_lonlat(filename, self.base.arrlon, self.base.arrlat, self.base.geodatum,
                    arrcell=arrcell, gpis=gpis, subsets=subset_dicts, zlib=True,
                    global_attrs=global_attrs, var_attrs=var_attrs)

    def add_subset(self, subset: {Subset, dict}):
        """
        Add a new subset to the subset collection either from a Subset object
        or from a dict with name and gpis as key and value.

        Parameters
        ----------
        subset : Subset or dict
            If a Subset is passed directy it is simply added. If a dict of the
            for {name : gpis} is passed, a new basic subset is created.
        """

        if isinstance(subset, Subset):
            pass
        elif isinstance(subset, dict):
            for name, gpis in subset.items():
                subset = Subset(name, gpis)
        else:
            raise ValueError("Either pass a Subset or a dict like {name: gpis}")

        self.subsets.add(subset)

    def subset_from_bbox(self, latmin=-90, latmax=90, lonmin=-180, lonmax=180,
                         name=None, **subset_kwargs):
        """
        Create a new subset from a bounding box and add it to the collection.
        This applies to the currently active subset.

        Parameters
        ----------
        latmin : float
            Lat of the lower left corner of the bbox
        latmax : float
            Lat of the upper right corner of the bbox
        lonmin : float
            Lon of the lower left corner of the bbox
        lonmax : float
            Lon of the upper right corner of the bbox
        name : str
            Name of the subset, if None is passed a name is generated from the
            bbox
        subset_kwargs :
            Additional keywords are passed to the subset generation
        """
        # if self.active_subset is None:
        #    raise ValueError("No subset is currently active")

        gpis = self.base.get_bbox_grid_points(latmin, latmax, lonmin, lonmax)

        if name is None:
            bbox_str = '_'.join([str(f) for f in [latmin, latmax, lonmin, lonmax]])
            name = f"bbox_{bbox_str}"

        self.add_subset(Subset(name, gpis, **subset_kwargs))

    def filter_active_subset(self, vals: {int: list}, **subset_kwargs):
        """
        Create a new subset from the currently active one by filtering with
        the passed values.
        """
        # todo: rename to filter active
        # todo create a similar fct subset_from_values(name, vals, new_name)
        # todo: add name to select a ss instead of using the current one
        if self.active_subset is None:
            raise ValueError('No subset active to be filtered. '
                             'Activate one with activate_subset(<name>)')
        else:
            subset = self.active_subset

        self.add_subset(subset.select_by_val(vals, **subset_kwargs))

    def deactivate_subset(self):
        """
        Deactivate the current subset. I.e. go back to the initialisation state.
        Also revert splitting if any splitting was performed.
        """
        self.base._empty_subset()
        self.base.unite()

    def activate_subset(self, name, vals=None):
        """
        Activate a subset from the collection. Only one subset can be active_subset at
        a time.

        Parameters
        ----------
        name : str
            Name of the subset to activate, must be in the collection.
        vals : {int,float,list}
            Subset values are filtered for these values directly. without creating
            a new subset
        """

        if self.active_subset is not None:
            self.deactivate_subset()

        subset = self.subsets[name]
        if vals is not None:
            subset = subset.select_by_val(vals)

        self.active_subset = subset

        subset_gpis = self.active_subset.gpis

        self.base.activearrlon = self.base.arrlon[subset_gpis]
        self.base.activearrlat = self.base.arrlat[subset_gpis]
        self.base.activegpis = self.base.gpis[subset_gpis]
        self.base.allpoints = False

        self.subset = subset_gpis

    def combine_subsets(self, names, new_name, method='intersect', **subset_kwargs):
        """
        Combine two or more subsets and create a new one which is added to the
        current subset collction.

        Parameters
        ----------
        names : Iterable
            List of names of subsets to combine
        new_name : str
            Name of the subset that is created
        method : str, optional (default: 'intersect')
            Name of a method to use to combine the subsets.
        kwargs:
        Additional kwargs are used when creating the new subset.
        """

        self.subsets.combine(subset_names=names,
                             new_name=new_name,
                             method=method, **subset_kwargs)

    def merge_subsets(self, names: list, new_name, layer_vals=None, keep_merged=True):
        """
        Merge multiple subsets into a single, new one. Merge down layers in
        the given order. Optionally set a new value for each subset.
        Points that are present in multiple merged subsets, will have
        the value from the last merged subset.

        Parameters
        ----------
        names : list
            Names of subsets to merge. If a GPI is in multiple subsets,
            the value of the later subset will be used.
        new_name : str
            Name of the new subset that is created. Must be different from
            subsets that are already in the collection.
        keep_merged : bool, optional (default: True)
            Keep the original input subsets as well as the newly created one.
        """

        self.subsets.merge(subset_names=names,
                           new_name=new_name,
                           new_vals=layer_vals,
                           keep=keep_merged)

    def plot(self, only_subset=False, visualise_vals=False, ax=None, **kwargs):
        """ Draw a basic map of grid points and current active subset """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            warnings.warn('Plotting needs matplotlib installed, which is not found')
            return
        from pygeogrids.plotting import points_on_map
        imax = ax

        if not only_subset:
            not_ss_kwargs = {k: v for k, v in kwargs.items() if k not in ['cmap', 'color']}
            imax = points_on_map(self.base.arrlon, self.base.arrlat,
                                 c=None, color='grey', imax=imax, **not_ss_kwargs)

        if visualise_vals:
            c = self.active_subset.values
            if 'cmap' not in kwargs:
                kwargs['cmap'] = plt.get_cmap('jet')
        else:
            c = None
            if 'color' not in kwargs:
                kwargs['color'] = 'green'

        if 'set_auto_extent' not in kwargs:
            set_auto_extent = True if only_subset else False
        else:
            set_auto_extent = kwargs.pop('set_auto_extent')

        imax = points_on_map(self.base.activearrlon, self.base.activearrlat,
                             c=c, imax=imax,
                             set_auto_extent=set_auto_extent,
                             **kwargs)

        return imax
