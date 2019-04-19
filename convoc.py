#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Access CMIP6 Controlled Vocabularies.

You should clone CMIP6 CVs from github
"""

import os.path
import json
from pprint import pprint


class ConVoc:
    """
    Class for accessing CMIP6 Controlled Vocabularies
    """

    DEFAULT_CVPATH = "./:./CMIP6_CVs:~/Data/CMIP6/CMIP6_CVs"

    def __init__(self, paths=None):
        """
        Initialize self.

        See setCVPaths() for arguments.
        """

        self.setCVPaths(paths)
        pass

    def setCVPaths(self, paths=None):
        """
        Set search path for CV json files.

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
            p = os.environ.get('CVPATH',self.DEFAULT_CVPATH).split(':')
        else:
            p = paths.split(':')

        p = [os.path.expandvars(d) for d in p]
        p = [os.path.expanduser(d) for d in p]
        p = [d for d in p if os.path.exists(d)]

        self.cvpath = p


    def getCVPaths(self):
        """
        Return search paths for CV.
        """
        return self.cvpath


    def getCV(self, attr):
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

        if (attr in dir(self)):  # already read
            cv = getattr(self,attr)
            return cv[attr]

        file = 'CMIP6_'+attr+'.json'

        fname = None
        for d in self.cvpath:
            f = os.path.join(d,file)
            if (os.path.exists(f)):
                fname = f
                break

        # TODO: should raise some exception if no file found.
        cv = None
        if fname is not None:
            with open(fname, 'r') as f:
                cv = json.load(f)
            setattr(self, attr, cv)
            return cv[attr]
        else:
            return None


    def checkCV(self, value, attr):
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
        cv = self.getCV(attr)
        if cv is None:
            res = False
        else:
            res = value in cv
        return res


if (__name__ == '__main__'):

    cvs = ConVoc()

    print(cvs.getCVPaths())

    source_id = cvs.getCV('source_id')
    print('len(source_id):',len(source_id))

    # 'source_id' has set above
    attr = 'source_id'
    value = 'MIROC-ES2H'
    print(value,attr,cvs.checkCV(value, attr))

    # 'experiment_id' has not set yet
    attr = 'experiment_id'
    value = 'piControl'
    print(value, attr, cvs.checkCV(value, attr))
    print(dir(cvs))  # see there is cvs.experiment_id
    
