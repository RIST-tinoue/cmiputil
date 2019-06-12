#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maintain config file for cmiputil package.

Config file format for this package is so called 'INI file', handled
by python standard `configparser module`_, so you can use
`interpolation of values`_.

Default name of config file is ``cmiputil.conf`` (set as
:attr:`conf_name`), and searched in $HOME then current directory (set
as :attr:`conf_dir`). If `file` is specified to the constructor, that
is read and **override** the precedence.

"Common" section, which any module in this package may access, name is
:attr:`common_sect_name` and the key=value pair is
:attr:`common_config`.


You can create sample(default) config file by :mod:`createSampleConf`
program, that collects default configuration of each module by
``getDefaultConf()`` in each module and `Conf.read_dict()`_,
then :meth:`Conf.writeConf` to write the file.

.. _configparser module:
   https://docs.python.org/3/library/configparser.html

.. _interpolation of values:
   https://docs.python.org/3/library/configparser.html#interpolation-of-values

.. _configparser.ConfigParser:
   https://docs.python.org/3/library/configparser.html#configparser-objects

.. _Conf.read_dict():
   https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read_dict

"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190612'
__date__ = '2019/06/12'

import configparser
from pathlib import Path
# from pprint import pprint

#: directory list of the config file, order is important since the latter
#: override the former.
conf_dir = ['~/', './', ]

#: name of the config file
conf_name = 'cmiputil.conf'

#: name of the 'common' section
common_sect_name = 'cmiputil'

#: configuration of 'common' section.
common_config = {'cmip6_data_dir': '/data'}


class Conf(configparser.ConfigParser):
    """
    Config parser for this package.

    See `configparser.ConfigParser`_ for other methods and details.

    Args:
        file (str or path-like): config file

    Note:
        If `file` is ``None``, no config file is read and *blank*
        instance is created.  If you want only default config files,
        set ``file=""``.

    Attributes:
        files (list of Path): config files read in.
        commonSection (SectionProxy): "Common" section for this package.
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

    def __init__(self, file=""):
        super().__init__()
        if file is None:
            self.files = ""
        else:
            self.files = [Path(d).expanduser()/Path(conf_name)
                          for d in conf_dir]
            if file:
                self.files.append(file)
        res = self.read(self.files)
        if (self._debug):
            print(f"dbg:read config file(s):{res}")

        self.setCommonSection()


    def setCommonSection(self):
        """
        Set "Common" section.
        """
        self[common_sect_name] = common_config
        self.commonSection = self[common_sect_name]

    def writeConf(self, fname, overwrite=False):
        """
        Write current attributes to the `fname`.

        You have to set configurations for each module via, for example,
        `Conf.read_dict()`_.

        Args:
            fname (str or path-like): file to be written
            overwrite (bool): force overwrite

        Examples:

            >>> from cmiputil import esgfsearch
            >>> conf = Conf(None)
            >>> conf.setCommonSection()
            >>> d = esgfsearch.getDefaultConf()
            >>> conf.read_dict(d)
            >>> conf.writeConf('/tmp/cmiputil.conf', overwrite=True)

        """
        if ((not Path(fname).is_file()) or overwrite):
            with open(fname, 'w') as f:
                self.write(f)
        else:
            raise FileExistsError(f'file already exists: "{fname}"')

    def __str__(self):
        res = ''
        for sec in self.sections():
            res += f'[{sec}]\n'
            for op in self.options(sec):
                res += f'{op} = {self[sec][op]}\n'
            res += '\n'
        return res


if __name__ == '__main__':

    import doctest
    doctest.testmod()
