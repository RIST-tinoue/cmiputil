#!/usr/bin/env python3
# coding:utf-8

"""CMIP6 Data Reference Syntax (DRS).

(Excerpt from http://goo.gl/v1drZl)

File name template:
-------------------

DRS compilent filename consists of several global attributes as
follows::

    filename = <variable_id>
                _<table_id>
                  _<source_id>
                    _<experiment_id >
                      _<member_id>
                        _<grid_label>
                          [_<time_range>].nc

For time-invariant fields, the last segment (<time_range>) above is
omitted.

All strings appearing in the file name are constructed using only the
following characters: a-z, A-Z, 0-9, and the hyphen ("-"), except the
hyphen must not appear in <variable_id>.  Underscores are prohibited
throughout except as shown in the template.

The <member_id> is constructed from the <sub_experiment_id> and
<variant_label> using the following algorithm:

|    if <sub_experiment_id> == “none”
|        <member_id> = <variant_label>
|    else
|        <member_id> = <sub_experiment_id>-<variant_label>
|    endif

The <time_range> is a string generated consistent with the following:

|    if frequency == “fx” then
|        <time_range>=””
|    else
|        <time_range> = N1-N2
|        where N1 and N2 are integers of the form
|        ‘yyyy[MM[dd[hh[mm[ss]]]]][<suffix>]’ (expressed as a string,where
|        where ‘yyyy’, ‘MM’, ‘dd’, ‘hh’ ‘mm’ and ‘ss’ are integer year,
|        month, day, hour, minute, and second, respectively)
|    endif

where <suffix> is defined as follows:

| if the variable identified by variable_id has a time dimension with
| a “climatology” attribute then
|         <suffix> = “-clim”
|    else
|         <suffix> = “”
|    endif

and where the precision of the time_range strings is determined by the
<frequency> global attribute.

Example when there is no <sub_experiment_id>::

    tas_Amon_GFDL-CM4_historical_r1i1p1f1_gn_196001-199912.nc

Example with a <sub_experiment_id>::

    pr_day_CNRM-CM6-1_dcppA-hindcast_s1960-r2i1p1f1_gn_198001-198412.nc



Directory structure template:
-----------------------------

DRS complient directory structure consists of several global
attributes as follows::

    Directory structure = <mip_era>/
                            <activity_id>/
                              <institution_id>/
                                <source_id>/
                                  <experiment_id>/
                                    <member_id>/
                                      <table_id>/
                                        <variable_id>/
                                          <grid_label>/
                                            <version>


Note:

- <version> has the form “vYYYYMMDD” (e.g., “v20160314”), indicating a
  representative date for the version.  Note that files contained in a
  single <version> subdirectory at the end of the directory path
  should represent all the available time-samples reported from the
  simulation; a time-series can be split across several files, but all
  the files must be found in the same subdirectory.  This implies that
  <version> will not generally be the actual date that all files in
  the subdirectory were written or published.
- If multiple activities are listed in the global attribute, the first
  one is used in the directory structure.


Example when there is no <sub-experiment_id>::

     CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/1pctCO2/r1i1p1f1/Amon/tas/gn/v20150322

Example with a <sub_experiment_id>::

     CMIP6/DCPP/CNRM-CERFACS/CNRM-CM6-1/dcppA-hindcast/s1960-r2i1p1f3/day/pr/gn/v20160215

"""
__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190509'
__date__ = '2019/05/09'

from cmiputil.convoc import ConVoc
import netCDF4 as nc
from pathlib import PurePath
from pprint import pprint


class DRSError(Exception):
    """Base exception class for DRS."""

    pass


class InvalidDRSAttribError(DRSError):
    """Error for invalid attribute as DRS."""


class InvalidPathAsDRSError(DRSError):
    """Error for invalid path as DRS."""


sample_attrs = {
    'activity_id': 'CMIP',
    'experiment_id': 'piControl',
    'grid_label': 'gn',
    'institution_id': 'MIROC',
    'source_id': 'MIROC6',
    'table_id': 'Amon',
    'variable_id': 'tas',
    'variant_label': 'r1i1p1f1',
    'version': 'v20190308',
    'non_necessary_attribute': 'hoge'
}
sample_fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc"
sample_dname = "CMIP6/CMIP/MIROC/MIROC6/piControl/"\
               "r1i1p1f1/Amon/tas/gn/v20190308"

sample_attrs_w_subexp = {
    'activity_id': 'DCPP',
    'experiment_id': 'dcppC-atl-pacemaker',
    'grid_label': 'gr',
    'institution_id': 'IPSL',
    'source_id': 'IPSL-CM6A-LR',
    'sub_experiment_id': 's1950',
    'table_id': 'Amon',
    'time_range': '192001-201412',
    'variable_id': 'rsdscs',
    'variant_label': 'r1i1p1f1',
    'version': 'v20190110'}
sample_fname_w_subexp = 'rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker'\
                        '_s1950-r1i1p1f1_gr_192001-201412.nc'
sample_dname_w_subexp = 'CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/'\
                        's1950-r1i1p1f1/Amon/rsdscs/gr/v20190110'


class DRS:
    """
    Class for CMIP6 DRS.

    This class contains attributes necessary to construct a file
    name/directory name that is valid for CMIP6 DRS (Data Reference
    Syntax).  See above and http://goo.gl/v1drZl for details about DRS
    as well as CMIP6 global attributes, etc.

    Instance member variables of this class are:

    - ``variable_id``
    - ``table_id``
    - ``source_id``
    - ``experiment_id``
    - ``grid_label``
    - ``time_range``
    - ``version``
    - ``sub_experiment_id``
    - ``variant_label``
    - ``member_id``
    - ``mip_era``
    - ``activity_id``
    - ``institution_id``
    - ``source_id``

    Note that ``member_id`` is not able to set directly, this is set by
    ``sub_experiment_id`` (omittable) and ``variant_label``.

    You can use the class member :attr:`requiredAttribs` to know
    necessary attributes to set a filename/dirname valid for DRS.

    Args:
        file(path-like): filename of valid CMIP6 netCDF file.
        filename(str): filename to be used to set attributes.
        kw(dict): attribute-value pairs

    If `file` is given, it must be a valid CMIP6 netCDF file, and
    attributes in that file are read and set.

    Else if `filename` is given, it must be a valid filename as DRS,
    and attributes are set from components consist of that filename.

    Else attributes are set from `**kw` dict.
    """

    requiredAttribs = (
        'activity_id',
        'experiment_id',
        'grid_label',
        'institution_id',
        'mip_era',
        'source_id',
        'sub_experiment_id',
        'table_id',
        'time_range',
        'variable_id',
        'variant_label',
        'version',
        )

    def __init__(self, file=None, filename=None, **kw):
        self.cvs = ConVoc()
        self.mip_era = 'CMIP6'

        if (file):
            with nc.Dataset(file, "r") as ds:
                attrs = {a: getattr(ds, a, None)
                         for a in drs.DRS.requiredAttribs}
            attrs = {a: v for a, v in attrs.items() if v != 'none'}
            self.set(**attrs)
        elif (filename):
            attrs = self.splitFileName(filename)
            self.set(**attrs)
        else:
            self.set(**kw)

    def __repr__(self):
        res = ["{}={!a}".format(k, getattr(self, k))
               for k in DRS.requiredAttribs if hasattr(self, k)]
        res = 'drs.DRS(' + ', '.join(res) + ')'
        return res

    def __str__(self):
        res = ["{}: {!a}".format(k, getattr(self, k))
               for k in DRS.requiredAttribs if hasattr(self, k)]
        res = "\n".join(res)
        return res

    def getAttribs(self):
        """
        Return current instance attributes defined of
        :attr:`requiredAttribs` and their values.

        Returns:
            dict: attribute-value pairs.
        """
        return {k: getattr(self, k)
                for k in DRS.requiredAttribs if hasattr(self, k)}

    def _check_time_range(self, value):
        # TODO: must be 'YYYYMMDD-YYYYMMDD', use regex.
        return value is not None

    def _check_version(self, value):
        # TODO: must be 'vYYYYMMDD', use regex.
        return value is not None

    def _check_variable_id(self, value):
        # TODO: Is there any method to check ?
        return value is not None

    def _check_variant_label(self, value):
        # TODO: must be r{i}i{i}p{i}f{i}, use regex.
        return value is not None

    def isValidValueForAttr(self, value, attr):
        """
        Check `value` is valid for the attribute `attr`.

        Args:
            value (object) : value for `attr`
            attr (object) : global attribute
        Raises:
            InvalidDRSAttribError: raises when `attr` is invalid for DRS.
        Returns:
            bool: whether `value` is valid for the attribute `attr`
        """
        if attr == 'sub_experiment_id':
            # TODO:
            # Currently, value of <sub_experiment_id> used in
            # published datasets is only 's1920', which is not in CVs.
            # So avoid check tentatively
            return (ConVoc().isValidValueForAttr(value, attr)
                    or value == 's1920')
        elif attr in ConVoc().managedAttribs:
            return ConVoc().isValidValueForAttr(value, attr)
        elif attr == 'time_range':
            return self._check_time_range(value)
        elif attr == 'version':
            return self._check_version(value)
        elif attr == 'variable_id':
            return self._check_variable_id(value)
        elif attr == 'variant_label':
            return self._check_variant_label(value)
        elif attr == 'mip_era':
            return (value.lower() == 'cmip6')
        else:
            raise InvalidDRSAttribError('Invalid Attribute for DRS:', attr)

    def set(self, return_self=False, **argv):
        """
        Set instance attributes, if attribute is in :attr:`requiredAttribs`.

        Missing attributes in `argv` are left unset/untouched.
        Attribute with invalid value is also unset/untouched sirently.
        Unnecessary attributes are neglected.

        Each of attributes are checked by
        :meth:`isValidValueForAttr()` before set.

        Args:
            argv (dict): attribute/value pairs
            return_self (bool): return self or nothing.
        Raises:
            InvalidDRSAttribError:  raises when `attr` is invalid for DRS.
        Return:
            nothing or self when `return_self` is ``True``
        """
        attribs = [a for a in argv.keys() if a in DRS.requiredAttribs]
        for a in attribs:
            if (self.isValidValueForAttr(argv[a], a)):
                setattr(self, a, argv[a])

        if (hasattr(self, 'variant_label')):
            if (hasattr(self, 'sub_experiment_id')):
                self.member_id = "{}-{}".format(
                    argv['sub_experiment_id'], argv['variant_label'])
            else:
                self.member_id = self.variant_label
        if (return_self):
            return self

    def fileName(self):
        """
        Construct filename from current instance member attributes.

        Raises:
            AttributeError: any attributes are missing.

        Returns:
            str: filename


        Examples:

        DRS from dict w/o `time_range`

        >>> drs.DRS(**drs.sample_attrs).fileName()
        'tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc'

        DRS from dict w/ `sub_experiment_id`

        >>> drs.DRS(**drs.sample_attrs_w_subexp).fileName()
        'rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker_s1950-r1i1p1f1_gr_192001-201412.nc'

        Invalid value for valid attrib

        >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
        >>> attrs.update({'table_id': 'invalid'})
        >>> d = drs.DRS(**attrs).fileName()
        Traceback (most recent call last):
          ...
        AttributeError: 'DRS' object has no attribute 'table_id'

        In the example above, since the key ``table_id`` has invalid value,
        ``d.table_id`` is NOT set, and so the exception raised.
        """
        var = self.variable_id
        tab = self.table_id
        src = self.source_id
        exp = self.experiment_id
        mem = self.member_id
        grd = self.grid_label
        if (hasattr(self, 'time_range')):
            tim = self.time_range
            f = f"{var}_{tab}_{src}_{exp}_{mem}_{grd}_{tim}.nc"
        else:
            f = f"{var}_{tab}_{src}_{exp}_{mem}_{grd}.nc"
        return f

    def dirName(self, prefix=None):
        """
        Construct directory name by DRS from drs.DRS instance members.

        Args:
            prefix (Path-like): prepend to the result path.

        Raises:
            AttributeError: any attributes are missing.

        Returns:
            Path-like: directory name

        Examples:

        DRS from dict w/o ``time_range``.

        >>> drs.DRS(**drs.sample_attrs).dirName()
        'CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20190308'

        DRS from dict w/ ``sub_experiment_id``.

        >>> drs.DRS(**drs.sample_attrs_w_subexp).dirName() # doctest: +NORMALIZE_WHITESPACE
        'CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/s1950-r1i1p1f1/Amon/rsdscs/gr/v20190110'

        Invalid value for valid attrib.

        >>> attrs = {k:v for k,v in drs.sample_attrs.items()}
        >>> attrs['table_id'] = 'invalid'
        >>> drs.DRS(**attrs).dirName()
        Traceback (most recent call last):
          ...
        AttributeError: 'DRS' object has no attribute 'table_id'

        In the example above, since ``table_id`` has invalid value, `d.table_id`
        has NOT set, and so the exception is raised.

        """
        d = PurePath(
           self.mip_era,
           self.activity_id,
           self.institution_id,
           self.source_id,
           self.experiment_id,
           self.member_id,
           self.table_id,
           self.variable_id,
           self.grid_label,
           self.version)
        if (prefix):
            d = PurePath(prefix) / d
        return str(d)

    def splitFileName(self, fname):
        """
        Split filename to attributes for DRS.

        Set them as members of the instance and also return as a dict.

        Args:
            fname (Path-like): filename

        Raises:
            ValueError: if `fname` is invalid for DRS.

        Returns:
            dict: attribute and it's value

        Examples:
            >>> fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc"
            >>> drs.DRS().splitFileName(fname) # doctest: +NORMALIZE_WHITESPACE
            {'experiment_id': 'piControl', 'grid_label': 'gn',
            'source_id': 'MIROC6', 'table_id': 'Amon', 'time_range':
            '320001-329912', 'variable_id': 'tas', 'variant_label':
            'r1i1p1f1'}
        """
        (variable_id,
         table_id,
         source_id,
         experiment_id,
         member_id,
         grid_label) = PurePath(fname).stem.split('_', 5)

        try:
            (grid_label, time_range) = grid_label.split('_')
        except ValueError:
            # time_range = None
            pass

        try:
            (sub_experiment_id, variant_label) = member_id.split('-')
        except ValueError:
            variant_label = member_id
            # sub_experiment_id = None

        res = {}
        for k in DRS.requiredAttribs:
            try:
                res[k] = eval(k)
            except NameError:
                pass
        self.set(**res)

        return res

    def splitDirName(self, dname):
        """
        Split dirname to attributes for DRS.

        Then set them as members of the instance, and also return as a dict.

        Args:
            dname (path-like) : directory name

        Returns:
            dict: attribute and it's value, {} if `dname` is not enough.

        Examples:

            >>> dname = ('/work/data/CMIP6/CMIP6/CMIP/MIROC/MIROC6/'
            ...          'piControl/r1i1p1f1/Amon/tas/gn/v20190308')
            >>> drs.DRS().splitDirName(dname) # doctest: +NORMALIZE_WHITESPACE
            {'activity_id': 'CMIP', 'experiment_id': 'piControl',
            'grid_label': 'gn', 'institution_id': 'MIROC', 'mip_era': 'CMIP6',
            'source_id': 'MIROC6', 'table_id': 'Amon', 'variable_id': 'tas',
            'variant_label': 'r1i1p1f1', 'version': 'v20190308',
            'prefix': '/work/data/CMIP6'}

            >>> dname = ('CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/'
            ...          'Amon/tas/gn/v20190308')
            >>> drs.DRS().splitDirName(dname) # doctest: +NORMALIZE_WHITESPACE
            {'activity_id': 'CMIP', 'experiment_id': 'piControl',
            'grid_label': 'gn', 'institution_id': 'MIROC', 'mip_era': 'CMIP6',
            'source_id': 'MIROC6', 'table_id': 'Amon', 'variable_id': 'tas',
            'variant_label': 'r1i1p1f1', 'version': 'v20190308', 'prefix': ''}
        """
        res = {}

        d = PurePath(dname)

        try:
            (version,
             grid_label,
             variable_id,
             table_id,
             member_id,
             experiment_id,
             source_id,
             institution_id,
             activity_id,
             mip_era) = d.parts[-1:-11:-1]
        except ValueError:
            return res

        try:
            (sub_experiment_id, variant_label) = member_id.split('-')
        except ValueError:
            variant_label = member_id

        for k in DRS.requiredAttribs:
            try:
                res[k] = eval(k)
            except NameError:
                pass
        self.set(**res)
        if (len(d.parts) > 10):
            res["prefix"] = str(PurePath(*d.parts[:-10]))
        else:
            res["prefix"] = ''
        return res

    def isValidPath(self, path, directory=False, separated=False):
        """
        Check if given `path` is DRS compliant.

        `path` may be a URL obtained by ESGF Search function. See
        :mod:`cmiputil.esgfsearch` for details.

        Args:
            path (Path-like) : pathname to be checked
            directory (bool) : treat `path` is a directory
            separated (bool) : return a tuple of two dicts

        If `separate` is True, return a tuple of two dicts, first
        element is for the filename, second is for the directory name,
        both dicts' key/value shows that each attributes are valid or
        not. If `directory` is ``True``, first elements is just a ``True``.

        Examples:

            >>> url = ('http://vesg.ipsl.upmc.fr/thredds/fileServer/cmip6/DCPP/IPSL/'
            ...       'IPSL-CM6A-LR/dcppC-pac-pacemaker/s1920-r1i1p1f1/Amon/rsdscs/'
            ...       'gr/v20190110/rsdscs_Amon_IPSL-CM6A-LR_dcppC-pac-'
            ...       'pacemaker_s1920-r1i1p1f1_gr_192001-201412.nc')
            >>> drs.DRS().isValidPath(url)
            True
        """
        p = PurePath(path)
        if (directory):
            fname = None
            dname = p
        else:
            fname = p.name
            dname = p.parent

        if (fname):
            f_attr = self.splitFileName(fname)
            f_res = {a: self.isValidValueForAttr(f_attr[a], a)
                     for a in f_attr if a in DRS.requiredAttribs}
        else:
            f_res = True
        if (dname != PurePath('.')):
            d_attr = self.splitDirName(dname)
            d_res = {a: self.isValidValueForAttr(d_attr[a], a)
                     for a in d_attr if a in DRS.requiredAttribs}
        else:
            d_res = True

        if separated:
            return f_res, d_res
        else:
            return all((f_res, d_res))


if __name__ == "__main__":
    from cmiputil import drs
    import doctest
    doctest.testmod()
