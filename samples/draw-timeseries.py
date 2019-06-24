#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draw time-series of CMIP6 data, searched via RESTful API and accessed
by OPeNDAP.

This is just a "Proof-of-concept" for accessing CMIP6/ESGF data via
cmiputil. Process after opening dataset is a sloppy and dirty hack.
You should implemnt properly by yourself.
"""

from cmiputil import esgfsearch
import argparse
import matplotlib.pyplot as plt
from pprint import pprint
import xarray as xr
from os.path import basename


__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190614'
__date__ = '2019/06/14'


desc = __doc__
epilog = """
"""


def my_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=epilog)
    parser.add_argument(
        '-d', '--debug', action='store_true', default=False)
    parser.add_argument(
        '-c', '--conffile', type=str, default="",
        help='config file')
    parser.add_argument(
        '-l', '--local', action='store_true', default=False,
        help='search local data')
    parser.add_argument(
        'params', type=str, nargs='*', default=None,
        help='key=value series of keyword/facet parameters'
    )

    return parser


def openDatasets(data_urls):
    """
    Open and return dataset object from dataset URLs.

    `data_urls` attribute is obtained by, for example,
    :meth:`ESGFSearch.getDataURLs`.

    If an element of `data_urls` is a list, that is opened as a
    multi-file dataset, via `xarray.open_mfdataset()`.

    """
    res = [_openDataset(url) for url in data_urls]
    datasets = [d for d in res if d]
    return datasets


def _openDataset(url):
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


def openLocalDatasets(data_files):
    """
    Open and return dataset object from local dataset paths.

    Dataset paths are set as :attr:`local_dirs` of `self`, obtained
    by, for example, :meth:`getLocalDirs()`.

    """
    if not data_files:
        datasets = None
    else:
        res = [_openLocalDataset(p) for p in data_files]
        datasets = [d for d in res if d]
    return datasets


def _openLocalDataset(p):
    print('dbg:',p, type(p))
    return xr.open_mfdataset(p, decode_times=False)


def drawFig(datasets):
    """
    Draw timeseries of each dataset

    This is just a quick hack.

    Note:
       ``xarray.DataArray.mean()`` is **NOT** an weighted-average.
    """
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)
    for d in datasets:
        label = ':'.join((d.source_id, d.experiment_id, d.variant_label))
        print(f"plotting {label}")
        # d[d.variable_id].sel(lon=0, lat=0, method='nearest').plot(ax=ax)
        d[d.variable_id].mean(('lon', 'lat')).plot(ax=ax, label=label)
    ax.legend()
    print('Ready to show plot...')
    plt.tight_layout()
    plt.show()
    print('Done.')


def main():
    a = my_parser().parse_args()

    params = {}
    for p in a.params:
        k, v = p.split('=')
        params[k] = v

    if (a.debug):
        esgfsearch.ESGFSearch._enable_debug()
    es = esgfsearch.ESGFSearch(conffile=a.conffile)

    if a.local:
        es.getLocalDirs(params)
        print('Local Directories:')
        pprint(es.local_dirs)
        es.getDataFiles()
        print('Local Dataset files:')
        pprint(es.data_files)
        datasets = openLocalDatasets(es.data_files)
        if datasets:
            print('Num of datasets:', len(datasets))
        else:
            exit(1)

    else:
        # Do search, return a list of catalog URLs
        es.doSearch(params)
        es.getCatURLs()
        print('Catalog URLs:')
        pprint(es.cat_urls)

        # Get catalog, then get URLs of dataset
        es.getDataURLs()
        print('Dataset URLs:')
        pprint(es.data_urls)

        # from URLs, open and return datasets
        datasets = openDatasets(es.data_urls)

        if datasets:
            print(f'Num of datasets found: {len(datasets)}')
        else:
            exit(1)

    # Analyse data, draw figure, or do what you want.
    drawFig(datasets)


if (__name__ == '__main__'):
    main()
