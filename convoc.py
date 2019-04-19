#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Access CMIP6 Controlled Vocabularies.


"""

import os.path

DEFAULT_CV_DIR = "./:./CMIP6_CVs:~/Data/CMIP6/CMIP6_CVs"

def getCVDir():
    """
    Return list of directories for searching CV json files.

    Directories taken from the environment variable `CV_DIR`, which is
    a colon separated strings.

    Non-existent directories are omitted silently.

    You have to specify '.' explicitly.

    Parameters
    ---------
      None

    Returns
    -------
      List of strings

    """
    
    cvd = os.environ.get('CV_DIR',DEFAULT_CV_DIR).split(':')
    # print(cvd)
    cvd = [os.path.expandvars(d) for d in cvd]
    # print(cvd)
    cvd = [os.path.expanduser(d) for d in cvd]
    # print(cvd)
    cvd = [d for d in cvd if os.path.exists(d)]
    return cvd


def openCVFile(attr):
    dirs = getCVDir()
    file = 'CMIP6_'+attr+'.json'

    fname = None
    for d in dirs:
        f = os.path.join(d,file)
        if (os.path.exists(f)):
            fname = f
            break

    if (fname):
        fd = open(fname, 'r')
    else:
        fd = None

    return fd


if (__name__ == '__main__'):

    paths = getCVDir()
    print(paths)
    
    fd = openCVFile('source_id')
    print(fd)

