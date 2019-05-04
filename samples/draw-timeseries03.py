#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# xarray with OPeNDAP Aggregation version.
# Using xarray's plot()

from cmiputil.esgfsearch import fields_default, getCatURLs, getDataset
import matplotlib.pyplot as plt
from pprint import pprint


if (__name__ == '__main__'):

    # setup for search API.
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
        'source_id':'MIROC6,MRI-ESM2-0, CNRM-CM6-1',
        'experiment_id': 'piControl, abrupt-4xCO2',
        # 'experiment_id': 'historical',
        # 'experiment_id': 'piControl',
        'variant_label': 'r1i1p1f1,r2i1p1f1',
        'variable': 'tas',
    }

    params = fields_default
    params.update(params_update)
    print('Search params(keywords and facets):')
    pprint(params)

    # Do search, return list of catalog URLs
    urls = getCatURLs(params)

    # get Catalog, then Aggregated datasets.
    datasets = []
    for url in urls:
        print("Processing Catalog:", url)
        d = getDataset(url)
        if (d is not None):
            datasets.append(d)
    print('Num of datasets:', len(datasets))
    if (len(datasets) == 0):  # nothing found
        raise Exception('Nothing found')

    # draw timeseries of each dataset
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)

    for d in datasets:
        vals = d['tas'].sel(lon=0, lat=0, method='nearest')
        vals.plot(ax=ax,add_legend=True)
        ax.legend()
    print('Ready to show plot...')
    plt.show()
    print('Done.')
