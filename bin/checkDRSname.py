#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check file/directory name is valid as DRS.
"""

from cmiputil import drs
import argparse
import sys

__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190525'
__date__ = '2019/05/25'

desc = __doc__+"""
If (one of) given file(s) is(are) invalid, exit with code 1.
If verbose (-v), the reason is also shown.
"""

epilog="""
"""

def my_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        epilog=epilog)
    parser.add_argument(
        'files', nargs='+', type=str, metavar='nc_file')
    parser.add_argument(
        '-v', '--verbose', action="store_true", default=False)
    parser.add_argument(
        '-q', '--quiet', action="store_true", default=False)
    return parser


def isValidFileAsDRS(f, verbose=True):

    try:
        d = drs.DRS(filename=f, do_sanitize=False)
    except ValueError as e:
        reason = '  '+e.args[0]
        return False, reason

    f_res, d_res = d.isValidPath(f, separated=True)
    res = all(f_res.values())
    if res:
        reason = ''
    else:
        mess = [f'  <{a}> is invalid: "{getattr(d, a)}"' for a, v in f_res.items() if not v]
        reason = '\n'.join(mess)

    return res, reason


if __name__ == '__main__':

    parser = my_parser()
    args = parser.parse_args()

    count = 0
    for f in args.files:
        res, reason = isValidFileAsDRS(f, args.verbose)
        if res:
            if not args.quiet:
                print(f'{f} is valid.')
        else:
            if not args.quiet:
                print(f'{f} is invalid.')
                if args.verbose:
                    print(reason)
            count +=1

    if (count > 0):
        sys.exit(1)
