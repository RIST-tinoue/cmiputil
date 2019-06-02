#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmiputil import esgfsearch
from cmiputil.timer import timer
from pprint import pprint
from os.path import basename
from pathlib import Path
import json
from cftime import num2date
import matplotlib.pyplot as plt

def composeMeta(datasets):
    """
    Compose meta info dictionaries from a list of xarray.Dataset
    obtained by getDataset().

    Returns `meta` dictionary.

    """
    if datasets is None:
        return None

    # print(type(datasets))
    meta = {}
    for ds in datasets:
        if not ds:
            continue
        # print(type(ds))
        dsname = basename(ds.further_info_url)
        print("Compose meta info for:", dsname)
        try:
            var = ds[ds.variable_id]
        except IndexError:
            print("{} not found in {}".format(ds.variable_id, dsname))
            raise IndexError

        times = ds['time']
        t_units = getattr(times, 'units', None)
        t_size = getattr(times, 'size', None)
        var_id = getattr(var, 'name')

        meta.setdefault(ds.experiment_id, []).append({
            # No filepath() or path related attributes in xarray.dataset.
            # 'file': ds.filepath(),
            'source': ds.source_id,
            'experiment_id': ds.experiment_id,
            'variable|id': var_id,
            'variable|long_name': var.long_name,
            'variabel|units': var.units,
            'calendar': ds['time'].calendar,
            'branch_time': ds.branch_time_in_parent,
            't_units': t_units,
            't_size': t_size,
            't_range': str(num2date(times[[0, -1]], times.units))
        })

    return meta


def drawPlot(datasets):
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)
    ax.set_title('tas')
    ax.set_xlabel('time')
    ax.set_ylabel('K')

    for d in datasets:
        label = d.source_id+': '+d.experiment_id+': '+d.variant_label
        print(label)
        times = num2date(d['time'], d['time'].units)
        # Just a quick hack, should get area averaged.
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


if (__name__ == '__main__'):
    params = {
        # 'source_id': 'MIROC6',
        # 'source_id': 'CNRM-CM6-1',
        # 'source_id': 'IPSL-CM6A-LR',    #<- not found error for aggregation dataset
        # 'source_id': 'GISS-E2-1-G',
        # 'source_id': 'CanESM5',
        # 'source_id': 'CESM2',
        # 'source_id': 'BCC-CSM2-MR',  # <- times in cftime.DatetimeNoLeap, causes error in plt.plot()
        'source_id': 'MIROC6,BCC-CSM2-MR',
        'experiment_id': 'piControl, abrupt-4xCO2',
        # 'experiment_id': 'historical',
        'variant_label': 'r1i1p1f1,r2i1p1f1',
        'variable': 'tas',
    }

    es = esgfsearch.ESGFSearch()
    urls = es.getCatURLs(params)

    aggregate = False
    netcdf = False
    with timer('getting Datasets'):
        datasets = [es.getDataset(url, aggregate=aggregate, netcdf=netcdf)
                     for url in urls]

    with timer('constructing meta info'):
        meta = composeMeta(datasets)
        outfile = 'meta_info.json'
        Path(outfile).write_text(json.dumps(meta, indent=4))
        print(f'meta info wriiten to {outfile}')


    with timer('drawing graph'):
        # draw timeseries of each dataset
        drawPlot(datasets)

