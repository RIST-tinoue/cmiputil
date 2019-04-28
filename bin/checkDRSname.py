#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check file/directory name is valid as DRS.

"""

from cmiputil import drs
import netCDF4 as nc
import argparse
from pprint import pprint
import sys

__version__ = '0.1'
__author__ = 'T.Inoue'
__date__ = '2019/04/28'


def isValidFileAsDRS(f, verbose=True):

    f_attrs = drs.DRS().splitFileName(f)
    d = drs.DRS()

    results = {}
    results = {a: d.isValid4Attr(v, a) for a, v in f_attrs.items()}
    res = all(results.values())

    if verbose and not res:
        print('in {}:'.format(f))
        for a, v in results.items():
            if (not v):
                print('  <{}> in invalid: "{}"'.format(a, f_attrs[a]))

    return res


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'files', nargs='+', type=str, metavar='nc_file')
    parser.add_argument(
        '-v', '--verbose', action="store_true", default=False)

    args = parser.parse_args()

    count = 0
    for f in args.files:
        if (not isValidFileAsDRS(f, args.verbose)):
            print("{} is invalid.".format(f))
            count += 1
        else:
            print("{} is valid.".format(f))
    if (count > 0):
        sys.exit(1)
