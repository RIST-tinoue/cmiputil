#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# xarray with OPeNDAP Aggregation version.
# Using xarray's plot()

from cmiputil import esgfsearch
import matplotlib.pyplot as plt
from pprint import pprint


if (__name__ == '__main__'):

    # setup for search API.
    params = {
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
        'source_id':'MIROC6,MRI-ESM2-0, CNRM-CM6-1',
        'experiment_id': 'piControl, abrupt-4xCO2',
        # 'experiment_id': 'historical',
        # 'experiment_id': 'piControl',
        'variant_label': 'r1i1p1f1,r2i1p1f1',
        'variable': 'tas',
    }

    es = esgfsearch.ESGFSearch()

    # Do search, return list of catalog URLs
    urls = es.getCatURLs(params)

    # get Catalog, then Aggregated datasets.
    aggregate = True
    netcdf = False
    datasets = [es.getDataset(url, aggregate=aggregate, netcdf=netcdf)
                for url in urls]
    datasets = [d for d in datasets if d]
    print('Num of datasets:', len(datasets))

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
