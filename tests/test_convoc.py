#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import convoc
import unittest
import os


class ConVoc_Test(unittest.TestCase):
    def setUp(self):
        self.cvpath_test = (
            '.:./non-existent-path/:'
            '$HOME:$HOME/non-existent-path')
        self.cvlist_test = ['.', '$HOME']
        try:
            self.cvpath_orig = os.environ['CVPATH']
        except KeyError:
            self.cvpath_orig = ""
        pass

    def tearDown(self):
        os.environ['CVPATH'] = self.cvpath_orig
        pass

    def test_00_init01(self):
        "Test constructor."
        os.environ['CVPATH'] = self.cvpath_test
        ref = [os.path.expandvars(d) for d in self.cvlist_test]

        cvs = convoc.ConVoc()
        self.assertTrue(isinstance(cvs, convoc.ConVoc))
        self.assertEqual(ref, cvs.cvpath)

    def test_00_init02(self):
        "Test constructor, invalid CVPATH, expect InvalidCVPathError."
        os.environ['CVPATH'] = '/some/nonexistent/path'

        with self.assertRaises(convoc.InvalidCVPathError):
            cvs = convoc.ConVoc()
            cvs.getSearchPath()

    def test_01_getSearchPath01(self):
        "Set and get valid CVPATH."
        os.environ['CVPATH'] = self.cvpath_test
        ref = [os.path.expandvars(d) for d in self.cvlist_test]

        cvs = convoc.ConVoc()
        res = cvs.getSearchPath()
        self.assertEqual(ref, res)

    def test_01_getSearchPath11(self):
        "Give search path as an argument of constructor."
        cvpath = self.cvpath_test
        ref = [os.path.expandvars(d) for d in self.cvlist_test]

        cvs = convoc.ConVoc(cvpath)
        res = cvs.getSearchPath()
        self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_02_getAttr01(self):
        "Get actual table_id CV."
        attr = 'table_id'
        ref = ('CFday', 'Efx',  'IyrGre', 'SImon')

        cv = convoc.ConVoc().getAttr(attr)
        self.assertEqual(len(cv), 43)
        res = (cv[10], cv[20], cv[30], cv[40])
        self.assertEqual(ref, res)

    def test_02_getAttr02(self):
        "Invalid CV attribute, expect InvalidCVAttribError raises."
        attr = 'invalid_attr'

        cvs = convoc.ConVoc()
        with self.assertRaises(convoc.InvalidCVAttribError):
            cvs.getAttr(attr)

    def test_02_getAttr03(self):
        "Get several actual CVs sequently."

        cvs = convoc.ConVoc()
        cv = cvs.getAttr('activity_id')
        self.assertEqual(len(cv), 24)
        self.assertTrue('PAMIP' in cv)

        cv = cvs.getAttr('source_id')
        self.assertEqual(len(cv), 112)
        for k in ('MIROC6', 'NICAM16-7S', 'MRI-AGCM3-2'):
            self.assertTrue(k in cv)

        cv = cvs.getAttr('grid_label')
        self.assertEqual(len(cv), 45)
        for k in ('gn', 'gr', 'grz'):
            self.assertTrue(k in cv)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_03_checkKey01(self):
        "Check actual activity_id CV."
        attr = 'activity_id'
        key = 'CMIP'

        res = convoc.ConVoc().checkKey(key, attr)
        self.assertTrue(res)

    def test_03_checkKey02(self):
        "Invalid CV attribute, expect InvalidCVAttribError"
        attr = 'invalid_attr'
        key = "CMIP"

        with self.assertRaises(convoc.InvalidCVAttribError):
            res = convoc.ConVoc().checkKey(key, attr)
            self.assertFalse(res)

    def test_03_checkKey03(self):
        "Invalid key for valid CV"
        attr = 'activity_id'
        key = 'invalid_key'

        res = convoc.ConVoc().checkKey(key, attr)
        self.assertFalse(res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getValue01(self):
        "Test getValue"
        attr = 'realm'
        key = 'atmos'
        ref = "Atmosphere"

        res = convoc.ConVoc().getValue(key, attr)
        self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
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

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getValue03(self):
        "Invalid attribute, expect InvalidCVAttribError raiesd"
        attr = 'invalid_attr'
        key = 'OMIP'
        ref = "Ocean Model Intercomparison Project"

        with self.assertRaises(convoc.InvalidCVAttribError):
            res = convoc.ConVoc().getValue(key, attr)
            self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getValue04(self):
        "Invalid key, expect KeyError raiesd"
        attr = 'activity_id'
        key = 'invalid_key'
        ref = "Ocean Model Intercomparison Project"

        with self.assertRaises(KeyError):
            res = convoc.ConVoc().getValue(key, attr)
            self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
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