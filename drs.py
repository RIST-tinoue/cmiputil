#!/usr/bin/env python3
#coding:utf-8
"""CMIP6 Data Reference Syntax (DRS):

(Excerpt from http://goo.gl/v1drZl)

File name template:

file name = <variable_id>_<table_id>_<source_id>_<experiment_id >_<member_id>_<grid_label>[_<time_range>].nc

For time-invariant fields, the last segment (time_range) above is omitted.

Example when there is no sub-experiment:
  tas_Amon_GFDL-CM4_historical_r1i1p1f1_gn_196001-199912.nc
Example with a sub-experiment:
  pr_day_CNRM-CM6-1_dcppA-hindcast_s1960-r2i1p1f1_gn_198001-198412.nc


All strings appearing in the file name are constructed using only the following
characters: a-z, A-Z, 0-9, and the hyphen ("-"), except the hyphen must not
appear in variable_id.  Underscores are prohibited throughout except as shown in
the template.


The member_id is constructed from the
sub_experiment_id and variant_label using the following algorithm:


if sub_experiment_id = “none”
  member_id = <variant_label>
else
  member_id = <sub_experiment_id>-<variant_label>
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
  if the variable identified by variable_id has a time dimension with a “climatology” attribute then
     suffix = “-clim”
  else
     suffix = “”
endif

and where the precision of the time_range strings is determined by the
“frequency” global attribute as specified in Table 2.


Directory structure template:

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
representative date for the version.  Note that filescontained in a single
<version> subdirectory at the end of the directory path should represent all
the available time-samplesreported from the simulation; a time-series can be
split across several files, but all the files must be found in the
samesubdirectory.  This implies that <version> will not generally be the actual
date that all files in the subdirectory were written orpublished.

- If multiple activities are listed in the global attribute, the first one is
used in the directory structure.

Example when there is no sub-experiment:
     CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/1pctCO2/r1i1p1f1/Amon/tas/gn/v20150322
Example with a sub-experiment:
     CMIP6/DCPP/CNRM-CERFACS/CNRM-CM6-1/dcppA-hindcast/s1960-r2i1p1f3/day/pr/gn/v20160215

"""

from convoc import ConVoc
import os.path
from pprint import pprint

__author__ = 'T.Inoue'
__version__ = '0.9.0'
__date__ = '2019/04/16'

class DRSError(Exception):
    "Base exception class for DRS."
    pass


class InvalidDRSAttribError(DRSError):
    "Error for invalid attribute as a component DRS"


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
    """This class contains attributes necessary to construct filename and
    directory name follows CMIP6 DRS (Data Reference Syntax).

    Instance member variables are:
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

    Note that member_id is not able to set directly, this is set by
    sub_experiment_id (omittable) and variant_label.

    See http://goo.gl/v1drZl for details about DRS as well as CMIP6 global
    attributes, etc.
    """
    requiredAttribs = (
        'activity_id',
        'experiment_id',
        'grid_label',
        'institution_id',
        'member_id',
        'mip_era',
        'source_id',
        'sub_experiment_id',
        'table_id',
        'time_range',
        'variable_id',
        'variant_label',
        'version',
        )


    def __init__(self, **kw):
        self.cvs = ConVoc()
        self.mip_era = 'CMIP6'
        self.set(**kw)


    def __repr__(self):
        tmpl = ("drs.DRS("
                "mip_era={!a}, "
                "activity_id={!a}, "
                "institution_id={!a}, "
                "variable_id={!a}, "
                "table_id={!a},"
                "source_id={!a},"
                "experiment_id={!a},"
                "sub_experiment_id={!a},"
                "variant_label={!a},"
                "grid_label={!a},"
                "time_range={!a},"
                "version={!a})")

        return tmpl.format(
            getattr(self,'mip_era'),
            getattr(self,'activity_id'),
            getattr(self,'institution_id'),
            getattr(self,'variable_id'),
            getattr(self,'table_id'),
            getattr(self,'source_id'),
            getattr(self,'experiment_id'),
            getattr(self,'sub_experiment_id'),
            getattr(self,'variant_label'),
            getattr(self,'grid_label'),
            getattr(self,'time_range'),
            getattr(self,'version')
            )

    def __str__(self):
        tmpl = ("========== DRS instance ==========\n"
                "mip_era        : {!a}\n"
                "activity_id    : {!a}\n"
                "institution_id : {!a}\n"
                "variable_id    : {!a}\n"
                "table_id       : {!a}\n"
                "source_id      : {!a}\n"
                "experiment_id  : {!a}\n"
                "sub_experiment_id: {!a}\n"
                "variant_label  : {!a}\n"
                "member_id      : {!a}\n"
                "grid_label     : {!a}\n"
                "time_range     : {!a}\n"
                "version        : {!a}\n"
                "=================================\n")

        return tmpl.format(
            getattr(self,'mip_era', None),
            getattr(self,'activity_id', None),
            getattr(self,'institution_id', None),
            getattr(self,'variable_id', None),
            getattr(self,'table_id', None),
            getattr(self,'source_id', None),
            getattr(self,'experiment_id', None),
            getattr(self,'sub_experiment_id', None),
            getattr(self,'variant_label', None),
            getattr(self,'member_id', None),
            getattr(self,'grid_label', None),
            getattr(self,'time_range', None),
            getattr(self,'version', None)
            )

    def check_time_range(self, value):
        # must be 'YYYYMMDD-YYYYMMDD', use regex.
        return value is not None

    def check_version(self, value):
        # must be 'vYYYYMMDD', use regex.
        return True

    def check_variable_id(self, value):
        # Is there any method to check ?
        return True

    def check_variant_label(self, value):
        # TODO: must be r{i}i{i}p{i}f{i}, use regex.
        return True

    def checkAttribs(self, value, attr):
        "Check `value` is valid for the attribute `attr`"
        if attr == 'time_range':
            return self.check_time_range(value)
        elif attr == 'version':
            return self.check_version(value)
        elif attr == 'variable_id':
            return self.check_variable_id(value)
        elif attr == 'variant_label':
            return self.check_variant_label(value)
        elif attr == 'mip_era':
            return True
        else:
            raise InvalidDRSAttribError('Invalid Attribute for DRS:', attr)



    def set(self, **argv):
        """
        Set attributes as members of self, if attribute is in
        `self.requiredAttribs`.

        Missing attributes in argv are selft unset as members.

        Unnecessary attributes are neglected.

        Each of attributes must pass ConVoc.checkKey() or DRS.checkAttribs().
        """

        attribs =[a for a in argv.keys() if a in self.requiredAttribs]
        cvattrs     = [ a for a in attribs if a in self.cvs.managedAttribs]
        non_cvattrs = [ a for a in attribs if a not in self.cvs.managedAttribs]

        for attr in cvattrs:
            if (self.cvs.checkKey(argv[attr], attr)):
                setattr(self, attr, argv[attr])

        for attr in non_cvattrs:
            if (self.checkAttribs(argv[attr],attr)):
                setattr(self, attr, argv[attr])

        if ('variant_label' in dir(self)):
            if ('sub_experiment_id' in dir(self)):
                self.member_id = argv['sub_experiment_id'] \
                                 + '-' \
                                 + argv['variant_label']
            else:
                self.member_id = argv['variant_label']

        # How to check all necessary members are set.
        # pprint([(k, k in dir(self)) for k in self.requiredAttribs])

        return self

    def fileName(self):
        """
        Construct filename from instance members.
        """

        if ('time_range' in dir(self)):
            f = "{}_{}_{}_{}_{}_{}_{}.nc".format(
                self.variable_id,
                self.table_id,
                self.source_id,
                self.experiment_id,
                self.member_id,
                self.grid_label,
                self.time_range,
            )
        else:
            f = "{}_{}_{}_{}_{}_{}.nc".format(
                self.variable_id,
                self.table_id,
                self.source_id,
                self.experiment_id,
                self.member_id,
                self.grid_label
            )

        return f

    def dirName(self, prefix=None):

        # TODO: error check
        d = os.path.join(
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
            d = os.path.join(prefix, d)
        return d

    def splitFileName(self, fname):
        fbase, fext = os.path.splitext(fname)

        (variable_id,
         table_id,
         source_id,
         experiment_id,
         member_id,
         grid_label) = os.path.basename(fbase).split('_', 5)

        try:
            (grid_label, time_range) = grid_label.split('_')
        except ValueError:
            time_range = None

        try:
            (sub_experiment_id, variant_label) = member_id.split('-')
        except ValueError:
            variant_label = member_id
            sub_experiment_id = None

        res = {'variable_id': variable_id,
               'table_id': table_id,
               'source_id': source_id,
               'experiment_id': experiment_id,
               'variant_label': variant_label,
               'grid_label': grid_label,
               'time_range': time_range,
               'sub_experiment_id': sub_experiment_id}
        self.set(**res)

        return res

    def splitDirName(self, dname):
        (dname, version) = os.path.split(dname)
        (dname, grid_label) = os.path.split(dname)
        (dname, variable_id) = os.path.split(dname)
        (dname, table_id) = os.path.split(dname)
        (dname, member_id) = os.path.split(dname)
        (dname, experiment_id) = os.path.split(dname)
        (dname, source_id) = os.path.split(dname)
        (dname, institution_id) = os.path.split(dname)
        (dname, activity_id) = os.path.split(dname)
        (prefix, mip_era) = os.path.split(dname)

        try:
            (sub_experiment_id, variant_label) = member_id.split('-')
        except ValueError:
            variant_label = member_id
            sub_experiment_id = None

        # TODO: prefix should be a member of this class ??
        res = {
            'mip_era': mip_era,
            'activity_id': activity_id,
            'institution_id': institution_id,
            'source_id': source_id,
            'experiment_id': experiment_id,
            'sub_experiment_id': sub_experiment_id,
            'variant_label': variant_label,
            'table_id': table_id,
            'variable_id': variable_id,
            'grid_label': grid_label,
            'version': version}
        self.set(**res)
        res["prefix"] = prefix
        return res


if __name__ == "__main__":
    import drs
    from pprint import pprint

    # w/o time_range
    d = drs.DRS(**drs.sample_attrs)
    print(d)
    print("dirname:", d.dirName())
    print("filename:", d.fileName())

    d = drs.DRS(**drs.sample_attrs_w_subexp)
    print(d)
    print("dirname:", d.dirName())
    print("filename:", d.fileName())

    # print(d)

    # attrs = drs.sample_attrs
    # # attrs.update({'table_id':'invalid'})
    # pprint(attrs)
    # d = drs.DRS(**attrs)
    # print(d)

    # print(d.fileName())
    # print(d.dirName())
    
