#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Access CMIP6 Controlled Vocabularies(CVs).

A CV, in simplest form, is a list of the permitted values that can be
assigned to a given global attribute, such as <activity_id>,
<experiment_id>, etc.

For some attributes, such as <source_id>, its value is a key-value
pair, whose value is again dict of key-value.

CVs are maintained as json files. You should clone them from github,
and set a environment variable `CVPATH`, which is a colon separated
string.
"""

# import os.path
from pathlib import Path
from os.path import expandvars    ## hey, pathlib doesn't have expandvars !?
import json
from os import environ
from pprint import pprint


class ControlledVocabulariesError(Exception):
    "Base exception class for convoc."
    pass


class InvalidCVAttribError(ControlledVocabulariesError):
    "Error for invalid attribute as a Controlled Vocabulary"
    pass


class InvalidCVKeyError(ControlledVocabulariesError):
    "Error for invalid key as a Controlled Vocabulary for valid attribute."
    pass


class InvalidCVPathError(ControlledVocabulariesError):
    "Error for invalid path as a Controlled Vocabulary"
    pass


class ConVoc:
    """
    Class for accessing CMIP6 Controlled Vocabularies.
    """

    DEFAULT_CVPATH = "./:./CMIP6_CVs:~/CMIP6_CVs"
    managedAttribs = (
        'activity_id',
        'experiment_id',
        'frequency',
        'grid_label',
        'institution_id',
        'license',
        'nominal_resolution',
        'realm',
        'required_global_attributes',
        'source_id',
        'source_type',
        'sub_experiment_id',
        'table_id',
    )

    def __init__(self, paths=None):
        """
        Initialize self.

        See setSearchPath() for arguments.
        """

        self.setSearchPath(paths)
        pass

    def setSearchPath(self, paths=None):
        """
        Set search path for CV json files.

        Directories taken from the environment variable `CVPATH`, which is
        a colon separated string.

        If `CVPATH` is not set, `ConVoc.DEFAULT_CVPATH` is used.

        If `paths` given, it is used instead of CVPATH.

        Non-existent directories are omitted silently.

        You have to specify '.' explicitly if necessary.

        Unless valid path is set, InvalidCVPathError is raised.

        Note that the order is meaningful.

        Parameters
        ---------
          paths(optional) : str, paths joined by ':'

        Returns
        -------
          nothing.

        """

        if (paths is None):
            paths = environ.get('CVPATH', self.DEFAULT_CVPATH)

        p = [Path(expandvars(d)) for d in paths.split(':')]

        p = [d.expanduser() for d in p]
        p = [d for d in p if d.is_dir()]

        if (p):
            self.cvpath = p
        else:
            raise InvalidCVPathError('No valid CVPATH set.')

    def getSearchPath(self):
        """
        Return search paths for CV.

        Returns
        -------
        list of Path():
        """
        return self.cvpath

    def setAttr(self, attr):
        """
        Read CV json file for `attr` and set members of self.

        If attr is already read and set, do nothing.

        If attr is not valid, InvalidCVAttribError is raised.
        If valid CVs file not found, InvalidCVPathError is raised.

        Parameters
        ----------
          attr : str

        Returns
        -------
          nothing
        """

        if (attr not in self.managedAttribs):
            raise InvalidCVAttribError("Invalid attribute as a CV: "+attr)

        if (attr in dir(self)):
            # print('dbg:setAttr:attr already set:',attr)
            return

        file = 'CMIP6_'+attr+'.json'

        fpath = None
        for p in self.cvpath:
            f = p / file
            if (f.is_file()):
                fpath = f
                break

        if fpath is None:
            raise InvalidCVPathError(
                'Valid CVs file not found, check CVPATH.')

        with open(fpath, 'r') as f:
            setattr(self, attr, json.load(f))

    def getAttr(self, attr):
        """
        Return values of given `attr` as a dict.

        `attr` must be valid and it's json file must be in CVPATH.

        See setAttr() for exception.

        Parameters
        ----------
          attr : str

        Returns
        -------
          dict : whole CV key-values
        """

        self.setAttr(attr)
        return getattr(self, attr)[attr]

    def isValidValueForAttr(self, key, attr):
        """
        Check if given `key` is in CV `attr`.

        `attr` must be in DRS.requiredAttribs.

        Parameters
        ----------
          attr : str
          key : str

        Returns
        -------
          logical
        """

        cv = self.getAttr(attr)
        return key in cv

    def getValue(self, key, attr):
        """
        Return current value of `key` of attribute `attr`.

        If `key` has no value, return None.

        If `attr` is invalid, InvalidCVAttribError is raised
        if `key` is invalid for `attr`, KeyError is raised

        Parameters
        ----------
          attr : str
          key : str

        Returns
        -------
          object or None

        """

        try:
            res = self.getAttr(attr)[key]
        except TypeError:   # This attribute has only keys.
            res = None
        return res


if (__name__ == '__main__'):

    cvs = ConVoc()

    print(cvs.getSearchPath())

    source_id = cvs.getAttr('source_id')
    print('len(source_id):', len(source_id))

    # 'source_id' has set above
    attr = 'source_id'
    key = 'MIROC-ES2H'
    print(key, attr, cvs.isValidValueForAttr(key, attr))

    # 'experiment_id' has not set yet
    attr = 'experiment_id'
    key = 'historical'
    print(key, attr, cvs.isValidValueForAttr(key, attr))
    print(getattr(cvs, attr) is not None)  # see there is cvs.experiment_id

    pprint(cvs.getValue(key, attr))

    # activity_id
    attr = 'activity_id'
    key = 'CMIP'
    print(key, attr, cvs.isValidValueForAttr(key, attr))
    print(getattr(cvs, attr) is not None)  # see there is cvs.experiment_id

    pprint(cvs.getValue(key, attr))

    attr = 'hoge_id'  # will raise exception
    try:
        cv = cvs.getAttr(attr)
    except InvalidCVAttribError as e:
        print("Excepted Error raised:", e)

    # table_id has only keys, no value.
    attr = 'table_id'
    key = 'Amon'
    cv = cvs.getAttr(attr)
    print(key, attr, cvs.isValidValueForAttr(key, attr))
    print(cvs.getValue(key, attr))  # should be None

    attr = 'realm'
    key = 'atmos'

    print(key, attr, cvs.isValidValueForAttr(key, attr))
    print(key, attr, cvs.getValue(key, attr))
