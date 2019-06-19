#!/usr/bin/env python3
"""
Manage ESGF dataset info.

Attributes are collected from ESGF RESTful API search result and
OPeNDAP Catalog, which are not in datafile global attributes.

"""

from pprint import pprint


__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190619'
__date__ = '2019/06/19'


class ESGFDataInfo():
    """
    Info of ESGF dataset.

    Collect info from ESGF RESTful API search result and OPeNDAP catalog.


    Example:
    >>> import urllib3
    >>> from cmiputil import esgfdatainfo
    >>> keywords = {
    ... 'distrib':'true',
    ... 'type':'Dataset',
    ... 'format':r'application/solr+json',
    ... 'offset':0,
    ... 'replica':'False'}
    >>> params = {
    ... 'experiment_id':'piControl',
    ... 'variable_id':'tas',
    ... 'table_id':'Amon',
    ... 'source_id':'BCC-CSM2-MR'}
    >>> base_url = 'http://esgf-node.llnl.gov/esg-search/' 'search'
    >>> params.update(keywords)
    >>> http = urllib3.PoolManager()
    >>> r = http.request('GET', base_url, fields=params)
    >>> result = json.loads(r.data.decode())
    >>> attrs = result['response']['docs'][0]
    >>> dinfo = esgfdatainfo.ESGFDataInfo(**attrs)
    >>> dinfo.id
    'CMIP6.CMIP.BCC.BCC-CSM2-MR.piControl.r1i1p1f1.Amon.tas.gn.v20181016|cmip.bcc.cma.cn'
    """

    _debug = False

    @classmethod
    def _enable_debug(cls):
        cls._debug = True

    @classmethod
    def _disable_debug(cls):
        cls._debug = True

    # @property
    # def debug(cls):
    #     return cls._debug

    managed_attributes = [
        'data_node',
        # 'dataset_id',
        'id',
        'instance_id',
        'master_id',
        'number_of_aggregations',
        'number_of_files',
        'title',
        'type',
        'url',
        'version',
        'mip_era',
        'activity_drs',
        'activity_id',
        'institution_id',
        'source_id',
        'experiment_id',
        'member_id',
        'table_id',
        'variable_id',
        'grid_label',
        'sub_experiment_id'
    ]


    def __init__(self, **attrs):
        self.set(**attrs)

        if self._debug:
            print('dbg:esgfdatainfo.ESGFDataInfo():')
            pprint(vars(self))

    def set(self, **argv):
        attribs = {a: argv[a] for a in argv
                   if a in self.managed_attributes}
        for a,v in attribs.items():
            setattr(self, a, v)

    @property
    def managedAttribs(self):
        return {a: getattr(self, a) for a in self.managed_attributes}



if (__name__ == '__main__'):
    import doctest
    doctest.testmod()




### type='Dataset'
# {'_timestamp': '2018-12-12T10:01:59.852Z',
#  '_version_': 1619639842743779328,
#  'access': ['HTTPServer', 'OPENDAP'],
#  'activity_drs': ['CMIP'],
#  'activity_id': ['CMIP'],
#  'branch_method': ['standard'],
#  'cf_standard_name': ['air_temperature'],
#  'citation_url': ['http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.json'],
#  'data_node': 'esgf-data2.diasjp.net',
#  'data_specs_version': ['01.00.28'],
#  'dataset_id_template_': ['%(mip_era)s.%(activity_drs)s.%(institution_id)s.%(source_id)s.%(experiment_id)s.%(member_id)s.%(table_id)s.%(variable_id)s.%(grid_label)s'],
#  'datetime_start': '3200-01-16T12:00:00Z',
#  'datetime_stop': '3999-12-16T12:00:00Z',
#  'directory_format_template_': ['%(root)s/%(mip_era)s/%(activity_drs)s/%(institution_id)s/%(source_id)s/%(experiment_id)s/%(member_id)s/%(table_id)s/%(variable_id)s/%(grid_label)s/%(version)s'],
#  'east_degrees': 358.59375,
#  'experiment_id': ['piControl'],
#  'experiment_title': ['pre-industrial control'],
#  'frequency': ['mon'],
#  'further_info_url': ['https://furtherinfo.es-doc.org/CMIP6.MIROC.MIROC6.piControl.none.r1i1p1f1'],
#  'geo': ['ENVELOPE(-180.0, -1.40625, 88.927734, -88.927734)',
#          'ENVELOPE(0.0, 180.0, 88.927734, -88.927734)'],
#  'geo_units': ['degrees_east'],
#  'grid': ['native atmosphere T85 Gaussian grid'],
#  'grid_label': ['gn'],
#  'id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|esgf-data2.diasjp.net',
#  'index_node': 'esgf-node.llnl.gov',
#  'instance_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212',
#  'institution_id': ['MIROC'],
#  'latest': True,
#  'master_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn',
#  'member_id': ['r1i1p1f1'],
#  'mip_era': ['CMIP6'],
#  'model_cohort': ['Registered'],
#  'nominal_resolution': ['250 km'],
#  'north_degrees': 88.927734,
#  'number_of_aggregations': 2,
#  'number_of_files': 8,
#  'pid': ['hdl:21.14100/0cc48997-f6e9-3e5f-a68e-e657f53a5dab'],
#  'product': ['model-output'],
#  'project': ['CMIP6'],
#  'realm': ['atmos'],
#  'replica': False,
#  'retracted': False,
#  'score': 1.0,
#  'size': 694317642,
#  'source_id': ['MIROC6'],
#  'source_type': ['AOGCM', 'AER'],
#  'south_degrees': -88.927734,
#  'sub_experiment_id': ['none'],
#  'table_id': ['Amon'],
#  'title': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn',
#  'type': 'Dataset',
#  'url': ['http://esgf-data2.diasjp.net/thredds/catalog/esgcet/1/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.xml#CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|application/xml+thredds|THREDDS'],
#  'variable': ['tas'],
#  'variable_id': ['tas'],
#  'variable_long_name': ['Near-Surface Air Temperature'],
#  'variable_units': ['K'],
#  'variant_label': ['r1i1p1f1'],
#  'version': '20181212',
#  'west_degrees': 0.0,
#  'xlink': ['http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.json|Citation|citation',
#            'http://hdl.handle.net/hdl:21.14100/0cc48997-f6e9-3e5f-a68e-e657f53a5dab|PID|pid']}



##### type='File'
# {'_timestamp': '2019-02-12T21:44:03.856Z',
#  '_version_': 1625301024879149056,
#  'activity_drs': ['CMIP'],
#  'activity_id': ['CMIP'],
#  'branch_method': ['standard'],
#  'cf_standard_name': ['air_temperature'],
#  'checksum': ['a60588c68852a36c6c8cb3f68cf497d73ca0b036b21703424e67e402c0ec79f1'],
#  'checksum_type': ['SHA256'],
#  'citation_url': ['http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.json'],
#  'data_node': 'aims3.llnl.gov',
#  'data_specs_version': ['01.00.28'],
#  'dataset_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|aims3.llnl.gov',
#  'dataset_id_template_': ['%(mip_era)s.%(activity_drs)s.%(institution_id)s.%(source_id)s.%(experiment_id)s.%(member_id)s.%(table_id)s.%(variable_id)s.%(grid_label)s'],
#  'directory_format_template_': ['%(root)s/%(mip_era)s/%(activity_drs)s/%(institution_id)s/%(source_id)s/%(experiment_id)s/%(member_id)s/%(table_id)s/%(variable_id)s/%(grid_label)s/%(version)s'],
#  'experiment_id': ['piControl'],
#  'experiment_title': ['pre-industrial control'],
#  'frequency': ['mon'],
#  'further_info_url': ['https://furtherinfo.es-doc.org/CMIP6.MIROC.MIROC6.piControl.none.r1i1p1f1'],
#  'grid': ['native atmosphere T85 Gaussian grid'],
#  'grid_label': ['gn'],
#  'id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc|aims3.llnl.gov',
#  'index_node': 'esgf-node.llnl.gov',
#  'instance_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc',
#  'institution_id': ['MIROC'],
#  'latest': True,
#  'master_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc',
#  'member_id': ['r1i1p1f1'],
#  'mip_era': ['CMIP6'],
#  'model_cohort': ['Registered'],
#  'nominal_resolution': ['250 km'],
#  'pid': ['hdl:21.14100/0cc48997-f6e9-3e5f-a68e-e657f53a5dab'],
#  'product': ['model-output'],
#  'project': ['CMIP6'],
#  'realm': ['atmos'],
#  'replica': True,
#  'retracted': False,
#  'score': 1.0,
#  'size': 86784688,
#  'source_id': ['MIROC6'],
#  'source_type': ['AOGCM', 'AER'],
#  'sub_experiment_id': ['none'],
#  'table_id': ['Amon'],
#  'timestamp': '2018-11-30T09:02:16Z',
#  'title': 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc',
#  'tracking_id': ['hdl:21.14100/bac3aaa1-4605-4758-84a1-b54bc860614c'],
#  'type': 'File',
#  'url': ['http://aims3.llnl.gov/thredds/fileServer/css03_data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc|application/netcdf|HTTPServer',
#          'http://aims3.llnl.gov/thredds/dodsC/css03_data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc.html|application/opendap-html|OPENDAP',
#          'gsiftp://aimsdtn3.llnl.gov:2811//css03_data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc|application/gridftp|GridFTP',
#          'globus:415a6320-e49c-11e5-9798-22000b9da45e/css03_data/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc|Globus|Globus'],
#  'variable': ['tas'],
#  'variable_id': ['tas'],
#  'variable_long_name': ['Near-Surface Air Temperature'],
#  'variable_units': ['K'],
#  'variant_label': ['r1i1p1f1'],
#  'version': '1'}


