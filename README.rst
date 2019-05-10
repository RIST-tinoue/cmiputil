`cmiputil`
==========

A small package for CMIP6/ESGF data users.



What is this ?
--------------

This is a collection of small python modules for CMIP6/ESGF data users.

These modules has been developed to support researchers who use
CMIP6 data via ESGF, under the ongoing project called `TOUGOU Program 
<http://www.jamstec.go.jp/tougou/eng>`__.

Currently there are a few modules listed below:

-  `esgfsearch`: Search and access datasets using ESGF RESTful API and
   THREDDS.
-  `drs`: Handle DRS-complient directory name and file name.
-  `convoc`: Handle CMIP6 CVs.


You may want
------------

If you want to search and *download* datasets, you should use `synda
<https://github.com/Prodiguer/synda>`__, which is highly comprehensive
useful and reliable.

Requirement
-----------

This package has been developed under this environment only:

- python 3.6.8
- siphon 0.8.0
- xarray 0.11.3
- netCDF4 1.3.1
- urllib3 1.24.1

For creating documents:

- sphinx 2.0.1
- sphinx-rtd-theme 0.4.3


Install
-------

You can get from https://github.com/RIST-tinoue/cmiputil

::

    $ git clone https://github.com/RIST-tinoue/cmiputil
    $ cd cmiputil
    $ python ./setup.py develop   # <- strongly recommended for a while.

Usage
-----

::

    $ python3
    >>> from cmiputil import esgfsearch
    >>> help(esgfsearch)
    >>> from cmiputil import drs
    >>> help(drs)
    >>> from cmiputil import convoc
    >>> help(convoc)

See also each source files, tests, and sample apprications.

Document
--------

See `HTML
Documentation <https://rist-tinoue.github.io/cmiputil/index.html>`__.

Author
------

Takahiro Inoue

Copyright |copy| 2019, RIST

.. |copy| unicode:: 0xA9 .. copyright sign

Licence
-------

`BSD 3-Clause
License <https://github.com/RIST-tinoue/cmiputil/blob/master/LICENSE>`__
