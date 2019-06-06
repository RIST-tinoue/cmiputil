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
epilog = ""


def my_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=epilog)
    parser.add_argument(
        'file', type=str, nargs='?', metavar='conf_file',
        default='cmiputil.conf')
    parser.add_argument(
        '-O', '--overwrite', action='store_true', default=False)
    return parser


def main():
    a = my_parser().parse_args()

    conf = cmiputil.config.Conf('')
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

    conf.writeSampleConf(a.file, overwrite=a.overwrite)
    print(f'config file "{a.file}" created successfully')


if __name__ == '__main__':
    main()
