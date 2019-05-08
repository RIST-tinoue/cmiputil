cmiputil
========

This is a small package for CMIP6/ESGF data users, especially for myself.

## What is this ?
This is a collection of small python modules for CMIP6/ESGF data users.

Currently there are a few modules listed below:

- esgfsearch: Search and download datafile using ESGF RESTful API and THREDDS.
- drs: Handle DRS-complient directory name and file name.
- convoc: Handle CMIP6 CVs

## Install

    $ git clone git@github.com:RIST-tinoue/cmiputil.git
    $ cd cmiputil
    $ python ./setup.py develop   # <- strongly recommended for a while.

## Usage

    $ python3
    >>> from cmiputil import esgfsearch
    >>> help(esgfsearch)
    >>> from cmiputil import drs
    >>> help(drs)
    >>> from cmiputil import convoc
    >>> help(convoc)

See each source files for example, or see below. 

## Document

See [HTML Documentation](https://rist-tinoue.github.io/cmiputil/index.html).

## Licence

[BSD 3-Clause License](https://github.com/RIST-tinoue/cmiputil/blob/master/LICENSE)

## Author

[T.Inoue @ RIST](https://github.com/RIST-tinoue)
