#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draw time-series of CMIP6 data, searched via RESTful API and accessed
by OPeNDAP.

This is just a "Proof-of-concept" for accessing CMIP6/ESGF data via
cmiputil. 
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
Process after opening dataset is a sloppy and dirty hack.
You should implemnt properly by yourself.
"""

def my_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=epilog)
    parser.add_argument(
        '-c', '--conffile', type=str, default="",
        help='config file')
    parser.add_argument(
        'params', type=str, nargs='*', default=None,
        help='key=value series of keyword/facet parameters'
    )

    return parser


def drawFig(datasets):
    """
    Draw timeseries of each dataset

    This is just a quick hack, should get temporal/spatial averaged.
    """
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)
    for d in datasets:
        d['tas'].sel(lon=0, lat=0, method='nearest').plot(ax=ax)
    ax.legend()
    print('Ready to show plot...')
    plt.tight_layout()
    plt.show()
    print('Done.')


def main():
    a = my_parser().parse_args()

    params={}
    for p in a.params:
        k, v = p.split('=')
        params[k] = v

    es = esgfsearch.ESGFSearch(conffile=a.conffile)

    # Do search, return a list of catalog URLs
    urls = es.getCatURLs(params)
    print('Catalog URLs:')
    pprint(urls)

    # Get catalog, then get aggregated datasets.
    datasets = [es.getDataset(url)
                for url in urls]
    print('Num of datasets:', len(datasets))
    if (len(datasets) < 1):
        exit(1)

    # Analyse data, draw figure, or do what you want.
    drawFig(datasets)


if (__name__ == '__main__'):
    main()
