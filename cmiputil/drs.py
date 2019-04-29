#!/usr/bin/env python3
# coding:utf-8

"""
CMIP6 Data Reference Syntax (DRS):
==================================
(Excerpt from http://goo.gl/v1drZl)

File name template:
------------------
    file name = <variable_id>
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

if <sub_experiment_id> = “none”
  <member_id> = <variant_label>
else
  <member_id? = <sub_experiment_id>-<variant_label>
endif

The <time_range> is a string generated consistent with the following:

If frequency = “fx” then
  <time_range>=””
else
  <time_range> = N1-N2 where N1 and N2 are integers of the form
‘yyyy[MM[dd[hh[mm[ss]]]]][<suffix>]’ (expressed as a string,where where ‘yyyy’,
‘MM’, ‘dd’, ‘hh’ ‘mm’ and ‘ss’ are integer year, month, day, hour, minute, and
second, respectively) endif

where <suffix> is defined as follows:
  if the variable identified by variable_id has a time dimension with
  a “climatology” attribute then
     <suffix> = “-clim”
  else
     <suffix> = “”
endif

and where the precision of the time_range strings is determined by the
<frequency> global attribute.

Example when there is no <sub-experiment_id>:
  tas_Amon_GFDL-CM4_historical_r1i1p1f1_gn_196001-199912.nc
Example with a <sub-experiment_id>:
  pr_day_CNRM-CM6-1_dcppA-hindcast_s1960-r2i1p1f1_gn_198001-198412.nc



Directory structure template:
----------------------------
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
single <version> subdirectory at the end of the directory path should
represent all the available time-samples reported from the simulation;
a time-series can be split across several files, but all the files
must be found in the same subdirectory.  This implies that <version>
will not generally be the actual date that all files in the
subdirectory were written or published.

- If multiple activities are listed in the global attribute, the first one is
used in the directory structure.


Example when there is no <sub-experiment>:
     CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/1pctCO2/r1i1p1f1/Amon/tas/gn/v20150322
Example with a <sub-experiment>:
     CMIP6/DCPP/CNRM-CERFACS/CNRM-CM6-1/dcppA-hindcast/s1960-r2i1p1f3/day/pr/gn/v20160215

"""

from cmiputil.convoc import ConVoc
from pathlib import PurePath
from pprint import pprint

__author__ = 'T.Inoue'
__version__ = '0.9.0'
__date__ = '2019/04/16'


class DRSError(Exception):
    "Base exception class for DRS."
    pass


class InvalidDRSAttribError(DRSError):
    "Error for invalid attribute as DRS"

class InvalidPathAsDRSError(DRSError):
    "Error for invalid path as DRS"

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
    This class contains attributes necessary to construct a file
    name/directory name that is valid for CMIP6 DRS (Data Reference
    Syntax).  See http://goo.gl/v1drZl for details about DRS as well
    as CMIP6 global attributes, etc.

    Instance member variables of this class are:
    - variable_id
    - table_id
    - source_id
    - experiment_id
    - grid_label
    - time_range
    - version
    - sub_experiment_id
    - variant_label
    - member_id
    - mip_era
    - activity_id
    - institution_id
    - source_id

    Note that `member_id` is not able to set directly, this is set by
    <sub_experiment_id> (omittable) and <variant_label>.

    You can use the class member `drs.DRS().requiredAttribs` to know
    necessary attributes to set a filename/dirname valid for DRS.
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

    def __init__(self, file=None, **kw):
        self.cvs = ConVoc()
        self.mip_era = 'CMIP6'

        if (file):
            attrs = self.splitFileName(file)
            self.set(**attrs)
        else:
            self.set(**kw)

    def __repr__(self):
        res = ["{}={!a}".format(k, getattr(self, k))
               for k in DRS.requiredAttribs if k in dir(self)]
        res = 'drs.DRS(' + ', '.join(res) + ')'
        return res

    def __str__(self):
        res = ["{}: {!a}".format(k, getattr(self, k))
               for k in DRS.requiredAttribs if k in dir(self)]
        res = "\n".join(res)
        return res

    def getAttribs(self):
        """
        Current instance attributes.

        Return
        ------
        dict : attirbutes

        """
        return {k: getattr(self, k)
                for k in DRS.requiredAttribs if k in dir(self)}

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

        If `attr` is invalid, InvalidDRSAttribError is raised.

        Parameters
        ----------
          value : str
          attr : str
        Returns:
        --------
          logical
        """

        if attr == 'sub_experiment_id':
            # TODO:
            # Currently, value of <sub_experiment_id> used in
            # published datasets is only 's1920', which is not in CVs.
            # So avoid check tentatively
            return ConVoc().isValidValueForAttr(value, attr) or value == 's1920'
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

    def set(self, **argv):
        """
        Set instance attributes, if attribute is in
        `drs.DRS().requiredAttribs`.

        Missing attributes in argv are left unset/untouched.

        Unnecessary attributes are neglected.

        Each of attributes are checked by DRS.isValidValueForAttr().

        See isValidValueForAttr() for exception.

        Parameters:
        ----------
          argv : dict
        Returns
        -------
          self.

        """

        attribs = [a for a in argv.keys() if a in self.requiredAttribs]

        for attr in attribs:
            if (self.isValidValueForAttr(argv[attr], attr)):
                setattr(self, attr, argv[attr])

        if ('variant_label' in dir(self)):
            if ('sub_experiment_id' in dir(self)):
                self.member_id = argv['sub_experiment_id'] \
                                 + '-' \
                                 + argv['variant_label']
            else:
                self.member_id = argv['variant_label']
        return self


    def fileName(self):
        """
        Construct filename from current instance member attributes.

        Return
        ------
        str : filename
        """

        tmpl_w_time = "{var}_{tab}_{src}_{exp}_{mem}_{grd}_{tim}.nc"
        tmpl_wo_time = "{var}_{tab}_{src}_{exp}_{mem}_{grd}.nc"

        if ('time_range' in dir(self)):
            f = tmpl_w_time.format(
                var=self.variable_id,
                tab=self.table_id,
                src=self.source_id,
                exp=self.experiment_id,
                mem=self.member_id,
                grd=self.grid_label,
                tim=self.time_range,
            )
        else:
            f = tmpl_wo_time.format(
                var=self.variable_id,
                tab=self.table_id,
                src=self.source_id,
                exp=self.experiment_id,
                mem=self.member_id,
                grd=self.grid_label,
            )

        return str(f)

    def dirName(self, prefix=None):
        """
        Construct directory name by DRS from drs.DRS instance members.

        If any attributes are missing, raises AttributeError.

        Parameter
        ---------
        prefix(optional) : path-like : prepend to the result path.

        Return
        ------
        str : dirname

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
            d = prefix / d
        return str(d)

    def splitFileName(self, fname):
        """
        Split filename as attributes for DRS.

        If `fname` is invalid for DRS, raise ValueError 

        Parameters
        ----------
        fname : path-like

        Returns:
        --------
          dict

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
        Split given `dname` to set DRS().

        if `dname` has enough elements, return `{}`.

        Parameters:
        ----------
          dname : path-like
        Returns:
        --------
          dict
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
            # sub_experiment_id = None

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
        Check if given `path` is composed of DRS-valid attributes.

        `path` may be a URL obtained by ESGF Search function.

        If `directory` == True, ensure `path` is a directory, even if
        that ends with '/' or not.

        If `separate` == True, return dict that each attributes are
        valid or not.

        Parameter
        ---------
        `path` : `path-like`
        `directory` : `logical`

        Return
        ------
        `logical` or `dict` of {attr:logical} if `separated`

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

    def ex01():
        print("==ex01: DRS from dict w/o time_range ==")
        d = drs.DRS(**drs.sample_attrs)
        print(d)
        print("dirname:", d.dirName())
        print("filename:", d.fileName())
        print("="*30+"\n")

    def ex02():
        print("==ex02: DRS from dict w/ sub_experiment_id ==")
        d = drs.DRS(**drs.sample_attrs_w_subexp)
        print(d)
        print("dirname(): ", d.dirName())
        print("filename(): ", d.fileName())
        print("="*30+"\n")

        # print(d)

    def ex03():
        print("==ex03: dict with **invalid** `table_id`")
        attrs = drs.sample_attrs
        attrs.update({'table_id': 'invalid'})
        pprint(attrs)
        print("== DRS from this dict ==")
        d = drs.DRS(**attrs)
        print(d)
        print("== Note that `table_id` is not defined above,"
              "causes AttributeError below. ==")
        print("=== calling drs.DRS.fileName()...")
        try:
            print(d.fileName())
        except AttributeError:
            import traceback
            print("expected Exception raised:")
            traceback.print_exc()
        print("=== calling drs.DRS.dirName()...")
        try:
            print(d.dirName())
        except AttributeError:
            import traceback
            print("expected Exception raised:")
            traceback.print_exc()
        print("="*30+"\n")

    def ex04():
        print("== ex04: splitFileName")
        fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc"
        print(fname)
        d = drs.DRS()
        res = d.splitFileName(fname)
        pprint(res)
        print("="*30+"\n")

    def ex05():
        print("== ex05: splitDirName")
        dname = ('/work/data/CMIP6/CMIP6/CMIP/MIROC/MIROC6/'
                 'piControl/r1i1p1f1/Amon/tas/gn/v20190308')
        dname = ('CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/'
                 'Amon/tas/gn/v20190308')
        print(dname)
        d = drs.DRS()
        res = d.splitDirName(dname)
        pprint(res)
        print("="*30+"\n")

    def ex06():
        url = ("http://vesg.ipsl.upmc.fr/thredds/fileServer/cmip6/DCPP/IPSL/"
               "IPSL-CM6A-LR/dcppC-pac-pacemaker/s1920-r1i1p1f1/Amon/rsdscs/"
               "gr/v20190110/rsdscs_Amon_IPSL-CM6A-LR_dcppC-pac-"
               "pacemaker_s1920-r1i1p1f1_gr_192001-201412.nc")
        fname = PurePath(url).name
        dname = PurePath(url).parent

        print("== ex05: isValidPath?")

        print('url:', url)
        res = drs.DRS().isValidPath(url, separated=True)
        pprint(res)
        print(all(res))

        print('fname:', fname)
        res = drs.DRS().isValidPath(fname, separated=True)
        pprint(res)
        print(all(res))

        print('dname:', dname)
        res = drs.DRS().isValidPath(dname, directory=True, separated=True)
        pprint(res)
        print(all(res))

        print("="*30+"\n")

    def main():
        ex01()
        ex02()
        ex03()
        ex04()
        ex05()
        ex06()

    main()
