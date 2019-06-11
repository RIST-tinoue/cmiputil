#!/usr/bin/env python3
"""
Search by ESGF RESTful API, get and open multiple datafiles,
create meta info.

See https://earthsystemcog.org/projects/cog/esgf_search_restful_api
for the detail ESGF RESTful API.

This version uses
`siphon <https://www.unidata.ucar.edu/software/siphon/>`_ and
`xarray <http://xarray.pydata.org/>`_.

Basic Usage
-----------

Typical flow of searching and downloading CMIP6 data from ESGF is as
follows;

1. instantiate :class:`esgfsearch.ESGFSearch` instance,
2. get catalog URLs via :meth:`ESGFSearch.getCatURLs` method,
3. get dataset URLs via :meth:`ESGFSearch.getDataURLs` method,
4. get dataset via :meth:`ESGFSearch.getDatasets` method,

Catalog URLs, dataset URLs, and dataset objects are all stored as
instance attributes.


Config File
-----------

This module read in conf file, sections below;

- [ESGFSearch]
    - `search_service`: the base URL of the search service at a ESGF Index Node
    - `service_type`: ``search`` or ``wget``
    - `aggregate` : :meth:`getDatasets` returns aggregated datasets or not
    - `datatype_xarray` : :meth:`getDatasets` returns xarray or netCDF4
- [ESGFSearch.keywords] : keyword parameters of RESTful API
- [ESGFSearch.facets] : facet parameters of RESTful API
"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190602'
__date__ = '2019/06/02'

from cmiputil import drs, config
import urllib3
import json
import xarray as xr
import netCDF4 as nc
from siphon.catalog import TDSCatalog
from pprint import pprint
from os.path import basename


class NotFoundError(Exception):
    pass


class ESGFSearch():
    """
    Search by ESGF RESTful API, get to the datafile via OPenDAP.

    If `conffile` is ``None``, no conf file is read and *blank* instance
    is created.  If you want only default conf files, set ``conffile=""``.
    See :mod:`config` module for details.

    Args:
        conffile (path-like): configure file

    Attributes:
        conf: :class:`config.Conf` instance
        search_service: search service for RESTful API, eg.,
                        ``http://esgf-node.llnl.gov/esg-search/``
        service_type: service type for RESTful API.
                      currently ``search`` only allowed.
        aggregate: access aggregated via OPeNDAP.
        datatype_xarray: open dataset as xarray or netCDF4
        params: keyword parameters and facet parameters for RESTful API
        cat_urls (list(str)): obtained catalog URLs
        data_urls (list(str) or list of list(str)): obtained dataset URLs
        datasets: list of obtained datasets
    """
    _debug = False

    @classmethod
    def _enable_debug(cls):
        cls._debug = True

    @classmethod
    def _disable_debug(cls):
        cls._debug = True

    # @property
    # def debug(cls):
    #     return cls._debug

    def __init__(self, conffile=""):
        self.conf = config.Conf(conffile)
        try:
            self.search_service = self.conf['ESGFSearch']['search_service']
            self.service_type = self.conf['ESGFSearch']['service_type']
        except KeyError:
            self.search_service = search_service_default
            self.service_type = service_type_default

        try:
            self.aggregate = self.conf['ESGFSearch']['aggregate']
        except KeyError:
            self.aggregate = aggregate_default

        try:
            self.datatype_xarray = self.conf['ESGFSearch']['datatype_xarray']
        except KeyError:
            self.datatype_xarray = datatype_xarray_default

        try:
            self.params = dict(self.conf['ESGFSearch.keywords'].items())
        except KeyError:
            self.params = {}

        try:
            self.params.update(dict(self.conf['ESGFSearch.facets'].items()))
        except KeyError:
            pass

    def getCatURLs(self, params=None, base_url=None):
        """
        Using ESGF RESTful API, get URLs for OPeNDAP TDS catalog.

        Obtained catalog URLs are set as :attr:`cat_urls` attribute of
        `self`.

        Args:
            params (dict): keyword parameters and facet parameters.
            base_url : base URL of the ESGF search service.

        Raises:
            NotFoundError: raised if no catalog found.

        Return:
            None

        If `base_url` is not ``None``, override :attr:`search_service` +
        :attr:`service_type` of `self`.

        `params` is to *update* (use `update()` method of python dict)
        to :attr:`params` of `self`.

        TODO:
            - How to enable *a negative facet* of RESTful API ?
        """
        if params:
            self.params.update(params)
        if not base_url:
            base_url = self.search_service + self.service_type

        if (self._debug):
            print(f'dbg:ESGFSearch.getCatURLs:base_url:{base_url}')
            print('dbg:ESGFSeaerch.getCatURLs:params:')
            pprint(self.params)

        http = urllib3.PoolManager()
        try:
            r = http.request('GET', base_url, fields=self.params)
        except Exception as e:
            print('Error in http.request():')
            print(e.args)
            raise
            return []
        if (r.status != 200):
            print('Bad Status:', r.status)
            print(r.data.decode())
            return []
        # don't know why but returned are bytes, not str.
        result = json.loads(r.data.decode())

        if (result['response']['numFound'] == 0):
            raise NotFoundError('No catalog found.')

        self.cat_urls = []
        for r in result['response']['docs']:
            for l in r['url']:
                (url, mime, service) = l.split('|')
                # select TDS catalog
                if (service == 'THREDDS'):
                    self.cat_urls.append(url)

    def getDataURLs(self):
        """
        From URLs of TDS catalog, obtain URLs of dataset.

        Catalog URLs are set as :attr:`cat_urls` attribute of `self`,
        that is obtained by, for example, :meth:`getCatURLs()`.

        If :attr:`aggregate` of `self` is ``True``, obtain URLs of
        aggregated dataset, else URLs of all of files listed in the
        catalog.

        Obtained dataset URLs are set as :attr:`.data_urls` of `self`.

        """
        self.data_urls = [self._getDataURL(u) for u in self.cat_urls]

    def _getDataURL(self, url):

        try:
            cat = TDSCatalog(url)
        except Exception as e:
            print('Error in siphon.TDSCatalog():', e.args)
            raise

        if self._debug:
            print('dbg:ESGFSearch.aggregate:', self.aggregate)

        if self.aggregate:
            # construct base url
            data_url = cat.base_tds_url
            service_base = _getServiceBase(cat.services)
            data_url += service_base

            # url of Aggregated dataset
            ds = cat.datasets[-1]   # Is this universal ?

            data_url += ds.url_path
        else:
            data_url = [x.access_urls['OpenDAPServer']
                        for x in cat.datasets.values()
                        if 'OpenDAPServer' in x.access_urls]
            data_url.sort()

        return data_url

    def openDatasets(self):
        """
        Open and return dataset object from dataset URLs.

        Dataset URLs are set as :attr:`data_urls` attribute of `self`,
        obtained by, for example, :meth:`getDataURLs`.

        If :attr:`datatype_xarray` of `self` is ``True``,
        open by ``xarray.open_dataset()``, else open by
        ``netCDF4.Dataset()``.

        If `url` is a list, they are opened as a multi-file dataset,
        via `xarray.open_mfdataset()` or `netCDF4.MFDataset()`.

        Opened datasets are stored as :attr:`dataset` of `self`.
        """
        res = [self._openDataset(url) for url in self.data_urls]
        self.datasets = [d for d in res if d]

    def _openDataset(self, url):
        if self.datatype_xarray:
            try:
                if type(url) is list:
                    ds = xr.open_mfdataset(url, decode_cf=False)
                else:
                    # ds = xr.open_dataset(url,
                    #                      decode_times=False, decode_cf=False)
                    ds = xr.open_dataset(url, decode_cf=False)
            except (KeyError, OSError) as e:
                print(f"Error in opening xarray dataset:"
                      f"{basename(url)}:{e.args}\n Skip.")
            else:
                return ds
        else:
            try:
                if type(url) is list:
                    ds = nc.MFDataset(url)
                else:
                    ds = nc.Dataset(url, 'r')
            except (KeyError, OSError) as e:
                print(f"Error in opening netCDF dataset:"
                      f"{basename(url)}:{e.args}\n Skip.")
            else:
                return ds

    def getDatasets(self):
        """
        From URLs of TDS catalog, open xarray or netCDF4 dataset.

        Catalog URLs are set as :attr:`cat_urls` attribute of `self`,
        that is obtained by, for example, :meth:`getCatURLs()`.

        If :attr:`aggregate` of `self` is ``True``, obtain URLs of
        aggregated dataset, else URLs of all of files listed in the
        catalog.

        Obtained datasets are set as :attr:`.dataset` of `self`.

        """
        self.getDataURLs()
        self.openDatasets()

    def getLocalPath(self, params, base_dir=None):
        """
        Search local data directory for CMIP6 data.

        Using same interface with getCatURLs()

        Args:
            params(dict): keyword parameters and facet parameters.
            base_url : base path for local data directory.
        Raises:
            NotFoundError: raised if no paths found.
        Return:
            list of path-like:  paths found to match given facets.

        `field` is initialized by :data:`.keyword_defautls` and
        :data:`.facet_defaults`.

        Example:
            >>> params = {'source_id': 'MIROC6', 'experiment_id': 'historical',
            ...    'variant_label': 'r1i1p1f1', 'variable': 'tas', }
            >>> str(getLocalPath(params, base_dir='/data/'))
            '/data/CMIP6/*/*/MIROC6/historical/r1i1p1f1/Amon/*/*/*/*_Amon_MIROC6_historical_r1i1p1f1_*_*.nc'
        """
        d = drs.DRS(**params)
        p = d.dirName(prefix=base_dir)
        f = d.fileName()
        return p / f


def _getServiceBase(services):
    # `services` must be a list of SimpleService or CompoundService
    # class, attribute of TDSCatalog instance.

    for s in services:
        # search 'OpenDAP' service.
        if (s.service_type.lower() == 'opendap'):
            return s.base
        # if service_type is compound, do recursive call.
        elif (s.service_type.lower() == 'compound'):
            return _getServiceBase(s.services)

########################################################################
# defaults


#: Default search service URL
search_service_default = 'http://esgf-node.llnl.gov/esg-search/'
# search_service_default = 'http://esgf-data.dkrz.de/esg-search/'

#: Default service type
service_type_default = 'search'

aggregate_default = True
datatype_xarray_default = True

#: Default keywords for RESTful API.
keywords_default = {
    'format': r'application/solr+json',
    'replica': 'false',
    'latest': 'true',
    'limit': 10000,
    'type': 'Dataset',  # must be to get catalog
    'fields': 'url',
    }

#: Default fasets for RESTful API.
facets_default = {
    'table_id': 'Amon',
    }

# params_default = dict(keywords_default)
# params_default.update(facets_default)


def getDefaultConf():
    """
    Return default values for config file.

    Intended to be called before :meth:`config.writeConf`

    Example:
        >>> from cmiputil import esgfsearch, config
        >>> conf = Conf('')
        >>> conf.setDefaultSection()
        >>> d = esgfsearch.getDefaultConf()
        >>> conf.read_dict(d)
        >>> conf.writeConf('/tmp/cmiputil.conf', overwrite=True)

    """
    res = {}
    res['ESGFSearch'] = {'search_service': search_service_default,
                         'service_type': service_type_default,
                         'aggregate': aggregate_default,
                         'datatype_xarray': datatype_xarray_default}
    res['ESGFSearch.keywords'] = keywords_default
    res['ESGFSearch.facets'] = facets_default
    return res


if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
