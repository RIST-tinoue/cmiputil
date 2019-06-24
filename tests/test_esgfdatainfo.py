#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmiputil import esgfdatainfo
import unittest
import copy

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


keys = ['master_id', 'source_id', 'type']
vals = [managed_attribs[k] for k in keys]
elements = {k: managed_attribs[k] for k in keys}


class test_ESGFDataInfo(unittest.TestCase):
    def setUp(self):
        self.sample_attrs={}
        self.sample_attrs.update(sample_attrs)

        self.managed_attribs={}
        self.managed_attribs.update(managed_attribs)

        self.keys = copy.copy(keys)
        self.vals = copy.copy(vals)
        self.elements = {}
        self.elements.update(elements)

    def tearDown(self):
        pass

    def test_init00(self):
        "Test constructor"
        dinfo = esgfdatainfo.ESGFDataInfo()
        self.assertIsInstance(dinfo, esgfdatainfo.ESGFDataInfo)

    def test_init01(self):
        "Test constructor w/ real attributes"
        ref = self.managed_attribs
        dinfo = esgfdatainfo.ESGFDataInfo(self.sample_attrs)
        res = {a: getattr(dinfo, a) for a in self.managed_attribs.keys()}
        self.assertEqual(ref, res)

    def test_managedAttribs00(self):
        "@property method managed_attribs"
        ref = self.managed_attribs

        dinfo = esgfdatainfo.ESGFDataInfo(self.sample_attrs)
        res = dinfo.managedAttribs
        self.assertEqual(ref, res)


    def test_getattr(self):
        """test __getattr__()"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)
        for k in self.elements:
            self.assertEqual(self.elements[k], dinfo[k])
        with self.assertRaises(KeyError):
            res = dinfo['d']

    def test_setattr(self):
        """test __setattr__()"""
        ref = 'Amon'
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)

        dinfo['table_id'] = ref
        self.assertEqual(dinfo.table_id, ref)

        with self.assertRaises(TypeError):
            dinfo[1] = ref
        with self.assertRaises(TypeError):
            dinfo[True] = ref
        with self.assertRaises(TypeError):
            dinfo[(1,2)] = ref

    def test_str(self):
        """test __str__()"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)
        ref = str(self.elements)
        res = str(dinfo)
        self.assertEqual(ref, res)

        self.elements['d'] = (1,2)
        dinfo['d'] = (1,2)
        ref = str(self.elements)
        res = str(dinfo)
        self.assertEqual(ref, res)

    def test_delitem(self):
        """test __del_()"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)
        res = dinfo[self.keys[2]]
        self.assertEqual(res, self.vals[2])
        del dinfo[self.keys[2]]
        with self.assertRaises(KeyError):
            res = dinfo[self.keys[2]]
        with self.assertRaises(KeyError):
            del dinfo['d']

    def test_iter(self):
        """ test __iter__()"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)
        for k in dinfo:
            self.assertEqual(self.elements[k], dinfo[k])

    def test_len(self):
        """test __len__()"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)
        self.assertEqual(len(self.elements), len(dinfo))

    def test_update(self):
        """ test update()"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)
        update = {'c':False, 'd':(1,2)}
        self.elements.update(update)
        dinfo.update(update)

        for k in self.elements:
            self.assertEqual(self.elements[k], dinfo[k])
        self.assertEqual(type(dinfo), esgfdatainfo.ESGFDataInfo)
        self.assertEqual(type(self.elements), dict)

    def test_in(self):
        """ test in operator"""
        dinfo = esgfdatainfo.ESGFDataInfo(self.elements)

        self.assertTrue(('master_id' in dinfo))
        self.assertTrue(('source_id' in dinfo))
        self.assertTrue(('type' in dinfo))
        self.assertFalse(('id' in dinfo))



def main():
    unittest.main()


if __name__ == "__main__":
    main()
