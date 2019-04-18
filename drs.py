#!/usr/bin/env python3
#coding:utf-8
"""CMIP6 Data Reference Syntax (DRS):

(Excerpt from http://goo.gl/v1drZl)

Data Reference Syntax (DRS) components:

The DRS identifies experiments, simulations, ensembles of experiments, and
atomic datasets.  Some of the DRS components are used, for example,to construct
file names, directory structures, the further_info_url, and in facets of some
search tools.  The following components are needed for CMIP6 (along with their
CMIP5 counterparts):

activity_id*     (CMIP5: "activity")        see CMIP6_activity_id.json
institution_id   (CMIP5: "institute")       see CMIP6_institution_id.json
source_id        (CMIP5: "model")           see CMIP6_source_id.json
experiment_id    (CMIP5: "experiment")      see CMIP6_experiment_id.json
variable_id      (CMIP5: "variable name")   see data request
table_id         (CMIP5: "table_id")        see CMIP6_table_id.json
variant_label    (CMIP5: "ensemble member") construct from realization,
                                            initialization, physics, and
                                            forcing indices
version          (CMIP5: "version number")  indicating approximate date of
                                            model output file. (This is the
                                            only DRS element that is not stored
                                            as a global attribute.)

We need additional components in CMIP6 to accommodate the more complex
structure:

sub_experiment_id (set to "none" for most experiments)                                 see CMIP6_sub_experiment_id.json
grid_label        (needed to distinguish the same field stored on more than one grid)  see CMIP6_grid_label.json
mip_era           (needed to distinguish CMIP5 experiments and datasets from CMIP6.)   set to “CMIP6”
member_id         a compound construction from sub_experiment_id and variant_label     see below for further information

As in CMIP5, we also define additional DRS elements because they can be helpful
in providing data discovery services:

frequency     (CMIP5: "frequency")        see CMIP6_frequency.json
realm*        (CMIP5: "modeling realm")   see CMIP6_realm.json
product       (CMIP5: "product")          set to “model-output” in CMIP6
nominal_resolution                        see CMIP6_nominal_resolution.json and Appendix 2
source_type*                              see CMIP6_source_type.json

The DRS elements marked with an asterisk (*) are associated with
global attributes that may be space-separated lists of values.  Only
the first item in a list is recognized by the DRS, but in faceted
searches all listed items will be recognized.

File name template:

Before constructing file names and directory structures, it is useful to define
a member_id, which can be used to distinguish among different simulations
belonging to a root experiment.  The member_id is constructed from the
sub_experiment_id and variant_label using the following algorithm:


if sub_experiment_id = “none”
  member_id = <variant_label>
else
  member_id = <sub_experiment_id>-<variant_label>
endif

With this segment defined, the file name can be constructed consistent with the
following template:

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

Note that the last segment of the file name indicates the time-range spanned by
the data in the file, and is omitted when inappropriate (e.g., if a variable is
“fixed” for all time).  The format for this segment is as in CMIP5 (see
http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf):

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
import os.path



__author__ = 'T.Inoue'
__version__ = '0.9.0'
__date__ = '2019/04/16'

sample_attrs = {
    'activity_id': 'CMIP',
    'experiment_id': 'piControl',
    'grid_label': 'gn',
    'institution_id': 'MIROC',
    'source_id': 'MIROC6',
    'table_id': 'Amon',
    'time_range': None,
    'variable_id': 'tas',
    'variant_label': 'r1i1p1f1',
    'version': 'v20190308'}
sample_fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc"
sample_dname = "CMIP6/CMIP/MIROC/MIROC6/piControl/"\
               "r1i1p1f1/Amon/tas/gn/v20190308"

sample_attrs_w_subexp = {
    'activity_id': 'DCPP',
    'experiment_id': 'dcppC-atl-pacemaker',
    'grid_label': 'gr',
    'institution_id': 'IPSL',
    'source_id': 'IPSL-CM6A-LR',
    'sub_experiment_id': 's1920',
    'table_id': 'Amon',
    'time_range': '192001-201412',
    'variable_id': 'rsdscs',
    'variant_label': 'r1i1p1f1',
    'version': 'v20190110'}
sample_fname_w_subexp = 'rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker'\
                        '_s1920-r1i1p1f1_gr_192001-201412.nc'
sample_dname_w_subexp = 'CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/'\
                        's1920-r1i1p1f1/Amon/rsdscs/gr/v20190110'


class DRS:
    """This class contains attributes necessary to construct filename and
    directory name follows CMIP6 DRS (Data Reference Syntax).

    Class members are:
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

    def __init__(self, **kw):
        self.variable_id = None
        self.table_id = None
        self.source_id = None
        self.experiment_id = None
        self.grid_label = None
        self.time_range = None
        self.version = None
        self.sub_experiment_id = None
        self.variant_label = None
        self.member_id = None

        self.mip_era = 'CMIP6'
        self.activity_id = None
        self.institution_id = None
        self.source_id = None

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
            self.mip_era,
            self.activity_id,
            self.institution_id,
            self.variable_id,
            self.table_id,
            self.source_id,
            self.experiment_id,
            self.sub_experiment_id,
            self.variant_label,
            self.grid_label,
            self.time_range,
            self.version)

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
                "grid_label     : {!a}\n"
                "time_range     : {!a}\n"
                "version        : {!a}\n"
                "=================================\n")

        return tmpl.format(
            self.mip_era,
            self.activity_id,
            self.institution_id,
            self.variable_id,
            self.table_id,
            self.source_id,
            self.experiment_id,
            self.sub_experiment_id,
            self.variant_label,
            self.grid_label,
            self.time_range,
            self.version)

    def set(self, mip_era=None, activity_id=None, institution_id=None,
            variable_id=None, table_id=None, source_id=None,
            experiment_id=None, sub_experiment_id=None, variant_label=None,
            grid_label=None, time_range=None, version=None):

        if (mip_era):
            self.mip_era = mip_era
        if (activity_id):
            self.activity_id = activity_id
        if (institution_id):
            self.institution_id = institution_id
        if (variable_id):
            self.variable_id = variable_id
        if (table_id):
            self.table_id = table_id
        if (source_id):
            self.source_id = source_id
        if (experiment_id):
            self.experiment_id = experiment_id
        if (sub_experiment_id):
            self.sub_experiment_id = sub_experiment_id
        if (variant_label):
            self.variant_label = variant_label
        if (grid_label):
            self.grid_label = grid_label
        if (time_range):
            self.time_range = time_range
        if (version):
            self.version = version

        if self.sub_experiment_id is None:
            self.member_id = self.variant_label
        else:
            self.member_id = self.sub_experiment_id+'-'+self.variant_label

        return self

    def fileName(self):
        """
        Construct filename from instance members.
        """

        if (self.time_range is None):
            f = "{}_{}_{}_{}_{}_{}.nc".format(
                self.variable_id,
                self.table_id,
                self.source_id,
                self.experiment_id,
                self.member_id,
                self.grid_label
            )
        else:
            f = "{}_{}_{}_{}_{}_{}_{}.nc".format(
                self.variable_id,
                self.table_id,
                self.source_id,
                self.experiment_id,
                self.member_id,
                self.grid_label,
                self.time_range,
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

    d = drs.DRS(**drs.sample_attrs)
    print('attributes:')
    pprint(vars(d))
    print("dirname:", d.dirName())
    print("filename:", d.fileName())

    print(d)
