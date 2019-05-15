#!/usr/bin/env python3
"""
Search by ESGF RESTful API, get and open multiple datafiles,
create meta info.

See https://earthsystemcog.org/projects/cog/esgf_search_restful_api
for the detail ESGF RESTful API.


This version uses
`siphon <https://www.unidata.ucar.edu/software/siphon/>`_ and
`xarray <http://xarray.pydata.org/>`_.

See ``if (__name__ == '__main__'):`` section in the source file for
the example usage.


"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190509'
__date__ = '2019/05/09'

from cmiputil.drs import DRS
from pathlib import Path
import urllib3
import json
import xarray as xr
import netCDF4 as nc
from siphon.catalog import TDSCatalog


class NotFoundError(Exception):
    pass


# defaults

#: Default search service URL
search_service = 'http://esgf-node.llnl.gov/esg-search/'
# search_service = 'http://esgf-data.dkrz.de/esg-search/'

#: Default service type
service_type = 'search'

#: Default keywords for RESTful API.
keyword_defaults = {
    'format': r'application/solr+json',
    'replica': 'false',
    'latest': 'true',
    'limit': 10000,
    'type': 'Dataset',  # must be to get catalog
    'fields': 'url',
    }

#: Default fasets for RESTful API.
facet_defaults = {
    'project': 'CMIP6',
    'table_id': 'Amon',
    'frequency': 'mon',
    'variant_label': 'r1i1p1f1',
    }

fields_default = dict(keyword_defaults)
fields_default.update(facet_defaults)


# from contextlib import contextmanager
# import time

# @contextmanager
# def timer(name):
#     """
#     Use as:

#          with timer('process train'):
#              hogehoge()


#     """

#     t0 = time.time()
#     yield
#     # print(f'[{name}] done in {time.time() - t0:.0f} s')


def getCatURLs(fields, base_url=None):
    """
    Using ESGF RESTful API, get URLs for OPeNDAP TDS catalog.

    Args:
        fields(dict): keyword parameters and facet parameters.
        base_url : base URL of the ESGF search service.
    Raises:
        NotFoundError: raised if no catalog found.
    Return:
        list of str:  TDS catalog URLs found.

    If `base_url` is None, :data:`.search_service` +
    :data:`.service_type` is used.

    `field` is initialized by :data:`.keyword_defautls` and
    :data:`.facet_defaults`.

    """
    if (base_url is None):
        base_url = search_service+service_type

    http = urllib3.PoolManager()
    try:
        r = http.request('GET', base_url, fields=fields)
    except Exception as e:
        print('Error in http.request():')
        print(e.args)
        raise e
        return []
    if (r.status != 200):
        print('Bad Status:', r.status)
        print(r.data.decode())
        return []
    # don't know why but returned are bytes, not str.
    result = json.loads(r.data.decode())

    if (result['response']['numFound'] == 0):
        raise NotFoundError('GetCatURLs: No catalog found.')

    urls = []
    for r in result['response']['docs']:
        for l in r['url']:
            (url, mime, service) = l.split('|')
            # select TDS catalog
            if (service == 'THREDDS'):
                urls.append(url)

    return urls


def getDataset(url, aggregate=True, netcdf=False):
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
        raise e

    if (aggregate):
        # construct base url
        data_url = cat.base_tds_url
        for s in cat.services[:]:
            if (s.service_type == 'OpenDAP'):
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


def getLocalPath(fields, base_dir=None):
    """
    Search local data directory for CMIP6 data.

    Using same interface with getCatURLs()

    Args:
        fields(dict): keyword parameters and facet parameters.
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
        >>> params = fields_default
        >>> params.update(params_update)
        >>> str(getLocalPath(params, base_dir='~/Data/'))
        '~/Data/CMIP6/*/*/MIROC6/historical/r1i1p1f1/Amon/*/*/*/*_Amon_MIROC6_historical_r1i1p1f1_*_*.nc'
    """
    d = DRS(allow_asterisk=True, **fields)
    p = Path(d.dirName(prefix=base_dir))
    f = Path(d.fileName())
    return p / f

if (__name__ == '__main__'):
    from cmiputil import drs
    import doctest
    doctest.testmod()
