#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relocate CMIP6 datafiles depending on their global attributes.

Input file(s) must be valid CMIP6 CF-Compliant netCDF. Relocation
directory will be constructed by DRS, under current directory by
default, or under prefix(-p).

DRS demands that directory must be contains "version" as the last
part, but since that is "the only DRS element that is not stored as
a global attribute" (see http://goo.gl/v1drZl), this is not
decided by the filename nor global attributes.

So you have to specify "--verstr" (or "-v").
"""

from cmiputil import drs
import netCDF4 as nc
import argparse
from pathlib import Path

__version__ = '0.1'
__author__ = 'T.Inoue'
__date__ = '2019/04/27'


def relocationPath(ncfile, verstr='v00000000', prefix=None):
    """
    Construct directory name for relocation of given file.

    Parameters
    ----------
    ncfile : str : filename
    prefix : path-like
    verstr : str

    Return
    ------
    path-like : path for given file
    """

    with nc.Dataset(ncfile, "r") as ds:
        attrs = {a: getattr(ds, a, None) for a in drs.DRS().requiredAttribs}
    attrs = {a: v for a, v in attrs.items() if v != 'none'}

    p = Path(ncfile)
    if (p.is_file()):
        p = p.parent
    d_attrs = drs.DRS().splitDirName(p)

    if (getattr(attrs, 'version', None) is None):
        attrs['version'] = verstr
    else:
        verstr = getattr(d_attrs, 'version', None)
        if (verstr):
            attrs['version'] = verstr

    return Path(drs.DRS(**attrs).dirName(prefix=prefix),
                drs.DRS(**attrs).fileName())


def validFileNameFrom(ncfile):
    """
    Construct filename valid as DRS from global attributes.

    Parameters
    ----------
    ncflie : str

    Return
    ------
    str
    """

    with nc.Dataset(ncfile, "r") as ds:
        attrs = {a: getattr(ds, a, None) for a in drs.DRS().requiredAttribs}
    attrs = {a: v for a, v in attrs.items() if v != 'none'}

    return drs.DRS(**attrs).fileName()


def doRelocateFile(s, d, overwrite=False):
    """
    Relocate file `s` to the path `d`.

    You can NOT rename file itself.

    If d is not exist yet, mkdir'ed silently.

    If file is already exist in d, raise FileExistsError, unless
    overwrite=True.

    Parameter
    ---------
    s : path-like: source file
    d : path-like: destination path
    overwrite(optional) : logical : overwrite file in destination, or not.

    Return
    ------
    path-like : pathname of relocated file.

    """

    sf = Path(s)
    dd = Path(d)

    if (dd.is_file()):
        raise FileExistsError('destination is existing file:', dd)

    df = dd / sf.name

    print(sf, '->', df)

    if (not Path(s).exists()):
        raise FileNotFoundError(s)

    if (df.exists() and not overwrite):
        raise FileExistsError(df)

    dd.mkdir(parents=True, exist_ok=True)
    sf.rename(df)

    return df


if (__name__ == '__main__'):

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'files', nargs='+', type=str, metavar='nc_file')
    parser.add_argument(
        '-w', '--overwrite', action='store_true', default=False)
    parser.add_argument(
        '-p', '--prefix', type=str, default=None,
        help='prefix for relocation directory')
    parser.add_argument(
        '-z', '--dry_run', action='store_true', default=False)
    parser.add_argument(
        '-v', '--verstr', type=str, default=None,
        help='<version> string for DRS')

    args = parser.parse_args()

    print('dry_run:', args.dry_run)
    print('overwrite:', args.overwrite)
    print('prefix:', args.prefix)
    print('verstr:', args.verstr)

    a = {}
    if (args.prefix):
        a['prefix'] = args.prefix
    if (args.verstr):
        a['verstr'] = args.verstr

    srcdst = {s: relocationPath(s, **a) for s in args.files}

    for s, d in srcdst.items():
        print(s, '->', d)
        if (not args.dry_run):
            doRelocateFile(s, d, args.overwrite)
