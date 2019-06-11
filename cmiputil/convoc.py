#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Access CMIP6 Controlled Vocabularies(CVs).

Controlled Vocabularies
~~~~~~~~~~~~~~~~~~~~~~~
A CV, in simplest form, is a list of the permitted values that can be
assigned to a given global attribute, such as <activity_id>,
<experiment_id>, etc.

For some attributes, such as <source_id>, its value is a key-value
pair, whose value is again dict of key-value.

CVs search path
~~~~~~~~~~~~~~~

CVs are maintained as json files. You should clone them from github.

Search path for CVs is set in the order below:

1) `paths` given to the constructor or :meth:`ConVoc.setSearchPath`
2) ``CMIP6_CVs_dir`` in section ``[ConVoc]`` in config file.
3) current directory

Non-existent directories are omitted silently.  You have to
specify ``'.'`` explicitly if necessary.  Note that the order is
meaningful.

"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190611'
__date__ = '2019/06/11'

from cmiputil import config
from pathlib import Path
from os.path import expandvars    # hey, pathlib doesn't have expandvars !?
import json


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


#: path to be written to the sample config file, via :func:`getDefaultConf`
DEFAULT_CVPATH = "./:./CMIP6_CVs:~/CMIP6_CVs:/data/CMIP6_CVs"


def getDefaultConf():
    """
    Return default values for config file.

    Intended to be called before :meth:`config.writeConf`

    Example:
       >>> conf = config.Conf(None)
       >>> conf.setDefaultSection()
       >>> conf.read_dict(getDefaultConf())
       >>> conf.writeSampleConf('/tmp/cmiputil.conf', overwrite=True)
    """
    res = {}
    res['ConVoc'] = {'cmip6_cvs_dir': DEFAULT_CVPATH}
    return res


class ConVoc:
    """
    Class for accessing CMIP6 Controlled Vocabularies.

    This class reads CV from corresponding json file on demand and
    keep as a member.

    See :meth:`setSearchPath()` for the argument `path`.

    Attributes:
        conf : '[ConVoc]' section of conffile
        cvpath  : list of CV files search path.

    Args:
        conf (path-like): config file
        paths (str): a colon separated string

    Examples:
        >>> cvs = ConVoc()
        >>> activity = cvs.getAttrib('activity_id')
        >>> activity['CFMIP']
        'Cloud Feedback Model Intercomparison Project'
        >>> cvs.getValue('CFMIP', 'activity_id')
        'Cloud Feedback Model Intercomparison Project'

        >>> cvs.isValidValueForAttr('MIROC-ES2H', 'source_id')
        True
        >>> cvs.isValidValueForAttr('MIROC-ES2M', 'source_id')
        False

        In the below example, instance member attribute `experiment_id` is
        set AFTER :meth:`isValidValueForAttr()`.

        >>> hasattr(cvs, 'experiment_id')
        False
        >>> cvs.isValidValueForAttr('historical', 'experiment_id')
        True
        >>> hasattr(cvs, 'experiment_id')
        True

        In the below,  example, `table_id` has only keys with no value,
        :meth:`getValue()` return nothing (not ``None``).

        >>> cvs.isValidValueForAttr('Amon', 'table_id')
        True
        >>> cvs.getValue('Amon', 'table_id')

        Invalid attribute raises InvalidCVAttribError.

        >>> cvs.getAttrib('invalid_attr')
        Traceback (most recent call last):
          ...
        InvalidCVAttribError: Invalid attribute as a CV: invalid_attr

        Invalid key for valid attribute raises KeyError.

        >>> cvs.getValue('CCMIP', 'activity_id')
        Traceback (most recent call last):
          ...
        KeyError: 'CCMIP'
    """
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
        'table_id')
    """
    Attributes managed by this class. Note that this is the CLASS
    attribute, not an instance attribute.
    """

    _debug = False

    @classmethod
    def _enable_debug(cls):
        cls._debug = True

    @classmethod
    def _disable_debug(cls):
        cls._debug = True

    # @property
    # def debug(cls):
    #     return cls._debug

    def __init__(self, conffile='', paths=''):
        """
        """
        conf = config.Conf(conffile)
        self.conf = conf['ConVoc']
        self.setSearchPath(paths)

        if self._debug:
            print(f'dbg:ConVoc:cvpath:{self.cvpath}')

    def setSearchPath(self, paths=''):
        """
        Set search path for CV json files.

        `paths` must be a colon separated string of serach path.

        Args:
            paths (str): a colon separated string

        Raises:
            InvalidCVPathError: Unless valid path is set.

        Returns:
            nothing
        """
        if not paths:
            try:
                paths = self.conf['cmip6_cvs_dir']
            except KeyError:
                pass

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

        Returns:
            list of path-like: search path.

        """
        return self.cvpath

    def setAttrib(self, attr):
        """
        Read CV json file for `attr` and set members of self.

        If `attr` is already read and set, do nothing.

        Args:
            attr(str): attribute to be read and set,
                       must be in :attr:`managedAttribs`
        Raises:
            InvalidCVAttribError: if `attr` is invalid.
            InvalidCVPathError: if a valid CV file not found.
        Returns:
            nothing.
        """

        if (attr not in self.managedAttribs):
            raise InvalidCVAttribError("Invalid attribute as a CV: "+attr)

        if (hasattr(self, attr)):
            # print('dbg:setAttrib:attr already set:',attr)
            return

        file = 'CMIP6_'+attr+'.json'

        for p in self.cvpath:
            f = p / file
            if (f.is_file()):
                fpath = f
                break
        else:
            raise InvalidCVPathError(
                'Valid CVs file not found, check CVPATH.')

        with open(fpath, 'r') as f:
            setattr(self, attr, json.load(f))

    def getAttrib(self, attr):
        """
        Return values of given `attr`.

        `attr` must be valid and it's json file must be in CV search
        path.

        Args:
            attr(str): attribute to get.
                       must be in :attr:`managedAttribs`
        Raises:
            InvalidCVAttribError: if `attr` is invalid
        Returns:
            str or dict or "": CV values for `attr`
        """

        self.setAttrib(attr)
        return getattr(self, attr)[attr]

    def isValidValueForAttr(self, key, attr):
        """
        Check if given `key` is in CV `attr`.

        Args:
            key(str): to be checked
            attr(str): attribute, must be in :attr:`managedAttribs`
        Raises:
            InvalidCVAttribError: if `attr` is invalid
            KeyError: if `key` is invalid for `attr`
        Returns:
            bool
        """
        cv = self.getAttrib(attr)
        return key in cv

    def getValue(self, key, attr):
        """
        Return current value of `key` of attribute `attr`.

        Args:
            key(str): key to be get it's value.
            attr(str): attribute, must be in :attr:`managedAttribs`
        Raises:
            InvalidCVAttribError: if `attr` is invalid
            KeyError: if `key` is invalid for `attr`
        Return:
            object: value of `key`, or ``None`` if `key` has no value.

        """
        try:
            res = self.getAttrib(attr)[key]
        except TypeError:   # This attribute has only keys.
            res = None
        return res


if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
