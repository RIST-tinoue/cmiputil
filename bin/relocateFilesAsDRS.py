#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relocate CMIP6 datafiles depending on their global attributes.
"""

from cmiputil import drs
import argparse
from pathlib import Path

__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190525'
__date__ = '2019/05/25'

verstr_default = 'v00000000'

desc = __doc__
epilog = """
Input file(s) must be valid CMIP6 CF-Compliant netCDF. Relocation
directory will be constructed by DRS, under current directory by
default, or under prefix(``-p``).

DRS demands that directory must be contains the attribute <version> as
the last part, but since that is "the only DRS element that is not
stored as a global attribute" (see http://goo.gl/v1drZl), this is not
decided by the filename nor global attributes.

So you have to specify it via ``--verstr`` (or ``-v``).
"""


def my_parser():
    parser = argparse.ArgumentParser(
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc,
        epilog=epilog)
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
    parser.add_argument(
        '-d', '--debug', action='store_true', default=False)

    return parser


def relocationPath(ncfile, verstr=None, prefix=None):
    """
    Construct directory/file name for relocation of given file.

    Parameters
    ----------
    ncfile : str : filename
    prefix : path-like
    verstr : str

    Return
    ------
    path-like : destination path.
    """

    d = drs.DRS(file=ncfile)

    # get <time_range> from filename of given ncfile
    f_attrs = drs.DRS().splitFileName(ncfile)
    d.set(time_range=f_attrs['time_range'])

    # try to get <version> from dirname of given ncfile.
    try:
        d_attrs = drs.DRS().splitDirName(Path(ncfile).parent)
    except ValueError:
        d_attrs = {}

    if (verstr):
        d.set(version=verstr)
    elif hasattr(d, 'version'):
        d.set(version=getattr(d, 'version'))
    elif hasattr(d_attrs, 'version'):
        d.set(version=getattr(d_attrs, 'version'))
    else:
        d.set(version=verstr_default)

    return (d.dirName(prefix=prefix, allow_asterisk=False)
            / d.fileName(allow_asterisk=False))


def doRelocateFile(src, dst, overwrite=False):
    """
    Relocate file `src` to the path `dst`.

    If dirname(dst) is not exist yet, mkdir'ed silently.

    If file is already exist as `dst`, raise ``FileExistsError``, unless
    ``overwrite=True``.

    Parameter
    ---------
    s : path-like: source file
    d : path-like: destination file
    overwrite(optional) : logical : overwrite file in destination, or not.

    Return
    ------
    path-like : pathname of relocated file.

    """

    sf = Path(src)
    df = Path(dst)

    if (df.is_file()):
        if overwrite:
            pass
        else:
            raise FileExistsError(f'destination is existing file: {df}')

    print(sf, '->', df)

    df.parent.mkdir(parents=True, exist_ok=True)
    sf.replace(df)

    return df


if (__name__ == '__main__'):

    parser = my_parser()
    a = parser.parse_args()

    if (a.debug):
        print('dbg: arguments:')
        print('  dry_run:', a.dry_run)
        print('  overwrite:', a.overwrite)
        print('  prefix:', a.prefix)
        print('  verstr:', a.verstr)
        print('  files:')
        for f in a.files:
            print(f'    {f}')

    # src/dst pair
    srcdst = {s: relocationPath(s, prefix=a.prefix, verstr=a.verstr)
              for s in a.files}

    for s, d in srcdst.items():
        print(s, '\n->', d)
        if not a.dry_run:
            doRelocateFile(s, d, a.overwrite)
