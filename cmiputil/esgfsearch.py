#!/usr/bin/env python3
"""
Search CMIP6 datasets via `ESGF RESTful API`_, get `OPeNDAP`_ URLs and
other information of found dataset.

Basic Usage
===========
Typical flow of searching and downloading CMIP6 dataset from ESGF is as
follows;

1. create a :class:`esgfsearch.ESGFSearch` instance,
2. do search via the :meth:`.doSearch` method,
3. seach results are set as a :attr:`.datainfo` attribute, which is a
   list of :class:`esgfdatainfo.DataInfo` instances. 
   One element corresponds to the one search result.
4. open dataset URLs as your favorit datatype, such as `xarray`_, `siphon`_ 
   or `netCDF4`_, etc.

All dataset URLs found are stored as the :attr:`.data_urls` attribute.


.. _ESGF RESTful API:
   https://earthsystemcog.org/projects/cog/esgf_search_restful_api
.. _OPeNDAP:
   https://www.earthsystemcog.org/projects/cog/doc/opendap
.. _xarray: http://xarray.pydata.org/
.. _siphon: https://www.unidata.ucar.edu/software/siphon/
.. _netCDF4: https:hogehoge


Example:

    >>> from cmiputil import esgfsearch
    >>> import xarray as xr
    >>> params = {'source_id': 'MIROC6',
    ...           'experiment_id': 'historical',
    ...           'variable_id': 'tas',
    ...           'variant_label': 'r1i1p1f1'}
    >>> es = esgfsearch.ESGFSearch()
    >>> es.doSearch(params)

    In above after :meth:`.doSearch()`, `es.data_urls` is set as below::

         'data_urls': ['http://esgf-data2.diasjp.net/thredds/dodsC/CMIP6.CMIP.MIROC.MIROC6.historical.r1i1p1f1.Amon.tas.gn.tas.20181212.aggregation.1']}

    You can open in any kind of datasets from this URLs, for example::

        ds = []
        for url in es.data_urls:
           if type(url) is list:
               ds.append(xr.open_mfdataset(url, decode_times=False, combine='by_coords'))
           else:
               ds.append(xr.open_dataset(url, decode_times=False))


"Aggregated"
--------------

One feature of OPenDAP is that a multi-files dataset can be accessed
as an *aggregated* single file.  If you prefer to get aggregated
dataset, set ``aggregate`` as ``True`` in config file (see below), or
vice varsa.

In case you choose not to use aggregation, netCDF4 (and the datatype
that use it as a backend) can open multifile as a single dataset, as
shown in above example.

Config File
===========

This module reads in config file, sections below;

- [cmiputil]

    ``cmip6_data_dir`` (str):
        the root of local data store (described below).

- [ESGFSearch]

    ``search_service`` (str):
        the base URL of the search service at a ESGF Index Node

    ``service_type`` (str):
        ``search`` or ``wget``

    ``aggregate`` (bool):
         retrieve OPeNDAP aggregated datasets or not

- [ESGFSearch.keywords] : keyword parameters of RESTful API

- [ESGFSearch.facets] : facet parameters of RESTful API


Warning:
  ``service_type='wget'`` case is not implemented yet.

Local files
===========

This module assumes that local data files are stored in the DRS
complient directory structure. See :mod:`drs` module for the details
of DRS.  If you use `synda install` for download and replication of
CMIP6 data files from ESGF, files are stored in such way. 

:meth:`.doSearch()` also searchs local files corresponding to the
search result and set :meth:`.local_files` property so that you can
use local files instead of downloading them.

Do not forget to set :attr:`.base_dir` attribute or `cmip6_data_dir`
in config file as the root of this directory structure.


After :meth:`.doSearch()` in above example, ``es.local_files`` is set as below if they are exists::

    [[PosixPath('/data/CMIP6/CMIP/MIROC/MIROC6/historical/r1i1p1f1/Amon/tas/gn/v20181212/tas_Amon_MIROC6_historical_r1i1p1f1_gn_185001-194912.nc'), 
      PosixPath('/data/CMIP6/CMIP/MIROC/MIROC6/historical/r1i1p1f1/Amon/tas/gn/v20181212/tas_Amon_MIROC6_historical_r1i1p1f1_gn_195001-201412.nc')]]


"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190714'
__date__ = '2019/07/14'

import json
from pprint import pprint

import urllib3

from cmiputil import config, drs, esgfdatainfo


#: OPeNDAP Catalog URL not found
class NotFoundError(Exception):
    pass


class ESGFSearch():
    """
    Search CMIP6 datasets via `ESGF RESTful API`_, get `OPeNDAP`_ URLs and 
    other information of found datasets

    If `conffile` is ``None``, no config file is read and the *blank* instance
    is created.  If you want only default config files, set ``conffile=""``.
    See :mod:`config` module for details.

    Args:
        conffile (path-like): configure file

    Attributes:
        conf: :class:`config.Conf` instance
        datainfo: list of :class:`esgfdatainfo.ESGFDataInfo` instances
        search_service: search service for RESTful API, eg.,
                        ``http://esgf-node.llnl.gov/esg-search/``
        service_type: service type for RESTful API.
                      currently only ``search`` is allowed.
        aggregate (bool): get aggregated URL if ``TRUE``
        params: dict for keyword parameters and facet parameters for RESTful API
        base_dir (str): base(root) path for local data directory structure
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
            esgfdatainfo.ESGFDataInfo._enable_debug()

        self.conf = config.Conf(conffile)

        sec = self.conf['ESGFSearch']
        try:
            self.search_service = sec['search_service']
        except KeyError:
            self.search_service = search_service_default

        try:
            self.service_type = sec['service_type']
        except KeyError:
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

        if self._debug:
            print('dbg:ESGFSearch():')
            pprint(vars(self))

    def doSearch(self, params=None, base_url=None):
        """
        Do search via ESGF RESTful API.

        Search results are stored to the :attr:`.datainfo` attributes
        as a list of :class:`esgfdatainfo.ESGFDataInfo` instances.

        If :attr:`aggregate` attribute is ``True``, this method
        obtains URLs of aggregated dataset, else URLs of all of files
        listed in the catalog.

        All of retrieved OPeNDAP URLs can be accessed by :meth:`.data_urls` attribute.

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
            print(f'dbg:ESGFSearch.doSearch():base_url:{base_url}')
            print('dbg:ESGFSeaerch.doSearch():params:')
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

        if self._debug:
            print('dbg:doSearch:numFound:', result['response']['numFound'])

        if (result['response']['numFound'] == 0):
            raise NotFoundError('No catalog found.')

        self.datainfo = [
            esgfdatainfo.ESGFDataInfo(attribs=doc)
            for doc in result['response']['docs']
        ]
        if self._debug:
            for dinfo in self.datainfo:
                print(dinfo.cat_url)

        for dinfo in self.datainfo:
            dinfo.getDataURL(self.aggregate)

        if self._debug:
            print('dbg:ESGFSearch.getDataURLs:')
            for dinfo in self.datainfo:
                print(f"- master id:{dinfo.master_id},\n data_url:")
                pprint(dinfo.data_url)

        for dinfo in self.datainfo:
            dinfo.getDDS() 
            dinfo.findLocalFile(self.base_dir)


    @property
    def cat_urls(self):
        """
        Obtained catalog URLs

        :type: list(str)
        """
        return [dinfo.cat_url for dinfo in self.datainfo]

    @property
    def data_urls(self):
        """
        URLs of each dataset.

        If :attr:`.aggregate` is ``False``, one dataset consists of
        multiple datafile, type of this is list of list(str).

        :type: list(str) or list(list(str))
        """
        return [dinfo.data_url for dinfo in self.datainfo]

    @property
    def local_files(self):
        """
        Paths of existing local file corresponding to the search result.

        :type: list(str) or list(list(str))
        """
        return [dinfo.local_files for dinfo in self.datainfo]



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
}

#: Default fasets for RESTful API.
facets_default = {
    'table_id': 'Amon',
}

# params_default = dict(keywords_default)
# params_default.update(facets_default)


def getDefaultConf():
    """
    Return default config values as a dict.

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
    res['ESGFSearch'] = {
        'search_service': search_service_default,
        'service_type': service_type_default,
        'aggregate': aggregate_default
    }
    res['ESGFSearch.keywords'] = keywords_default
    res['ESGFSearch.facets'] = facets_default
    return res


if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
