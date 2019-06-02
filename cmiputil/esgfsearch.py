#!/usr/bin/env python3
"""
Search by ESGF RESTful API, get and open multiple datafiles,
create meta info.

See https://earthsystemcog.org/projects/cog/esgf_search_restful_api
for the detail ESGF RESTful API.

This version uses
`siphon <https://www.unidata.ucar.edu/software/siphon/>`_ and
`xarray <http://xarray.pydata.org/>`_.

"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190602'
__date__ = '2019/06/02'

from cmiputil import drs, config
from pathlib import Path
import urllib3
import json
import xarray as xr
import netCDF4 as nc
from siphon.catalog import TDSCatalog
from pprint import pprint


class NotFoundError(Exception):
    pass


class ESGFSearch():
    """
    Search by ESGF RESTful API, get to the datafile via OPenDAP.


    If `conffile` is ``None``, use default conffile, defined in
    :mod:`config`.

    This class read below sections from conffile;

    - [ESGFSearch]
        - `cmip6_data_dir`: CMIP6 date directory
        - `search_service`: the base URL of the search service at a ESGF Index Node
        - `service_type`: ``search`` or ``wget``
    - [ESGFSearch.keywords]
    - [ESGFSearch.facets]


    Args:
        conffile (path-like): configure file
    """
    def __init__(self, conffile=None):
        # self.search_service = search_service_default
        # self.service_type = service_type_default
        # self.keywords = keywords_default
        # self.facets = facets_default
        # self.params = self.keywords.copy()
        # self.params.update(self.facets)

        self.conf = config.Conf(conffile)
        self.search_service = self.conf['ESGFSearch']['search_service']
        self.service_type = self.conf['ESGFSearch']['service_type']
        self.params = dict(self.conf['ESGFSearch.keywords'].items())
        self.params.update(dict(self.conf['ESGFSearch.facets'].items()))

    def getCatURLs(self, params=None, base_url=None):
        """
        Using ESGF RESTful API, get URLs for OPeNDAP TDS catalog.

        Args:
            params (dict): keyword parameters and facet parameters.
            base_url : base URL of the ESGF search service.

        Raises:
            NotFoundError: raised if no catalog found.

        Return:
            list of str:  TDS catalog URLs found.

        If `base_url` is None, :data:`.search_service` +
        :data:`.service_type` is used.

        `params` is to *update* (use `update()` method of python dict)
        to the ones read from conf file.

        TODO:
            - How to enable *a negative facet* of RESTful API ?
        """
        if params:
            self.params.update(params)
        if not base_url:
            base_url = self.search_service + self.service_type

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

        urls = []
        for r in result['response']['docs']:
            for l in r['url']:
                (url, mime, service) = l.split('|')
                # select TDS catalog
                if (service == 'THREDDS'):
                    urls.append(url)

        return urls

    def getDataset(self, url, aggregate=True, netcdf=False):
        """
        From given URL of TDS catalog, return xarray or netCDF4 dataset.

        A URL of TDS catalog is obtained by, for example,
        :meth:`getCatURLs()`.

        If `aggregate` is ``True``, access aggregated dataset, else
        access all of files listed in the catalog.

        Args:
            url(str): url of TDS catalog
            aggregate(bool): if True, access aggregate link in TDS catalog.
            netcdf(bool): if True return netCDF4's dataset, instead of xarray's.
        Returns:
            xarray.dataset() or xarray.mfdataset() or netCDF4.Dataset() or
            netCDF4.MFDataset() or None: opened dataset

        """
        try:
            cat = TDSCatalog(url)
        except Exception as e:
            print('Error in siphon.TDSCatalog():', e.args)
            raise

        if aggregate:
            # construct base url
            data_url = cat.base_tds_url
            for s in cat.services[:]:
                if (s.service_type.lower == 'opendap'):
                    data_url += s.base
                    break

            # url of Aggregated dataset
            ds = cat.datasets[-1]   # Is this universal ?

            data_url += ds.url_path
            try:
                if (netcdf):
                    ds = nc.Dataset(data_url, 'r')
                else:
                    ds = xr.open_dataset(data_url,
                                         decode_times=False, decode_cf=False)
            except ValueError as e:
                print(e.args)
                raise e
            except (IOError, AttributeError) as e:
                print("Error in Opening dataset:", e.args)
                print("  from url:", data_url)
                return None
        else:
            urls = [x.access_urls['OpenDAPServer']
                    for x in cat.datasets.values()
                    if 'OpenDAPServer' in x.access_urls]
            urls.sort()

            try:
                if (netcdf):
                    ds = nc.MFDataset(urls)
                else:
                    ds = xr.open_mfdataset(urls, decode_cf=False)
            except IOError as e:
                print("Error in xr.open_mfdataset:", e.args)
                print("  Skip", url)
                return None

        return ds


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
            >>> params_update = {'source_id': 'MIROC6', 'experiment_id': 'historical',
            ...    'variant_label': 'r1i1p1f1', 'variable': 'tas', }
            >>> params = params_default
            >>> params.update(params_update)
            >>> str(getLocalPath(params, base_dir='~/Data/'))
            '~/Data/CMIP6/*/*/MIROC6/historical/r1i1p1f1/Amon/*/*/*/*_Amon_MIROC6_historical_r1i1p1f1_*_*.nc'
        """
        d = drs.DRS(**params)
        p = d.dirName(prefix=base_dir)
        f = d.fileName()
        return p / f


########################################################################
# defaults

#: Default search service URL
search_service_default = 'http://esgf-node.llnl.gov/esg-search/'
# search_service_default = 'http://esgf-data.dkrz.de/esg-search/'

#: Default service type
service_type_default = 'search'

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
    'project': 'CMIP6',
    'table_id': 'Amon',
    'frequency': 'mon',
    'variant_label': 'r1i1p1f1',
    }

# params_default = dict(keywords_default)
# params_default.update(facets_default)


def getDefaultConf():
    """
    Set default values for config file.

    Intended to be called before config.Conf.writeSampleConf()

    Example:
       >>> conf = config.Conf('')
       >>> conf.setDefaultSection()
       >>> conf.read_dict(getDefaultConf())
       >>> conf.writeSampleConf('/tmp/cmiputil.conf', overwrite=True)
    """
    res = {}
    res['ESGFSearch'] = {'search_service': search_service_default,
                         'service_type': service_type_default}
    res['ESGFSearch.keywords'] =  keywords_default
    res['ESGFSearch.facets'] = facets_default
    return res



if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
