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
<variant_label> using the following algorithm::

    if <sub_experiment_id> == "none"
        <member_id> = <variant_label>
    else
        <member_id> = <sub_experiment_id>-<variant_label>
    endif

The <time_range> is a string generated consistent with the following::

    if frequency == "fx" then
        <time_range>=""
    else
        <time_range> = N1-N2
    endif

where N1 and N2 are integers of the form ``yyyy[MM[dd[hh[mm[ss]]]]][<suffix>]``
(expressed as a string, where ``yyyy``, ``MM``, ``dd``, ``hh``, ``mm`` and
``ss`` are integer year, month, day, hour, minute, and second, respectively),
where <suffix> is defined as follows::

    if the variable identified by variable_id has a time dimension with a “climatology” attribute then
         <suffix> = "-clim"
    else
         <suffix> = ""
    endif

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

- <version> has the form "vYYYYMMDD" (e.g., "v20160314"), indicating a
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
__version__ = 'v20190611'
__date__ = '2019/06/11'

from cmiputil.convoc import ConVoc
from cmiputil.braceexpand import braceexpand
import netCDF4 as nc
from pathlib import Path
import re
import glob
# from pprint import pprint


# def getDefaultConf():
#     """
#     Set default values for config file.

#     Currently no need to use config file, do nothing.
#     """
#     pass


class DRS:
    """Class for CMIP6 DRS.

    This class contains attributes necessary to construct a file
    name/directory name that is valid for CMIP6 DRS (Data Reference
    Syntax).  See above and http://goo.gl/v1drZl for details about DRS
    as well as CMIP6 global attributes, etc.

    Instance member variables of this class are:

    - ``activity_id``
    - ``experiment_id``
    - ``grid_label``
    - ``institution_id``
    - ``mip_era``
    - ``source_id``
    - ``source_id``
    - ``sub_experiment_id``
    - ``table_id``
    - ``time_range``
    - ``variable_id``
    - ``variant_label``
    - ``version``
    - ``member_id``

    Note that ``member_id`` is not able to set directly, this is
    constructed by ``sub_experiment_id`` (omittable) and
    ``variant_label``, via decorated method :meth:`member_id`.

    You can use the class member :attr:`requiredAttribs`,
    :attr:`filenameAttribs`, :attr:`filenameAttribsOptional`,
    :attr:`dirnameAttribs` to know necessary attributes to set this
    class and a filename/dirname valid for DRS.

    Note:
        Attributes as the class member,

        - ``hasattr(self, a) is False`` : not set explicitly
        - ``self.a == None`` : not set explicitly
        - ``self.a == '*'`` : set as is     <- not implemented yet
        - ``type(self.a) == list`` : multiple values for brace expansion.

    """

    #: Attributes managed in this class.
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

    #: Attributes necessary to construct dirname.
    dirnameAttribs = (
        "mip_era",
        "activity_id",
        "institution_id",
        "source_id",
        "experiment_id",
        "member_id",
        "table_id",
        "variable_id",
        "grid_label",
        "version")

    #: Attributes necessary to construct filename.
    filenameAttribs = (
        "variable_id",
        "table_id",
        "source_id",
        "experiment_id",
        "member_id",
        "grid_label",
        )

    #: Attributes optional to construct filename.
    filenameAttribsOptional = (
        "time_range",
        )

    #: list of <experiment_id> that have sub_experiment
    _experiments_w_sub = None

    #: ConVoc instance
    _cvs = None

    def __init__(self, file=None, filename=None, dirname=None,
                 do_sanitize=True, **kw):
        """
        Args:
            file(path-like): CMIP6 netCDF file.
            filename(str): filename to be used to set attributes.
            dirname(str): dirname to be used to set attributes.
            kw(dict): attribute-value pairs
            do_sanitize(bool): do sanitize or not

        If `file` is given, it must be a valid CMIP6 netCDF file, and
        attributes in that file are read and set.

        Else if `filename` is given, it must be a valid filename as DRS,
        and attributes are set from components consist of that name.

        Else if `dirname` is given, it must be a valid directory name as
        DRS, and attributes are set from components consist of that
        name.

        Else attributes are set from `**kw` dict.

        If `do_sanitize` is ``True``, remove invalid attribute values,
        else set as-is.

        You can sanitize *after* via :meth:`doSanitize`.


        Examples:
            >>> drs.DRS(filename='tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc')
            DRS(experiment_id='piControl', grid_label='gn', mip_era='CMIP6', source_id='MIROC6', table_id='Amon', time_range='320001-329912', variable_id='tas', variant_label='r1i1p1f1')
            >>> drs.DRS(dirname='/data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/')
            DRS(activity_id='CMIP', experiment_id='piControl', grid_label='gn', institution_id='MIROC', mip_era='CMIP6', source_id='MIROC6', table_id='Amon', variable_id='tas', variant_label='r1i1p1f1', version='v20181212')

            Do or not sanitize;

            >>> attrs = {k:v for k,v in drs.sample_attrs.items()}
            >>> attrs['table_id'] = 'INVALID'
            >>> d = drs.DRS(**attrs)
            >>> d.table_id
            Traceback (most recent call last):
                ...
            AttributeError: 'DRS' object has no attribute 'table_id'
            >>> d = drs.DRS(**attrs, do_sanitize=False)
            >>> d.table_id
            'INVALID'
        """
        if (not self.__class__._cvs):
            self.__class__._cvs = ConVoc()
        self.mip_era = 'CMIP6'

        if (file):
            attrs = self.getAttrsFromGA(file)
        elif (filename):
            attrs = self.splitFileName(filename)
        elif (dirname):
            attrs = self.splitDirName(dirname)
        else:
            attrs = kw
        self.set(do_sanitize=do_sanitize, **attrs)

    def __repr__(self):
        # Since now attributes of self allow to be a list, but at
        # setter values must be a comma-separated str, must convert
        # list to str.
        res = []
        for a in self.requiredAttribs:
            if hasattr(self, a):
                v = getattr(self, a)
                if (type(v) is list):
                    v = ', '.join(v)
                res.append("{}='{}'".format(a, v))
        res = (self.__class__.__name__
               + '(' + ', '.join(res) + ')')
        return res

    def __str__(self):
        res = ["{}: {!a}".format(k, getattr(self, k))
               for k in self.requiredAttribs if hasattr(self, k)]
        res = "\n".join(res)
        return res

    def __eq__(self, other):
        typecheck = (type(self) == type(other))
        res = [(getattr(self, k) == getattr(other, k))
               for k in self.requiredAttribs
               if hasattr(self, k)]
        return (all(res) and typecheck)

    def getAttrsFromGA(self, file):
        """
        Obtain requiered attributes from the global attributes defined
        in a valid netCDF file.

        Args:
            file(str or path-like?): filename of a valid netCDF file.

        Returns:
            dict: whose keys are from :attr:`DRS.requiredAttribs`.

        TODO:
            Should this be the member of this class ??

        """

        with nc.Dataset(file, "r") as ds:
            attrs = {a: getattr(ds, a, None)
                     for a in self.requiredAttribs}
        attrs = {a: v for a, v in attrs.items() if (v and v != 'none')}
        return attrs

    def set(self, do_sanitize=True, **argv):
        """
        Set instance attributes, if attribute is in :attr:`requiredAttribs`.

        In `argv`,

        - missing attributes are left unset/untouched,
        - attribute with invalid value is sanitized via
          :meth:`doSanitize` if ``do_sanitize=True``,
        - unnecessary attributes are neglected.

        Each of attributes are checked by
        :meth:`isValidValueForAttr()` before set.

        Args:
            argv (dict): attribute/value pairs
            do_sanitize(bool): remove invalid values via :meth:`doSanitize`

        Return:
            nothing

        Examples:

            >>> d = drs.DRS(**drs.sample_attrs)
            >>> d
            DRS(activity_id='CMIP', experiment_id='piControl', grid_label='gn', institution_id='MIROC', mip_era='CMIP6', source_id='MIROC6', table_id='Amon', time_range='320001-329912', variable_id='tas', variant_label='r1i1p1f1', version='v20181212')
            >>> d.set(experiment_id='amip')
            >>> d.experiment_id
            'amip'
            >>> d.set(experiment_id='invalid_experiment')
            >>> d.experiment_id
            Traceback (most recent call last):
                ...
            AttributeError: 'DRS' object has no attribute 'experiment_id'

            In the last example, invalid value for `experiment_id` is
            sanitized since ``do_sanitize=True`` by default.

        """
        attribs = {a: argv[a] for a in argv.keys()
                   if a in self.requiredAttribs}

        for a, v in attribs.items():
            v = [vv.strip() for vv in v.split(',')]
            if len(v) > 1:
                setattr(self, a, v)
            else:
                setattr(self, a, v[0])

        # self.set_member_id()

        if (do_sanitize):
            self.doSanitize()

    def fileName(self, prefix=None, w_time_range=True,
                 allow_asterisk=True):
        """
        Construct filename from current instance member attributes.

        Args:
            prefix(path-like): prepend to the resulting filename
            w_time_range(bool): result contains <time_range> part or not
            allow_asterisk(bool): allow result contains ``*``
        Raises:
            AttributeError: any attributes are missing.

        Returns:
            path-like: filename

        Note:
            By definition, including <time_range> part or not is
            decided by the attribute <frequency> is 'fx' or not.
            <frequency> is the same with the attribute <table_id>, so
            in this method if ``self.table_id == 'fx'`` force
            `w_time_range` to be ``True``.
            If ``self.table_id = '*'`` or set multi values and you
            want force <time_range> part to be omitted, set
            ``w_time_range=False`` explicitly.

        Examples:

            Usual case;

            >>> str(drs.DRS(**drs.sample_attrs).fileName())
            'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc'

            With ``sub_experiment_id``;

            >>> str(drs.DRS(**drs.sample_attrs_w_subexp).fileName())
            'rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker_s1950-r1i1p1f1_gr_192001-201412.nc'

            No ``time_range``;

            >>> str(drs.DRS(**drs.sample_attrs_no_time_range).fileName(w_time_range=False))
            'areacella_fx_MIROC6_historical_r1i1p1f1_gn.nc'

            With prefix;

            >>> prefix=Path('/data/CMIP6/')
            >>> str(drs.DRS(**drs.sample_attrs).fileName(prefix))
            '/data/CMIP6/tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc'

            Invalid value for valid attribute;

            >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
            >>> attrs.update({'table_id': 'invalid'})
            >>> str(drs.DRS(**attrs).fileName())
            'tas_*_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc'
            >>> str(drs.DRS(**attrs).fileName(allow_asterisk=False))
            Traceback (most recent call last):
               ...
            AttributeError: 'DRS' object has no attribute 'table_id'


            Missing attributes;

            >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
            >>> del attrs['time_range']
            >>> str(drs.DRS(**attrs).fileName())
            'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_*.nc'
            >>> str(drs.DRS(**attrs).fileName(allow_asterisk=False))
            Traceback (most recent call last):
               ...
            AttributeError: 'DRS' object has no attribute 'time_range'

            Allow multi values;

            >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
            >>> attrs.update({'experiment_id':'amip, piControl'})
            >>> str(drs.DRS(**attrs).fileName())
            'tas_Amon_MIROC6_{amip,piControl}_r1i1p1f1_gn_320001-329912.nc'
        """
        attr = {}
        for a in self.filenameAttribs + self.filenameAttribsOptional:
            try:
                v = getattr(self, a)
            except AttributeError:
                if (allow_asterisk):
                    v = '*'
                else:
                    raise
            if type(v) is list:
                v = '{'+','.join(v)+'}'
            attr[a] = v

        if (attr['table_id'] == 'fx'):
            w_time_range = False
        if w_time_range:
            f = ("{variable_id}_{table_id}_{source_id}_{experiment_id}"
                 "_{member_id}_{grid_label}_{time_range}.nc").format(**attr)
        else:
            f = ("{variable_id}_{table_id}_{source_id}_{experiment_id}"
                 "_{member_id}_{grid_label}.nc").format(**attr)
        f = Path(f)
        if (prefix):
            f = Path(prefix) / f

        return f

    def fileNameList(self, prefix=None):
        """
        Returns a list of filenames constructed by the instance member
        attributes that may contains '*' and/or braces.

        Returns:
        list of str: filenames

        Todo:
            Since non-existent files are omitted, this method seems
            useless. Implement pathNameList() to obtain a list of
            path(dir/file)

        Examples:

            >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
            >>> attrs.update({'experiment_id':'amip, piControl'})
            >>> del attrs['time_range']
            >>> str(drs.DRS(**attrs).fileName())
            'tas_Amon_MIROC6_{amip,piControl}_r1i1p1f1_gn_*.nc'

            >>> dlist = drs.DRS(**attrs).fileNameList() # doctest: +SKIP
            >>> [str(d) for d in dlist]  # doctest: +SKIP
            ['tas_Amon_MIROC6_amip_r1i1p1f1_gn_*.nc',
             'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_*.nc']

            The last example will return ``[]`` if expanded files do not
            exist.

        """
        fname = self.fileName(prefix=prefix)
        flist = [glob.glob(p) for p in braceexpand(str(fname))]
        return [f for ff in flist for f in ff]

    def dirName(self, prefix=None, allow_asterisk=True):
        """
        Construct directory name by DRS from :class:`DRS` instance members.

        If `allow_asterisk` is ``True``, invalid

        If you want glob/brace expaned list, use :meth:`dirNameList` instead.

        Args:
            prefix (Path-like): prepend to the result path.
            allow_asterisk: allow result contains ``*`` or not.
        Raises:
            AttributeError: any attributes are missing or invalid and
                            ``allow_asterisk=False``

        Returns:
            Path-like : directory name

        Examples:

            Usual case;

            >>> str(drs.DRS(**drs.sample_attrs).dirName())
            'CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212'

            With ``sub_experiment_id``;

            >>> str(drs.DRS(**drs.sample_attrs_w_subexp).dirName())
            'CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/s1950-r1i1p1f1/Amon/rsdscs/gr/v20190110'

            Invalid value for valid attribute;

            >>> attrs = {k:v for k,v in drs.sample_attrs.items()}
            >>> attrs['table_id'] = 'invalid'
            >>> str(drs.DRS(**attrs).dirName())
            'CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/*/tas/gn/v20181212'
            >>> str(drs.DRS(**attrs).dirName(allow_asterisk=False))
            Traceback (most recent call last):
                ...
            AttributeError: 'DRS' object has no attribute 'table_id'

            Missing attributes;

            >>> attrs = {k:v for k,v in drs.sample_attrs.items()}
            >>> del attrs['experiment_id']
            >>> str(drs.DRS(**attrs).dirName(prefix='/data/'))
            '/data/CMIP6/CMIP/MIROC/MIROC6/*/r1i1p1f1/Amon/tas/gn/v20181212'
            >>> str(drs.DRS(**attrs).dirName(prefix='/data/', allow_asterisk=False))
            Traceback (most recent call last):
                ...
            AttributeError: 'DRS' object has no attribute 'experiment_id'

            Allow multi values;

            >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
            >>> attrs.update({'experiment_id':'amip, piControl'})
            >>> str(drs.DRS(**attrs).dirName())
            'CMIP6/CMIP/MIROC/MIROC6/{amip,piControl}/r1i1p1f1/Amon/tas/gn/v20181212'

        """
        attr = {}
        for a in self.dirnameAttribs:
            try:
                v = getattr(self, a)
            except AttributeError:
                if allow_asterisk:
                    v = '*'
                else:
                    raise
            if type(v) is list:
                v = '{'+','.join(v)+'}'
            attr[a] = v
        print(attr)

        d = Path(
           attr["mip_era"],
           attr["activity_id"],
           attr["institution_id"],
           attr["source_id"],
           attr["experiment_id"],
           attr["member_id"],
           attr["table_id"],
           attr["variable_id"],
           attr["grid_label"],
           attr["version"])
        if (prefix):
            d = Path(prefix) / d
        return d

    def dirNameList(self, prefix=None):
        """
        Return list of directory name constructed by DRS from
        :class:`DRS` instance members, that contains asterisk and/or
        braces

        Args:
            prefix(path-like): dirname to prepend.

        Returns:
            list of path-like: directory names

        Note:
            Non-existent directories are omitted.

        Examples:
            >>> attrs = {k: v for k, v in drs.sample_attrs.items()}
            >>> attrs.update({'experiment_id':'amip, piControl'})
            >>> del attrs['version']
            >>> str(drs.DRS(**attrs).dirName())
            'CMIP6/CMIP/MIROC/MIROC6/{amip,piControl}/r1i1p1f1/Amon/tas/gn/*'
            >>> drs.DRS(**attrs).dirNameList(prefix='/data')
            ['/data/CMIP6/CMIP/MIROC/MIROC6/amip/r1i1p1f1/Amon/tas/gn/v20181214', '/data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212']

            The last example will return ``[]`` if expanded directories do
            not exist.

        TODO:
            Completely re-implment that

            - get list use glob (asterisk expansion) only
            - filter out using regex by brace list

        """
        dname = self.dirName(prefix=prefix)  # may contain '*' and braces
        plist = [glob.glob(p) for p in braceexpand(str(dname))]
        return [p for pp in plist for p in pp]

    def splitFileName(self, fname, validate=False):
        """Split filename to attributes for DRS.

        If ``varidate=False``, just split only. So if the `fname`
        consist of the same number of components with DRS-valid
        filename, no error happens. You should set `validate=True` or
        use :meth:`isValidValueForAttr` by yourself.

        Args:
            fname (Path-like) : filename
            validate(bool) : validate the resulting attribute/value pair

        Raises:
            ValueError: if `fname` is invalid for DRS.

        Returns:
            dict: attribute and it's value

        Note:
            Instance members keep untouched, give :meth:`set` the
            result of this method.

        Examples:

            >>> fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc"
            >>> drs.DRS().splitFileName(fname)
            {'experiment_id': 'piControl', 'grid_label': 'gn', 'source_id': 'MIROC6', 'table_id': 'Amon', 'time_range': '320001-329912', 'variable_id': 'tas', 'variant_label': 'r1i1p1f1'}
            >>> fname='invalid_very_long_file_name.nc'
            >>> drs.DRS().splitFileName(fname)
            Traceback (most recent call last):
                ...
            ValueError: not follow the name template: "invalid_very_long_file_name.nc"
            >>> fname='invalid_but_same_length_with_drs.nc'
            >>> drs.DRS().splitFileName(fname)
            {'experiment_id': 'length', 'grid_label': 'drs', 'source_id': 'same', 'table_id': 'but', 'variable_id': 'invalid', 'variant_label': 'with'}
            >>> drs.DRS().splitFileName(fname, validate=True)
            Traceback (most recent call last):
                ...
            ValueError: "length" is invalid for <experiment_id>
        """
        try:
            (variable_id, table_id, source_id, experiment_id, member_id,
             grid_label) = Path(fname).stem.split('_', 5)
        except ValueError:
            raise ValueError(f'not follow the name template: "{fname}"')

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
        for a in self.requiredAttribs:
            try:
                res[a] = eval(a)
            except NameError:
                pass

        if validate:
            for a, v in res.items():
                if not self.isValidValueForAttr(v, a):
                    raise ValueError(f'"{v}" is invalid for <{a}>')
        return res

    def splitDirName(self, dname, validate=False):
        """Split dirname to attributes for DRS.

        If ``varidate=False``, just split only. So if the `dname`
        consist of the same number of components with DRS-valid
        directory name, no error happens. You should set
        `validate=True` or use :meth:`isValidValueForAttr` by
        yourself.

        Args:
            dname (path-like) : directory name
            validate(bool) : validate the resulting attribute/value pair

        Returns:
            dict: attribute and it's value

        Note:
            Instance members keep untouched, give :meth:`set` the
            result of this method.

        Examples:

            >>> dname = 'CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212'
            >>> drs.DRS().splitDirName(dname)
            {'activity_id': 'CMIP', 'experiment_id': 'piControl', 'grid_label': 'gn', 'institution_id': 'MIROC', 'mip_era': 'CMIP6', 'source_id': 'MIROC6', 'table_id': 'Amon', 'variable_id': 'tas', 'variant_label': 'r1i1p1f1', 'version': 'v20181212', 'prefix': ''}

            With `prefix`;

            >>> dname = ('/work/data/CMIP6/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212')
            >>> drs.DRS().splitDirName(dname)
            {'activity_id': 'CMIP', 'experiment_id': 'piControl', 'grid_label': 'gn', 'institution_id': 'MIROC', 'mip_era': 'CMIP6', 'source_id': 'MIROC6', 'table_id': 'Amon', 'variable_id': 'tas', 'variant_label': 'r1i1p1f1', 'version': 'v20181212', 'prefix': '/work/data/CMIP6'}

            Invalid case;

            >>> dname = 'Some/Invalid/Path'
            >>> drs.DRS().splitDirName(dname)
            Traceback (most recent call last):
                ...
            ValueError: Invalid dirname: "Some/Invalid/Path"
            >>> dname = 'Some/Invalid/but/has/occasionally/the/same/number/of/component/'
            >>> drs.DRS().splitDirName(dname)
            {'activity_id': 'Invalid', 'experiment_id': 'occasionally', 'grid_label': 'of', 'institution_id': 'but', 'mip_era': 'Some', 'source_id': 'has', 'table_id': 'same', 'variable_id': 'number', 'variant_label': 'the', 'version': 'component', 'prefix': ''}
            >>> drs.DRS().splitDirName(dname, validate=True)
            Traceback (most recent call last):
                ...
            ValueError: "Invalid" is invalid for <activity_id>
        """
        res = {}

        d = Path(dname)

        try:
            (version, grid_label,  variable_id, table_id, member_id,
             experiment_id, source_id, institution_id, activity_id,
             mip_era) = d.parts[-1:-11:-1]
        except ValueError:
            raise ValueError(f'Invalid dirname: "{dname}"')


        try:
            (sub_experiment_id, variant_label) = member_id.split('-')
        except ValueError:
            variant_label = member_id

        for k in self.requiredAttribs:
            try:
                res[k] = eval(k)
            except NameError:
                pass

        if validate:
            for a, v in res.items():
                if not self.isValidValueForAttr(v, a):
                    raise ValueError(f'"{v}" is invalid for <{a}>')

        if (len(d.parts) > 10):
            res["prefix"] = str(Path(*d.parts[:-10]))
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

        Returns:
            bool or list of bool : valid or not (see below)

        If `separate` is True, return a tuple of two dicts, first
        element is for the filename, second is for the directory name,
        both dicts' key/value shows that each attributes are valid or
        not. If `directory` is ``True``, first elements is ``{'all': True}``.

        Examples:

            >>> url = ('http://vesg.ipsl.upmc.fr/thredds/fileServer/cmip6/DCPP/'
            ...       'IPSL/IPSL-CM6A-LR/dcppC-pac-pacemaker/s1920-r1i1p1f1/'
            ...       'Amon/rsdscs/gr/v20190110/rsdscs_Amon_IPSL-CM6A-LR_'
            ...       'dcppC-pac-pacemaker_s1920-r1i1p1f1_gr_192001-201412.nc')
            >>> drs.DRS().isValidPath(url)
            True
            >>> drs.DRS().isValidPath(url, separated=True)
            ({'experiment_id': True, 'grid_label': True, 'source_id': True, 'sub_experiment_id': True, 'table_id': True, 'time_range': True, 'variable_id': True, 'variant_label': True}, {'activity_id': True, 'experiment_id': True, 'grid_label': True, 'institution_id': True, 'mip_era': True, 'source_id': True, 'sub_experiment_id': True, 'table_id': True, 'variable_id': True, 'variant_label': True, 'version': True})
            >>> url = ('http://vesg.ipsl.upmc.fr/thredds/fileServer/cmip6/DCPP/'
            ...       'IPSL/IPSL-CM6A-LR/dcppC-pac-pacemaker/s1920-r1i1p1f1/'
            ...       'Amon/rsdscs/gr/v20190110')
            >>> drs.DRS().isValidPath(url)
            False
            >>> drs.DRS().isValidPath(url, directory=True)
            True
        """
        p = Path(path)
        if (directory):
            fname = None
            dname = p
        else:
            fname = p.name
            dname = p.parent

        if (fname):
            try:
                f_attr = self.splitFileName(fname)
            except ValueError:
                f_res = {'all': False}
            else:
                f_res = {a: self.isValidValueForAttr(f_attr[a], a)
                     for a in f_attr if a in self.requiredAttribs}
        else:
            f_res = {'all': True}
        if (dname != Path('.')):
            try:
                d_attr = self.splitDirName(dname)
            except ValueError:
                d_res = {'all': False}
            else:
                d_res = {a: self.isValidValueForAttr(d_attr[a], a)
                     for a in d_attr if a in self.requiredAttribs}
        else:
            d_res = {'all': True}

        if separated:
            return f_res, d_res
        else:
            return all(f_res.values()) and all(d_res.values())

    def isValid(self, silent=True):
        """
        Check if attributes are valid as DRS.

        Args:
          silent(bool): no message even if something is invalid.

        Return:
          bool: all attributes are valid or not.

        Examples:
            >>> d = drs.DRS(**drs.sample_attrs)
            >>> d.isValid()
            True
            >>> d.activity_id = 'InvalidMIP'
            >>> d.isValid()
            False
        """
        return self._validate(silent=silent, delete_invalid=False)

    def isValidValueForAttr(self, value, attr):
        """
        Check `value` is valid for the attribute `attr`.

        Args:
            value (object) : value for `attr`
            attr (object) : global attribute
        Raises:
            AttributeError: raises when `attr` is invalid for DRS.
        Returns:
            bool: whether `value` is valid for the attribute `attr`

        Examples:

            >>> d = drs.DRS()
            >>> d.isValidValueForAttr('Amon', 'table_id')
            True
            >>> d.isValidValueForAttr('Invalid', 'source_id')
            False
            >>> d.isValidValueForAttr('piControl', 'experiment_id')
            True
            >>> d.isValidValueForAttr('piControl', 'experiments_id')
            Traceback (most recent call last):
                ...
            AttributeError: ('Invalid Attribute for DRS:', 'experiments_id')
            >>> d.isValidValueForAttr('*', 'institution_id')
            True
            >>> d.isValidValueForAttr('MIROC*', 'source_id')
            True
        """
        if value is None:
            return False

        if '*' in value:
            return True

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
            raise AttributeError('Invalid Attribute for DRS:', attr)

    def getAttribs(self):
        """
        Return current instance attributes defined of
        :attr:`requiredAttribs` and their values.

        Returns:
            dict: attribute-value pairs.
        """
        return {k: getattr(self, k)
                for k in self.requiredAttribs if hasattr(self, k)}

    @property
    def member_id(self):
        """Getter for the attribute <member_id>.

        See the definition of this attribute in :mod:`cmiputil.drs`.
        """


        if not self.__class__._experiments_w_sub:
            exps = self._cvs.getAttrib('experiment_id')
            self.__class__._experiments_w_sub = [
                e for e in exps.keys()
                if exps[e]['sub_experiment_id'][0] != 'none']

        if (hasattr(self, 'variant_label')):
            if (hasattr(self, 'sub_experiment_id')):
                subexp = self.sub_experiment_id
                varlab = self.variant_label
                res = f"{subexp}-{varlab}"
            else:
                res = self.variant_label
            return res
        # else:
        #     return None

    def doSanitize(self, silent=True):
        """
        Sanitize instances.

        That is, remove invalid values for valid attributes.

        Args:
            silent(bool): do it silently or not

        Returns:
            nothing

        Examples:

            >>> d = drs.DRS(**drs.sample_attrs)
            >>> d.activity_id = 'InvalidMIP'
            >>> hasattr(d, 'activity_id')
            True
            >>> d.doSanitize()
            >>> hasattr(d, 'activity_id')
            False

            For above case, You should use ``d.set(activity_id='...')``
            instead of setting an attribute directly. See :meth:`set`.
        """
        self._validate(silent=silent, delete_invalid=True)

    def _validate(self, silent=False, delete_invalid=False):
        fmt = 'Warining: <{}> has invalid value "{}".'
        res = {}
        for a in self.requiredAttribs:
            v = getattr(self, a, None)
            if v is None:
                pass
            elif type(v) is list:
                # res[a] = True # tentative
                vals = {vv: self.isValidValueForAttr(vv, a) for vv in v}
                res[a] = all(vals.values())
                if (not res[a]):
                    if (not silent):
                        print(fmt.format(a, [vv for vv in v if not vals[vv]]))
                    if (delete_invalid):
                        setattr(self, a, [vv for vv in v if vals[vv]])
            else:
                if self.isValidValueForAttr(v, a):
                    res[a] = True
                else:
                    res[a] = False
                    if (not silent):
                        print(fmt.format(a, v))
                    if (delete_invalid):
                        delattr(self, a)
        return all(res.values())

    def _check_time_range(self, value):
        # TODO: precision and `-clim` depends on the attribute `frequency`.
        #       but I don't need quality assurance.
        if (value is None):
            return False
        elif (value == ""):
            return False
        # pat = re.compile(r'\d{4,8}(-clim)?-\d{4,8}(-clim)?')
        pat = re.compile(r'\d{4}(\d\d(\d\d(\d\d(\d\d(\d\d)?)?)?)?)?'
                         r'(-clim)?'
                         r'-'
                         r'\d{4}(\d\d(\d\d(\d\d(\d\d(\d\d)?)?)?)?)?'
                         r'(-clim)?'
                         )
        return pat.fullmatch(value) is not None

    def _check_version(self, value):
        if (value is None):
            return False
        pat = re.compile(r'v\d{8}')
        return pat.fullmatch(value) is not None

    def _check_variable_id(self, value):
        # TODO: Is there any method to check ?
        return value is not None

    def _check_variant_label(self, value):
        if (value is None):
            return False
        pat = re.compile(r'r\d+i\d+p\d+f\d+')
        return pat.fullmatch(value) is not None




sample_attrs = {
    'activity_id': 'CMIP',
    'experiment_id': 'piControl',
    'grid_label': 'gn',
    'institution_id': 'MIROC',
    'source_id': 'MIROC6',
    'table_id': 'Amon',
    'time_range': '320001-329912',
    'variable_id': 'tas',
    'variant_label': 'r1i1p1f1',
    'version': 'v20181212',
    'non_necessary_attribute': 'hoge'
}
sample_fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc"
sample_dname = ("CMIP6/CMIP/MIROC/MIROC6/piControl/"
                "r1i1p1f1/Amon/tas/gn/v20181212")

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
sample_fname_w_subexp = ('rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker'
                         '_s1950-r1i1p1f1_gr_192001-201412.nc')
sample_dname_w_subexp = ('CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/'
                         's1950-r1i1p1f1/Amon/rsdscs/gr/v20190110')

sample_attrs_no_time_range = {
    'activity_id': 'CMIP',
    'experiment_id': 'historical',
    'grid_label': 'gn',
    'institution_id': 'MIROC',
    'mip_era': 'CMIP6',
    'prefix': '',
    'source_id': 'MIROC6',
    'table_id': 'fx',
    'variable_id': 'areacella',
    'variant_label': 'r1i1p1f1',
    'version': 'v20190311'}
sample_fname_no_time_range = 'areacella_fx_MIROC6_historical_r1i1p1f1_gn.nc'
sample_dname_no_time_range = ('CMIP6/CMIP/MIROC/MIROC6/historical/r1i1p1f1/'
                              'fx/areacella/gn/v20190311/')


if __name__ == "__main__":
    from cmiputil import drs
    import doctest
    doctest.testmod()
