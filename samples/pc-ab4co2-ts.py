#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare piControl and abrupt-4xCO2 timeseries of tas.

"""
from cmiputil import esgfsearch
from cmiputil.timer import timer
from pprint import pprint
from os.path import basename
from pathlib import Path
import argparse
import json
from cftime import num2date
import matplotlib.pyplot as plt

__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190614'
__date__ = '2019/06/14'


desc = __doc__
epilog = """
`Experiment_id` and `variable` are forced as above, regardless of the
setting in config file and command line option.
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
        'params', type=str, nargs='*', default=None,
        help='key=value series of keyword/facet parameters'
    )

    return parser


def composeMeta(datasets):
    """
    Compose meta info dictionaries from a list of xarray.Dataset
    obtained by getDatasets().

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
        print(f"Compose meta info for: {dsname}")
        try:
            var = ds[ds.variable_id]
        except IndexError:
            print(f"{ds.variable_id} not found in {dsname}")
            raise

        var_id = getattr(var, 'name')

        t_size = getattr(ds.time, 'size', None)
        # Sometimes time.unit is missing, num2date raise AttirbuteError.
        t_units = getattr(ds.time, 'units', None)
        try:
            t_range = str(num2date(ds.time[[0, -1]], t_units))
        except AttributeError:
            t_range = str(ds.time.data[[0,-1]])

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
            't_range': t_range
        })

    return meta


def drawPlot(datasets):
    # to shut up the warning message...
    # from pandas.plotting import register_matplotlib_converters
    # register_matplotlib_converters()

    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(111)

    for d in datasets:
        label = ':'.join((d.source_id, d.experiment_id, d.variant_label))
        print(f"plotting {label}")
        try:
            # Just a quick hack, should get area averaged.
            # d['tas'].sel(lon=0, lat=0, method='nearest')\
            #         .plot(ax=ax, label=label)
            d[d.variable_id].mean(('lon', 'lat')).plot(ax=ax, label=label)
        except RuntimeError as e:
            print('Skip error:', e.args)
            continue
    ax.legend()
    print('Ready to plot...')
    plt.show()
    print('Done.')


def main():
    a = my_parser().parse_args()

    params = {}
    for p in a.params:
        k, v = p.split('=')
        params.update({k: v})

    # force these two experiment and variable
    params_force = {
        'experiment_id': 'piControl, abrupt-4xCO2',
        'variable': 'tas'}
    params.update(params_force)

    if (a.debug):
        esgfsearch.ESGFSearch._enable_debug()
    es = esgfsearch.ESGFSearch(conffile=a.conffile)

    with timer('getting Catalog URLs'):
        es.getCatURLs(params)

    if es.cat_urls:
        pprint(es.cat_urls)

    with timer('getting Dataset URLs'):
        es.getDataURLs()
        
    if es.data_urls:
        pprint(es.data_urls)


    with timer('getting Dataset'):
        es.getDatasets()

    print(f'Num of datasets found: {len(es.datasets)}')

    with timer('constructing meta info'):
        meta = composeMeta(es.datasets)
        outfile = 'meta_info.json'
        Path(outfile).write_text(json.dumps(meta, indent=4))
        print(f'meta info wriiten to {outfile}')

    with timer('drawing graph'):
        # draw timeseries of each dataset
        drawPlot(es.datasets)


if (__name__ == '__main__'):
    main()
