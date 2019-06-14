#!/usr/bin/env python3
"""
Search by `ESGF RESTful API`_, get via `OPeNDAP`_.

This version uses
`siphon <https://www.unidata.ucar.edu/software/siphon/>`_ and
`xarray <http://xarray.pydata.org/>`_.

Basic Usage
===========

Note:
    From ver.0.8, opening dataset, such as xarray or netCDF4, is dropped.
    You have to open them by yourself with your favorit datatype. 



Typical flow of searching and downloading CMIP6 data from ESGF is as
follows;

1. instantiate :class:`esgfsearch.ESGFSearch` instance,
2. get catalog URLs via :meth:`.getCatURLs` method,
3. get dataset URLs via :meth:`.getDataURLs` method,
4. get and open dataset URLs via your favorit datatype, such as xarray
   or netCDF4.

Catalog URLs and dataset URLs are stored as instance attributes.

Example:

    >>> from cmiputil import esgfsearch
    >>> import xarray as xr
    >>> params = {'source_id': 'MIROC6',
    ...           'experiment_id': 'historical',
    ...           'variable_id': 'tas',
    ...           'variant_label': 'r1i1p1f1'}
    >>> es = esgfsearch.ESGFSearch()
    >>> es.getCatURLs(params)
    >>> es.getDataURLs()
    >>> ds = []
    >>> for url in es.data_urls:
    ...     if type(url) is list:
    ...         ds.append(xr.open_mfdataset(url, decode_times=False))
    ...     else:
    ...         ds.append(xr.open_dataset(url, decode_times=False))

    In above, `es.cat_urls` and `es.data_urls` are set as below::

         'cat_urls': ['http://esgf-data2.diasjp.net/thredds/catalog/esgcet/1/CMIP6.CMIP.MIROC.MIROC6.historical.r1i1p1f1.Amon.tas.gn.v20181212.xml#CMIP6.CMIP.MIROC.MIROC6.historical.r1i1p1f1.Amon.tas.gn.v20181212'],
         'data_urls': ['http://esgf-data2.diasjp.net/thredds/dodsC/CMIP6.CMIP.MIROC.MIROC6.historical.r1i1p1f1.Amon.tas.gn.tas.20181212.aggregation.1']}

Config File
===========

This module read in config file, sections below;

- [cmiputil]
    - `cmip6_data_dir`: the root of local data store (described below).
- [ESGFSearch]
    - `search_service`: the base URL of the search service at a ESGF Index Node
    - `service_type`: ``search`` or ``wget``
    - `aggregate` : :meth:`getDataURLs` returns aggregated datasets or not
- [ESGFSearch.keywords] : keyword parameters of RESTful API
- [ESGFSearch.facets] : facet parameters of RESTful API

Local data store
================

This module assumes that local data files are stored in the DRS
complient directory structure. See :mod:`drs` module for the details
of DRS.  If you use `synda install` for download and replication of
CMIP6 data files from ESGF, files are stored in such way.  So you can
use :meth:`.getLocalDirs()` and :meth:`.getDataFiles()` with the same
interface with :meth:`.getCatURLs` and :meth:`.getDataURLs()`.

Do not forget to set :attr:`.base_dir` attribute or `cmip6_data_dir`
in config file as the root of this directory structure.

Example:
    >>> import xarray as xr
    >>> params = {'source_id': 'MIROC6',
    ...           'experiment_id': 'historical',
    ...           'variable_id': 'tas',
    ...           'variant_label': 'r1i1p1f1'}
    >>> es = ESGFSearch()
    >>> es.getLocalDirs(params, base_dir='/data')
    >>> es.getDataFiles()
    >>> ds = []
    >>> for files in es.data_files:
    ...     ds.append(xr.open_mfdataset(files, decode_cf=False))


    In above, ``es.local_dirs`` is set as below if they are exists::

        ['/data/CMIP6/CMIP/MIROC/MIROC6/historical/r1i1p1f1/Amon/tas/gn/v20181212',
         '/data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212']


.. _ESGF RESTful API: 
   https://earthsystemcog.org/projects/cog/esgf_search_restful_api

.. _OPeNDAP:
   https://www.earthsystemcog.org/projects/cog/doc/opendap
"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190612'
__date__ = '2019/06/12'

from cmiputil import drs, config
import urllib3
import json
from siphon.catalog import TDSCatalog
from pprint import pprint
from pathlib import Path


#: OPeNDAP Catalog URL not found
class NotFoundError(Exception):
    pass


class ESGFSearch():
    """
    Search by ESGF RESTful API, get via OPeNDAP.

    If `conffile` is ``None``, no config file is read and *blank* instance
    is created.  If you want only default config files, set ``conffile=""``.
    See :mod:`config` module for details.

    Args:
        conffile (path-like): configure file

    Attributes:
        conf: :class:`config.Conf` instance
        search_service: search service for RESTful API, eg.,
                        ``http://esgf-node.llnl.gov/esg-search/``
        service_type: service type for RESTful API.
                      currently ``search`` only allowed.
        aggregate (bool): access aggregated via OPeNDAP.
        params: keyword parameters and facet parameters for RESTful API
        cat_urls (list(str)): obtained catalog URLs
        data_urls (list(str) or list of list(str)): obtained dataset URLs
        base_dir: base(root) path for local data directory structure
        local_dirs: obtained local directories for local dataset files.
        data_files: obtained local dataset files
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

        if self._debug:
            config.Conf._enable_debug()
            drs.DRS._enable_debug()
            
        self.conf = config.Conf(conffile)

        sec = self.conf['ESGFSearch']
        try:
            self.search_service = sec['search_service']
            self.service_type = sec['service_type']
        except KeyError:
            self.search_service = search_service_default
            self.service_type = service_type_default

        try:
            self.aggregate = sec.getboolean('aggregate')
        except KeyError:
            self.aggregate = aggregate_default

        sec = self.conf['ESGFSearch.keywords']
        try:
            self.params = dict(sec.items())
        except KeyError:
            self.params = {}

        sec = self.conf['ESGFSearch.facets']
        try:
            self.params.update(dict(sec.items()))
        except KeyError:
            pass

        try:
            self.base_dir = self.conf.commonSection['cmip6_data_dir']
        except KeyError:
            self.base_dir = None

    def getCatURLs(self, params=None, base_url=None):
        """
        Using ESGF RESTful API, get URLs for OPeNDAP TDS catalog.

        Obtained catalog URLs are set as :attr:`cat_urls` attribute.

        Args:
            params (dict): keyword parameters and facet parameters.
            base_url : base URL of the ESGF search service.

        Raises:
            NotFoundError: raised if no catalog found.

        Return:
            None

        If `base_url` is not ``None``, overrides :attr:`search_service` +
        :attr:`service_type` attributes.

        `params` is to *update* (use `update()` method of python dict)
        to :attr:`params` attribute.

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

        Catalog URLs are set as :attr:`cat_urls` attribute,
        that is obtained by, for example, :meth:`getCatURLs()`.

        If :attr:`aggregate` attribute is ``True``, obtain URLs of
        aggregated dataset, else URLs of all of files listed in the
        catalog.

        Obtained dataset URLs are set as :attr:`.data_urls` attribute.

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

    def getLocalDirs(self, params=None, base_dir=None):
        """
        Get local path(s) to match given search condition.

        Using same interface with :meth:`getCatURLs()`, obtained path
        are set as :attr:`local_dirs` attribute.

        Resulting paths (set as :attr:`localpath`) are DRS compliant
        (see `Local data store`_) **real existing** ones, braces are
        expanded and asterisk are globed.

        Args:
            params (dict): keyword parameters and facet parameters.
            base_dir (str or path-like): base path for local data directory.
        Raises:
            NotFoundError: raised if no paths found.


        If `base_dir` is not ``None``, overrides :attr:`base_dir`.

        `params` is to *update* (use `update()` method of python dict)
        to :attr:`params` attribute.
        """
        if params:
            self.params.update(params)

        if base_dir is not None:
            self.base_dir = base_dir

        if (self._debug):
            print(f'dbg:ESGFSearch.getLocalDirs:base_dir:{self.base_dir}')
            print('dbg:ESGFSeaerch.getLocalDirs:params:')
            pprint(self.params)

        d = drs.DRS(**self.params)
        self.local_dirs = d.dirNameList(prefix=self.base_dir)

    def getDataFiles(self):
        """
        From directories of local data store, obtain dataset files.

        Directories are set as :attr:`local_dirs` attribute,
        that is obtained by, for example, :meth:`getLocalDirs()`.

        Obtained dataset files are set as :attr:`.data_files` attribute.

        """
        self.data_files = [self._getDataFiles(d) for d in self.local_dirs]

    def _getDataFiles(self, directory):
        return list(directory.iterdir())


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

    Intended to be called before :meth:`.writeConf()` in
    :mod:`config`.

    Example:
        >>> from cmiputil import esgfsearch, config
        >>> conf = config.Conf(None)   #  to create brank config
        >>> conf.setCommonSection()
        >>> d = esgfsearch.getDefaultConf()
        >>> conf.read_dict(d)
        >>> conf.writeConf('/tmp/cmiputil.conf', overwrite=True)

    """
    res = {}
    res['ESGFSearch'] = {'search_service': search_service_default,
                         'service_type': service_type_default,
                         'aggregate': aggregate_default,
    }
    res['ESGFSearch.keywords'] = keywords_default
    res['ESGFSearch.facets'] = facets_default
    return res


if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
