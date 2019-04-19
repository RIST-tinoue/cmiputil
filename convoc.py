#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Access CMIP6 Controlled Vocabularies.

You should clone CMIP6 CVs from github
"""

import os.path
import json
from pprint import pprint

DEFAULT_CVPATH = "./:./CMIP6_CVs:~/Data/CMIP6/CMIP6_CVs"

def getCVPaths(paths=None):
    """
    Return list of directories for searching CV json files.

    Directories taken from the environment variable `CVPATH`, which is
    a string of paths joined by ':'.

    If `CVPATH` is not set, `convoc.DEFAULT_CVPATH` is used.

    If `paths` given, it is used instead of CVPATH.

    Non-existent directories are omitted silently.

    You have to specify '.' explicitly.

    Note that the order is meaningful.

    Parameters
    ---------
      paths(optional) : str, paths joined by ':'

    Returns
    -------
      List of str

    """

    if (paths is None):
        cvd = os.environ.get('CVPATH',DEFAULT_CVPATH).split(':')
    else:
        cvd = paths.split(':')
    # print(cvd)
    cvd = [os.path.expandvars(d) for d in cvd]
    # print(cvd)
    cvd = [os.path.expanduser(d) for d in cvd]
    # print(cvd)
    cvd = [d for d in cvd if os.path.exists(d)]
    return cvd


def getCV(attr):
    """
    Return CV of given `attr` as a dict.

    `attr` must be valid and it's json file must be in CVPATH.

    Parameters
    ----------
      attr : str

    Returns
    -------
      dict : whole CV key-values
    """

    dirs = getCVPaths()
    file = 'CMIP6_'+attr+'.json'

    fname = None
    for d in dirs:
        f = os.path.join(d,file)
        if (os.path.exists(f)):
            fname = f
            break

    # TODO: should raise some exception if no file found.
    cv = None
    if fname is None:
        cv = None
    else:
        with open(fname, 'r') as f:
            cv = json.load(f)

    return cv


def checkCV(value, attr):
    """
    Check if given `value` is in CV `attr`.

    Parameters
    ----------
      attr : str
      value : str

    Returns
    -------
      logical
    """

    # TODO: should cache json file?
    cv = getCV(attr)
    if cv is None:
        res = False
    else:
        res = value in cv[attr]
    return res





if (__name__ == '__main__'):

    paths = getCVPaths()
    print(type(paths),type(paths[0]),paths[0])

    source_id = getCV('source_id')
    print(len(source_id))


    attr = 'source_id'
    value = 'MIROC-ES2H'

    print(checkCV(value, attr))

    attr = 'experiment_id'
    value = 'piControl'

    print(checkCV(value, attr))
