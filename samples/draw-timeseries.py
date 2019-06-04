#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draw time-series of CMIP6 data.

xarray with OPeNDAP Aggregation version.
Using xarray's plot()
"""

from cmiputil import esgfsearch
import argparse
import matplotlib.pyplot as plt
from pprint import pprint


__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190602'
__date__ = '2019/06/02'


desc = __doc__
epilog = """
"""


def my_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=epilog)
    parser.add_argument(
        '-c', '--conffile', type=str, default=None,
        help='config file')
    parser.add_argument(
        'params', type=str, nargs='*', default=None
    )

    return parser


def drawFig(datasets):
    # draw timeseries of each dataset
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)

    for d in datasets:
        # Just a quick hack, should get temporal/spatial averaged.
        print(type(d))
        vals = d['tas'].sel(lon=0, lat=0, method='nearest')
        vals.plot(ax=ax, add_legend=True)
        ax.legend()
    print('Ready to show plot...')
    plt.show()
    print('Done.')


if (__name__ == '__main__'):

    parser = my_parser()
    a = parser.parse_args()
    pprint(vars(a))

    params={}
    for p in a.params:
        k, v = p.split('=')
        params[k] = v


    es = esgfsearch.ESGFSearch(conffile=a.conffile)

    # Do search, return list of catalog URLs
    urls = es.getCatURLs(params)
    print('Catalog URLs:')
    pprint(urls)

    # get Catalog, then Aggregated datasets.
    aggregate = None
    datatype_xarray = None
    datasets = [es.getDataset(url, aggregate=aggregate, datatype_xarray=datatype_xarray)
                for url in urls]
    datasets = [d for d in datasets if d]
    print('Num of datasets:', len(datasets))
    if (len(datasets) < 1):
        exit(1)
    drawFig(datasets)
