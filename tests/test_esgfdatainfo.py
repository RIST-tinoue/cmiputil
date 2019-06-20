#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmiputil import esgfdatainfo
import unittest

sample_attrs = {
            '_timestamp': '2018-12-12T10:01:59.852Z',
            '_version_': 1619639842743779328,
            'access': ['HTTPServer', 'OPENDAP'],
            'activity_drs': ['CMIP'],
            'activity_id': ['CMIP'],
            'branch_method': ['standard'],
            'cf_standard_name': ['air_temperature'],
            'citation_url': ['http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.json'],
            'data_node': 'esgf-data2.diasjp.net',
            'data_specs_version': ['01.00.28'],
            'dataset_id_template_': ['%(mip_era)s.%(activity_drs)s.%(institution_id)s.%(source_id)s.%(experiment_id)s.%(member_id)s.%(table_id)s.%(variable_id)s.%(grid_label)s'],
            'datetime_start': '3200-01-16T12:00:00Z',
            'datetime_stop': '3999-12-16T12:00:00Z',
            'directory_format_template_': ['%(root)s/%(mip_era)s/%(activity_drs)s/%(institution_id)s/%(source_id)s/%(experiment_id)s/%(member_id)s/%(table_id)s/%(variable_id)s/%(grid_label)s/%(version)s'],
            'east_degrees': 358.59375,
            'experiment_id': ['piControl'],
            'experiment_title': ['pre-industrial control'],
            'frequency': ['mon'],
            'further_info_url': ['https://furtherinfo.es-doc.org/CMIP6.MIROC.MIROC6.piControl.none.r1i1p1f1'],
            'geo': ['ENVELOPE(-180.0, -1.40625, 88.927734, -88.927734)',
                    'ENVELOPE(0.0, 180.0, 88.927734, -88.927734)'],
            'geo_units': ['degrees_east'],
            'grid': ['native atmosphere T85 Gaussian grid'],
            'grid_label': ['gn'],
            'id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|esgf-data2.diasjp.net',
            'index_node': 'esgf-node.llnl.gov',
            'instance_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212',
            'institution_id': ['MIROC'],
            'latest': True,
            'master_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn',
            'member_id': ['r1i1p1f1'],
            'mip_era': ['CMIP6'],
            'model_cohort': ['Registered'],
            'nominal_resolution': ['250 km'],
            'north_degrees': 88.927734,
            'number_of_aggregations': 2,
            'number_of_files': 8,
            'pid': ['hdl:21.14100/0cc48997-f6e9-3e5f-a68e-e657f53a5dab'],
            'product': ['model-output'],
            'project': ['CMIP6'],
            'realm': ['atmos'],
            'replica': False,
            'retracted': False,
            'score': 1.0,
            'size': 694317642,
            'source_id': ['MIROC6'],
            'source_type': ['AOGCM', 'AER'],
            'south_degrees': -88.927734,
            'sub_experiment_id': ['none'],
            'table_id': ['Amon'],
            'title': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn',
            'type': 'Dataset',
            'url': ['http://esgf-data2.diasjp.net/thredds/catalog/esgcet/1/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.xml#CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|application/xml+thredds|THREDDS'],
            'variable': ['tas'],
            'variable_id': ['tas'],
            'variable_long_name': ['Near-Surface Air Temperature'],
            'variable_units': ['K'],
            'variant_label': ['r1i1p1f1'],
            'version': '20181212',
            'west_degrees': 0.0,
            'xlink': ['http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.json|Citation|citation',
                      'http://hdl.handle.net/hdl:21.14100/0cc48997-f6e9-3e5f-a68e-e657f53a5dab|PID|pid']}

managed_attribs = {
    'activity_drs': 'CMIP',
    'activity_id': 'CMIP',
    'data_node': 'esgf-data2.diasjp.net',
    'experiment_id': 'piControl',
    'grid_label': 'gn',
    'id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|esgf-data2.diasjp.net',
    'instance_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212',
    'institution_id': 'MIROC',
    'master_id': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn',
    'member_id': 'r1i1p1f1',
    'mip_era': 'CMIP6',
    'number_of_aggregations': 2,
    'number_of_files': 8,
    'source_id': 'MIROC6',
    'sub_experiment_id': 'none',
    'table_id': 'Amon',
    'title': 'CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn',
    'type': 'Dataset',
    'url': ['http://esgf-data2.diasjp.net/thredds/catalog/esgcet/1/CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212.xml#CMIP6.CMIP.MIROC.MIROC6.piControl.r1i1p1f1.Amon.tas.gn.v20181212|application/xml+thredds|THREDDS'],
    'variable_id': 'tas',
    'variant_label': 'r1i1p1f1',
    'version': 'v20181212'}


class set_ESGFDataInfo(unittest.TestCase):
    def setUp(self):
        self.sample_attrs={}
        self.sample_attrs.update(sample_attrs)
        
        self.managed_attribs={}
        self.managed_attribs.update(managed_attribs)

    def tearDown(self):
        pass

    def test_init00(self):
        "Test constructor"
        dinfo = esgfdatainfo.ESGFDataInfo()
        self.assertIsInstance(dinfo, esgfdatainfo.ESGFDataInfo)

    def test_init01(self):
        "Test constructor w/ real attributes"
        ref = self.managed_attribs
        dinfo = esgfdatainfo.ESGFDataInfo(**self.sample_attrs)
        res = {a: getattr(dinfo, a) for a in dinfo.managed_attributes}
        self.assertEqual(ref, res)

    def test_managedAttribs00(self):
        "@property method managed_attribs"
        ref = self.managed_attribs

        dinfo = esgfdatainfo.ESGFDataInfo(**self.sample_attrs)
        res = dinfo.managedAttribs
        self.assertEqual(ref, res)


def main():
    unittest.main()


if __name__ == "__main__":
    main()

    
