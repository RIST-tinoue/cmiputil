#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maintain config file for cmiputil package.

Config file for this package is so called 'INI file', handled by
python standard `configparser` module.

Default name of config file is ``cmiputil.conf``, and searched in
$HOME then current directory, unless specified by the argument of
:meth:`readConfFile`.

By calling :meth:`writeSampleConf` you can create a sample config file.
You have to call ``putConf()`` in each module in this package beforehand.

TODO:
    - System wide config file ?
    - Inherit configparser class

"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190529'
__date__ = '2019/05/29'


import configparser
import os.path
from pathlib import Path
from pprint import pprint

#: name of the conffile
conf_name = 'cmiputil.conf'

#: directory list of the conffile, current, $HOME
conf_dir = [os.path.expanduser('~/'), './']

#: configuration of default section.
conf_default = {'cmip6_data_dir': '/data'}


class Conf(configparser.ConfigParser):
    def __init__(self, file=None):
        super().__init__()
        if file is None:
            self.files = [Path(d)/Path(conf_name) for d in conf_dir]
        else:
            self.files = file
        self.read(self.files)

    def setDefaultSection(self):
        self['DEFAULT'] = conf_default

    def writeSampleConf(self, fname, overwrite=False):
        """
        Write sample config file to `fname`.

        You have to set configurations for each module via
        :meth:`self.read_dict`

        Args:
            fname (str or path-like): file to be written
            overwrite (bool): force overwrite

        Examples:

            >>> from cmiputil import esgfsearch
            >>> conf = Conf('')
            >>> conf.setDefaultSection()
            >>> d = esgfsearch.getDefaultConf()
            >>> conf.read_dict(d)
            >>> conf.writeSampleConf('/tmp/cmiputil.conf', overwrite=True)
        """
        if ((not Path(fname).is_file()) or overwrite):
            with open(fname, 'w') as f:
                self.write(f)
        else:
            raise FileExistsError(f'file already exists: "{fname}"')


if __name__ == '__main__':

    import doctest
    doctest.testmod()
