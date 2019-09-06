#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maintain config file for cmiputil package.

Config file format for this package is so called 'INI file', handled
by python standard `configparser module`_, so you can use
`interpolation of values`_.

Default name of config file is ``cmiputil.conf`` (set as
:attr:`conf_name`), and is searched in the order below:

1. specified by the argument of :class:`Conf()`
2. specified by the environment variable `CMIPUTIL_CONFFILE`
3. ``$CMIPUTIL_CONFDIR/cmiputil.conf``
4. ``$cwd/cmiputil.conf``
5. ``$HOME/cmiputil.conf``

Once found, the rest is skipped.

If `file` given to the :class:`Conf()` is ``None``, no config file is
read and *blank* instance is created.  If you want to read the default
config file only, leave ``file=""`` as a default.

The name of "Common" section, which any module in this package may
access, is :attr:`common_sect_name` and the key=value pair is
:attr:`common_config`.

You can create sample(default) config file by :mod:`createSampleConf`
program, that collects default configuration of each module by
``getDefaultConf()`` method defined in each module(class) in this
package, and write them to the file by `Conf.read_dict()`_ and
:meth:`Conf.writeConf`.

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
__version__ = 'v20190905'
__date__ = '2019/09/05'

import os
import configparser
from pathlib import Path
# from pprint import pprint

conf_dir = ['~/', './', ]
"""Directory list for searching a config file.

Overriden by an environment variable `CMIPUTIL_CONFDIR` if set.
The order is important since the latter searched first.
"""
if os.getenv('CMIPUTIL_CONFDIR'):
    conf_dir = os.getenv('CMIPUTIL_CONFDIR').split(':')

#: Name of the config file.
conf_name = 'cmiputil.conf'

#: Name of the 'common' section.
common_sect_name = 'cmiputil'

#: Default configuration of the 'common' section.
common_config = {'cmip6_data_dir': '/data'}


class Conf(configparser.ConfigParser):
    """
    Config parser for this package.

    If `file` is given, this must be a string or a path-like object,
    specifying config file to be read first (See above).

    See `configparser.ConfigParser`_ for other methods and details.

    Attributes:
        file (Path): config file had read in.
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
        self.file = file
        if file is None:
            files = ""
            self.read(files)
            if (self._debug):
                print("dbg:no config file read")
        else:
            files = [Path(d).expanduser()/Path(conf_name)
                     for d in conf_dir]
            if os.getenv('CMIPUTIL_CONFFILE'):
                files.append(Path(os.getenv('CMIPUTIL_CONFFILE')))
            if file:
                files.append(Path(file))

            for f in files[::-1]:
                try:
                    fp = open(f)
                except FileNotFoundError:
                    continue

                self.read_file(fp)
                self.file = f
                fp.close()
                break

        if (self._debug):
            print(f"dbg:read config file: {self.file}")

        if self.has_section(common_sect_name):
            self.commonSection = self[common_sect_name]

    def setCommonSection(self):
        """
        Set default "common" section.

        Warning:
            Do not call this after reading real config file.
        """
        self[common_sect_name] = common_config

    def writeConf(self, file, overwrite=False):
        """
        Write current attributes to the `file`, this must be a string
        or a path-like.

        If given `file` exists, :exc:`FileExistsError` is raised
        unless `overwrite` is ``True``.

        Do not forget to call :meth:`.setCommonSection()` to include
        common section to write.

        Examples:

            >>> from cmiputil import config, esgfsearch
            >>> conf = config.Conf(None)
            >>> conf.setCommonSection()
            >>> d = esgfsearch.getDefaultConf()
            >>> conf.read_dict(d)
            >>> conf.writeConf('/tmp/cmiputil.conf', overwrite=True)

            After above example, ``/tmp/cmiputil.conf`` is as below::

                [cmiputil]
                cmip6_data_dir = /data

                [ESGFSearch]
                search_service = http://esgf-node.llnl.gov/esg-search/
                aggregate = True

                [ESGFSearch.keywords]
                replica = false
                latest = true

                [ESGFSearch.facets]
                table_id = Amon

        """
        if ((not Path(file).is_file()) or overwrite):
            with open(file, 'w') as f:
                self.write(f)
        else:
            raise FileExistsError(f'file already exists: "{file}"')

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
