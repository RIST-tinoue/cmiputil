#!/usr/bin/env python3
"""
Search by ESGF RESTful API, get and open multiple datafiles,
create meta info.

Using siphon and xarray version.
"""

import urllib3
import json
from pprint import pprint
from os.path import basename
import xarray as xr
import netCDF4 as nc
from siphon.catalog import TDSCatalog
import matplotlib.pyplot as plt

DEBUG = False
VERBOSE = False

# defaults
search_service = 'http://esgf-node.llnl.gov/esg-search/'
# search_service = 'http://esgf-data.dkrz.de/esg-search/'
service_type = 'search'
keyword_defaults = {
    'format': r'application/solr+json',
    'replica': 'false',
    'latest': 'true',
    'limit': 10000,
    'type': 'Dataset',  # must be to get catalog
    'fields': 'url',
    }
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
    `fields` consists of keyword parameters and facet parameters.

    See https://earthsystemcog.org/projects/cog/esgf_search_restful_api
    for ESGF RESTful API.

    Parameters:
    base_url : search_searvice + search_type
    fields : dict, will be given to http.request()

    Return:
    urls : list of TDS catalog URLs found.
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
    if ( r.status != 200):
        print('Bad Status:',r.status)
        print(r.data.decode())
        return []
    # don't know why but returned are bytes, not str.
    result = json.loads(r.data.decode())


    if (DEBUG):
        print('Num found:',result['response']['numFound'])
    if (result['response']['numFound'] == 0):
        print('GetCatURLs: Nothing found.')
        return []

    if (DEBUG):
        pprint(result['response']['docs']) #dbg


    urls = []
    for r in result['response']['docs']:
        for l in r['url']:
            (url,mime,service) = l.split('|')
            if (DEBUG):
                print(service,':',url)
            # select TDS catalog
            if (service == 'THREDDS'):
                urls.append(url)

    if (VERBOSE):
        print('Num of catalogs found:',len(urls))

    return urls


def getDataset(url, netcdf=False):
    """
    From given url of TDS catalog, open catalog and get all urls of files in it,
    open as xarray.mfdataset and return it.

    Seems to be better to use getAggDataset() if available.

    Parameters:
    url : url of TDS catalog

    Returns:
    ds : xarray.mfdataset, or None if unable to open
    """
    if (VERBOSE):
        print("Processing Catalog:",url)

    try:
        cat = TDSCatalog(url)
    except Exception as e:
        print('Error in siphon.TDSCatalog():')
        pprint(e.args)
        return None

    urls = [x.access_urls['OpenDAPServer']
            for x in cat.datasets.values()
            if 'OpenDAPServer' in x.access_urls]

    if (VERBOSE):
        print("Num of files in this catalog:", len(urls))

    if (DEBUG):
        pprint(urls)

    try:
        if (netcdf):
            ds = nc.MFDataset(urls)
        else:
            ds = xr.open_mfdataset(urls, decode_cf=False)
    except IOError as e:
        print("Error in xr.open_mfdataset: ")
        pprint(e.args)
        print("skip",url)
        return None

    if (VERBOSE):
        print("Opened dataset:", basename(ds.further_info_url))

    return ds


def getAggDataset(url, netcdf=False):
    """
    get Aggregated Dataset from catarog URL.

    return Opened xarray dataset.
    """
    if (VERBOSE):
        print("Processing Catalog:",url)

    try:
        cat = TDSCatalog(url)
    except Exception as e:
        print('Error in siphon.TDSCatalog():')
        pprint(dir(e))
        return None

    data_url = cat.base_tds_url
    for s in cat.services[:]:
        if (s.service_type == 'OpenDAP'):
            data_url += s.base
            break

    # url of Aggregated dataset
    ds = cat.datasets[-1]
    if (DEBUG):
        pprint(vars(ds))

    data_url += ds.url_path
    if (VERBOSE):
        print('URL of Aggregated dataset:',data_url)

    try:
        if (netcdf):
            d = nc.Dataset(data_url, 'r')
        else:
            d = xr.open_dataset(data_url, decode_cf=False)
    except (IOError, AttributeError) as e:
        print("Error in Opening dataset from url:",data_url)
        pprint(e.args)
        return None

    return d


def calcGMean(d):

    return None





if (__name__ == '__main__'):

    # with timer('main'):
    #     main()
    ### setup for search API.
    params_update = {
        # 'source_id': 'MIROC6',
        # 'source_id': 'MRI-ESM2-0',
        # 'source_id': 'CNRM-CM6-1',
        # 'source_id': 'CNRM-ESM2-1',
        # 'source_id': 'IPSL-CM6A-LR',    #<- not found error for aggregation dataset
        # 'source_id': 'GISS-E2-1-G',
        # 'source_id': 'CanESM5',
        # 'source_id': 'CESM2',
        # 'source_id': 'E3SM-1-0',
        # 'source_id': 'GFDL-CM4',
        # 'source_id': 'BCC-CSM2-MR',
        # 'source_id': 'CESM2-WACCM',
        # 'source_id': 'EC-Earth3-LR',
        # 'experiment_id': 'piControl, abrupt-4xCO2',
        'experiment_id': 'historical',
        'variant_label': 'r1i1p1f1',
        'variable': 'tas',
    }

    params = fields_default
    params.update(params_update)
    print('Search params(keywords and facets):')
    pprint(params) 


    ### Do search.
    urls = getCatURLs(params)
    print('Catalog Search Result:',len(urls))
    # pprint(urls)



    ### get Catalog, then Aggregated datasets.
    datasets = []
    for url in urls:
        print("Processing Catalog:",url)

        d = getAggDataset(url)
        # d = getDataset(url)
        if (d is not None):
            datasets.append(d)
    print('Num of datasets:', len(datasets))
    if (len(datasets) == 0 ):  # nothing found
        # return False
        raise Exception

    ### draw timeseries of each dataset
    fig = plt.figure(figsize=(16,8))
    ax = fig.add_subplot(111)
    ax.set_title('tas')
    ax.set_xlabel('time')
    ax.set_ylabel('K')

    for d in datasets:
        label = d.source_id+': '+d.experiment_id+': '+d.variant_label
        print(label)
        times = nc.num2date(d['time'], d['time'].units)
        values = d['tas'].sel(lon=0, lat=0, method='nearest')

        try:
            ax.plot(times, values, label=label)
            ax.legend()
        except RuntimeError as e:
            print('Skip error:',e.args)
            continue

    plt.show()
    print('Done.')


