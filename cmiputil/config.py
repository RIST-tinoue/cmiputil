#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maintain config file for cmiputil package.

Config file for this package is so called 'INI file', handled by
python standard `configparser` module.

Default name of config file is ``cmiputil.conf``, and searched in
$HOME then current directory. If `file` is specified to the
constructor, that is read and override the precedence.

"Default" section name is :attr:`conf_section` and the key=value pair
is :attr:`conf_default`.


You can create sample(default) conf file by :mod:`createSampleConf`,
collect default configuration of each module by ``getDefaultConf()``
in each module and :meth:`read_dict`, then :meth:`writeConf` to write
the file.


"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190606'
__date__ = '2019/06/06'

import configparser
from pathlib import Path
# from pprint import pprint

#: directory list of the conffile, order is important.
conf_dir = ['~/', './', ]

#: name of the conffile
conf_name = 'cmiputil.conf'

#: name of the 'default' section
conf_section = 'cmiputil'

#: configuration of default section.
conf_default = {'cmip6_data_dir': '/data'}


class Conf(configparser.ConfigParser):
    """
    Args:
        file (str or path-like) or None: config file

    If `file` is ``None``, no conf file is read and *blank* instance
    is created.  If you want only default conf files, set ``file=""``.
    """
    _debug = False

    @classmethod
    def _enable_debug(cls):
        cls._debug = True

    @classmethod
    def _disable_debug(cls):
        cls._debug = True

    @property
    def debug(cls):
        return cls._debug

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
            print(f"dbg:read conf file(s):{res}")

    def setDefaultSection(self):
        """
        Set "default" section.
        """
        self[conf_section] = conf_default

    def writeConf(self, fname, overwrite=False):
        """
        Write current attributes to the `fname`.

        You have to set configurations for each module via, for example,
        :meth:`self.read_dict`.

        Args:
            fname (str or path-like): file to be written
            overwrite (bool): force overwrite

        Examples:

            >>> from cmiputil import esgfsearch
            >>> conf = Conf('')
            >>> conf.setDefaultSection()
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
