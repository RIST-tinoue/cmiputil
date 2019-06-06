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


By calling :meth:`writeSampleConf` you can create a sample config file.
You have to call ``putConf()`` in each module in this package beforehand.

"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190606'
__date__ = '2019/06/06'

_debug = False

import configparser
import os.path
from pathlib import Path
from pprint import pprint

#: directory list of the conffile, order is important.
conf_dir = [ '~/','./',]

#: name of the conffile
conf_name = 'cmiputil.conf'

#: name of the 'default' section
conf_section = 'cmiputil'

#: configuration of default section.
conf_default = {'cmip6_data_dir': '/data'}


class Conf(configparser.ConfigParser):
    def __init__(self, file=None):
        global _debug
        super().__init__()
        self.files = [Path(d).expanduser()/Path(conf_name) for d in conf_dir]
        if file :
            self.files.append(file)
        res = self.read(self.files)
        if (_debug):
            print(f"dbg:read conf file(s):{res}")


    def setDefaultSection(self):
        self[conf_section] = conf_default

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
