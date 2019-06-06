#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create config file for cmiputil.
"""

import cmiputil
import argparse

__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190530'
__date__ = '2019/05/30'


desc = __doc__
epilog = """
Note that the default search path for config file is current directory
and $HOME in this order, with filename 'cmiputil.conf'.
"""


def my_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=epilog)
    parser.add_argument(
        'file', type=str, nargs='?', metavar='conf_file',
        default='cmiputil.conf')
    parser.add_argument(
        '-o', '--overwrite', action='store_true', default=False)

    return parser


if __name__ == '__main__':

    parser = my_parser()
    args = parser.parse_args()

    conf = cmiputil.config.Conf(None)
    conf.setDefaultSection()

    try:
        d = cmiputil.esgfsearch.getDefaultConf()
    except AttributeError:
        pass
    else:
        conf.read_dict(d)

    try:
        d = cmiputil.drs.getDefaultConf()
    except AttributeError:
        pass
    else:
        conf.read_dict(d)

    try:
        d = cmiputil.convoc.getDefaultConf()
    except AttributeError:
        pass
    else:
        conf.read_dict(d)

    try:
        conf.writeConf(args.file, overwrite=args.overwrite)
    except Exception:
        raise
    else:
        print(f'config file "{args.file}" created successfully')
