#!/usr/bin/env python3
"""
Search by ESGF RESTful API, get and open multiple datafiles,
create meta info.

See https://earthsystemcog.org/projects/cog/esgf_search_restful_api
for ESGF RESTful API.


This version uses siphon and xarray.
"""

import urllib3
import json
from pprint import pprint
from os.path import basename
import xarray as xr
import netCDF4 as nc
from siphon.catalog import TDSCatalog
import matplotlib.pyplot as plt

class NotFoundError(Exception):
    pass


# defaults

#: Doc default search service URL
search_service = 'http://esgf-node.llnl.gov/esg-search/'
# search_service = 'http://esgf-data.dkrz.de/esg-search/'

#: Doc default service type
service_type = 'search'

#: Doc default keywords for RESTful API.
keyword_defaults = {
    'format': r'application/solr+json',
    'replica': 'false',
    'latest': 'true',
    'limit': 10000,
    'type': 'Dataset',  # must be to get catalog
    'fields': 'url',
    }

#: Doc default fasets for RESTful API.
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
        base_url : search_searvice + service_type
    Raises:
        NotFoundError: raised if no catalog found.
    Return:
        list:  TDS catalog URLs found.

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


if (__name__ == '__main__'):

    # with timer('main'):
    #     main()

    # setup for search API.
    params_update = {
        'source_id': 'MIROC6',
        # 'source_id': 'MRI-ESM2-0',
        # 'source_id': 'CNRM-CM6-1',    #<- Catalog not found
        # 'source_id': 'CNRM-ESM2-1',    #<- Catalog not found
        # 'source_id': 'IPSL-CM6A-LR',    #<- Couldn't resolve host name
        # 'source_id': 'GISS-E2-1-G',   # <- times in cftime.DatetimeNoLeap, causes error in plt.plot()
        # 'source_id': 'CanESM5',   # <- times in cftime.DatetimeNoLeap, causes error in plt.plot()
        # 'source_id': 'CESM2',   # <- times in cftime.DatetimeNoLeap, causes error in plt.plot()
        # 'source_id': 'E3SM-1-0',  #<- Catalog not found
        # 'source_id': 'GFDL-CM4',  #<- Catalog not found
        # 'source_id': 'BCC-CSM2-MR',  # <- times in cftime.DatetimeNoLeap, causes error in plt.plot()
        # 'source_id': 'CESM2-WACCM',  # <- times in cftime.DatetimeNoLeap, causes error in plt.plot()
        # 'source_id': 'EC-Earth3-LR',  #<- Catalog not found
        # 'experiment_id': 'piControl, abrupt-4xCO2',
        'experiment_id': 'historical',
        'variant_label': 'r1i1p1f1',
        'variable': 'tas',
    }

    params = fields_default
    params.update(params_update)
    print('Search params(keywords and facets):')
    pprint(params)

    # Do search.
    try:
        urls = getCatURLs(params)
    except NotFoundError as e:
        print('### No Catalog found, sorry.')
        raise e
    finally:
        print('Catalog Search Result:', len(urls))
        # pprint(urls)

    # get Catalog, then Aggregated datasets.
    datasets = []
    for url in urls:
        print("Processing Catalog:", url)
        d = getDataset(url, aggregate=False, netcdf=False)
        if (d is not None):
            datasets.append(d)
    print('Num of datasets:', len(datasets))
    if (len(datasets) == 0):  # nothing found
        raise NotFoundError('No datasets found')

    # draw timeseries of each dataset
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)
    ax.set_title('tas')
    ax.set_xlabel('time')
    ax.set_ylabel('K')

    import cftime
    for d in datasets:
        label = d.source_id+': '+d.experiment_id+': '+d.variant_label
        print(label)
        # d = xr.decode_cf(d)
        times = cftime.num2date(d['time'], d['time'].units)
        values = d['tas'].sel(lon=0, lat=0, method='nearest')

        try:
            ax.plot(times, values, label=label)
            ax.legend()
        except RuntimeError as e:
            print('Skip error:', e.args)
            continue

    print('Ready to plot...')
    plt.show()
    print('Done.')
