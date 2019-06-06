#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmiputil import convoc, config
import unittest
from pathlib import Path
import os
from tempfile import NamedTemporaryFile

class test_ConVoc(unittest.TestCase):
    def setUp(self):
        self.cvpath_test = (
            '.:./non-existent-path/:'
            '$HOME:$HOME/non-existent-path')
        self.cvlist_test = ['.', '$HOME']

    def tearDown(self):
        pass

    def test_00_init01(self):
        "Test constructor."
        cvs = convoc.ConVoc()
        self.assertIsInstance(cvs, convoc.ConVoc)

    def test_00_init02(self):
        "Give search path as an argument of constructor."
        ref = [Path(os.path.expandvars(d)) for d in self.cvlist_test]
        cvs = convoc.ConVoc(paths=self.cvpath_test)
        res = cvs.getSearchPath()
        self.assertEqual(ref, res)

    def test_00_init03(self):
        "Give conffile as an argument of constructor."
        ref = [Path(os.path.expandvars(d)) for d in self.cvlist_test]
        configlines = "\n".join((
            '[ConVoc]',
            f'cmip6_cvs_dir = {self.cvpath_test}'
            '\n',
            ))
        conffile = Path('/tmp/cmiputil.conf')
        conffile.write_text(configlines)
        cvs = convoc.ConVoc(conffile=conffile)
        res = cvs.getSearchPath()
        self.assertEqual(ref, res)

    def test_00_init04(self):
        "Give invalid search path, expect InvalidCVPathError."
        with self.assertRaises(convoc.InvalidCVPathError):
            cvs = convoc.ConVoc(paths='/some/non-existent/invalid/path')

    def test_00_init05(self):
        "Give conffile with invalid path, expect InvalidCVPathError."
        configlines = "\n".join((
            '[ConVoc]',
            'cmip6_cvs_dir = /some/nonexistent/path'
            '\n',
            ))
        conffile = Path('/tmp/cmiputil.conf')
        conffile.write_text(configlines)
        with self.assertRaises(convoc.InvalidCVPathError):
            cvs = convoc.ConVoc(conffile=conffile)

    def test_02_getAttrib01(self):
        "Get actual table_id CV."
        attr = 'table_id'
        ref = ('CFday', 'Efx',  'IyrGre', 'SImon')
        cv = convoc.ConVoc().getAttrib(attr)
        self.assertEqual(len(cv), 43)
        res = (cv[10], cv[20], cv[30], cv[40])
        self.assertEqual(ref, res)

    def test_02_getAttrib02(self):
        "Invalid CV attribute, expect InvalidCVAttribError raises."
        attr = 'invalid_attr'
        cvs = convoc.ConVoc()
        with self.assertRaises(convoc.InvalidCVAttribError):
            cvs.getAttrib(attr)

    def test_02_getAttrib03(self):
        "Get several actual CVs sequently."
        cvs = convoc.ConVoc()
        cv = cvs.getAttrib('activity_id')
        for k in ('PAMIP', 'C4MIP', 'LS3MIP'):
            self.assertIn(k, cv)
        cv = cvs.getAttrib('source_id')
        for k in ('MIROC6', 'NICAM16-7S', 'MRI-AGCM3-2'):
            self.assertIn(k, cv)
        cv = cvs.getAttrib('grid_label')
        for k in ('gn', 'gr', 'grz'):
            self.assertIn(k, cv)

    def test_03_isValidValueForAttr01(self):
        "Check actual activity_id CV."
        attr = 'activity_id'
        key = 'CMIP'
        res = convoc.ConVoc().isValidValueForAttr(key, attr)
        self.assertTrue(res)

    def test_03_isValidValueForAttr02(self):
        "Invalid CV attribute, expect InvalidCVAttribError"
        attr = 'invalid_attr'
        key = "CMIP"
        with self.assertRaises(convoc.InvalidCVAttribError):
            res = convoc.ConVoc().isValidValueForAttr(key, attr)
            self.assertFalse(res)

    def test_03_isValidValueForAttr03(self):
        "Invalid key for valid CV"
        attr = 'activity_id'
        key = 'invalid_key'
        res = convoc.ConVoc().isValidValueForAttr(key, attr)
        self.assertFalse(res)

    def test_04_getValue01(self):
        "Test getValue"
        attr = 'realm'
        key = 'atmos'
        ref = "Atmosphere"
        res = convoc.ConVoc().getValue(key, attr)
        self.assertEqual(ref, res)

    def test_04_getValue02(self):
        "Call getValue sequently"
        attr = 'realm'
        key = 'atmos'
        ref = "Atmosphere"
        res = convoc.ConVoc().getValue(key, attr)
        self.assertEqual(ref, res)
        attr = 'activity_id'
        key = 'OMIP'
        ref = "Ocean Model Intercomparison Project"
        res = convoc.ConVoc().getValue(key, attr)
        self.assertEqual(ref, res)

    def test_04_getValue03(self):
        "Invalid attribute, expect InvalidCVAttribError raiesd"
        attr = 'invalid_attr'
        key = 'OMIP'
        ref = "Ocean Model Intercomparison Project"
        with self.assertRaises(convoc.InvalidCVAttribError):
            res = convoc.ConVoc().getValue(key, attr)
            self.assertEqual(ref, res)

    def test_04_getValue04(self):
        "Invalid key, expect KeyError raiesd"
        attr = 'activity_id'
        key = 'invalid_key'
        ref = "Ocean Model Intercomparison Project"
        with self.assertRaises(KeyError):
            res = convoc.ConVoc().getValue(key, attr)
            self.assertEqual(ref, res)

    def test_04_getValue05(self):
        "This CV has no values, just keys only"
        attr = 'nominal_resolution'
        key = '1 km'
        ref = None
        res = convoc.ConVoc().getValue(key, attr)
        self.assertEqual(ref, res)


def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()
