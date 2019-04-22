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
            cvs.getCVPaths()

    def test_01_getCVPaths01(self):
        "Set and get valid CVPATH."
        os.environ['CVPATH'] = self.cvpath_test
        ref = [os.path.expandvars(d) for d in self.cvlist_test]

        cvs = convoc.ConVoc()
        res = cvs.getCVPaths()
        self.assertEqual(ref, res)

    def test_01_getCVPaths11(self):
        "Give search path as an argument of constructor."
        cvpath = self.cvpath_test
        ref = [os.path.expandvars(d) for d in self.cvlist_test]

        cvs = convoc.ConVoc(cvpath)
        res = cvs.getCVPaths()
        self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_02_getCVAttr01(self):
        "Get actual table_id CV."
        attr = 'table_id'
        ref = ('CFday', 'Efx',  'IyrGre', 'SImon')

        cv = convoc.ConVoc().getCVAttr(attr)
        self.assertEqual(len(cv), 43)
        res = (cv[10], cv[20], cv[30], cv[40])
        self.assertEqual(ref, res)

    def test_02_getCVAttr02(self):
        "Invalid CV attribute, expect InvalidCVAttribError raises."
        attr = 'invalid_attr'

        cvs = convoc.ConVoc()
        with self.assertRaises(convoc.InvalidCVAttribError):
            cvs.getCVAttr(attr)

    def test_02_getCVAttr03(self):
        "Get several actual CVs sequently."

        cvs = convoc.ConVoc()
        cv = cvs.getCVAttr('activity_id')
        self.assertEqual(len(cv), 24)
        self.assertTrue('PAMIP' in cv)

        cv = cvs.getCVAttr('source_id')
        self.assertEqual(len(cv), 112)
        for k in ('MIROC6', 'NICAM16-7S', 'MRI-AGCM3-2'):
            self.assertTrue(k in cv)

        cv = cvs.getCVAttr('grid_label')
        self.assertEqual(len(cv), 45)
        for k in ('gn', 'gr', 'grz'):
            self.assertTrue(k in cv)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_03_checkCVKey01(self):
        "Check actual activity_id CV."
        attr = 'activity_id'
        key = 'CMIP'

        res = convoc.ConVoc().checkCVKey(key, attr)
        self.assertTrue(res)

    def test_03_checkCVKey02(self):
        "Invalid CV attribute."
        attr = 'invalid_attr'
        key = "CMIP"

        res = convoc.ConVoc().checkCVKey(key, attr)
        self.assertFalse(res)

    def test_03_checkCVKey03(self):
        "Invalid key for valid CV"
        attr = 'activity_id'
        key = 'invalid_key'

        res = convoc.ConVoc().checkCVKey(key, attr)
        self.assertFalse(res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getCVValue01(self):
        "Test getCVValue"
        attr = 'realm'
        key = 'atmos'
        ref = "Atmosphere"

        res = convoc.ConVoc().getCVValue(key, attr)
        self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getCVValue02(self):
        "Call getCVValue sequently"
        attr = 'realm'
        key = 'atmos'
        ref = "Atmosphere"

        res = convoc.ConVoc().getCVValue(key, attr)
        self.assertEqual(ref, res)

        attr = 'activity_id'
        key = 'OMIP'
        ref = "Ocean Model Intercomparison Project"

        res = convoc.ConVoc().getCVValue(key, attr)
        self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getCVValue03(self):
        "Invalid attribute, expect InvalidCVAttribError raiesd"
        attr = 'invalid_attr'
        key = 'OMIP'
        ref = "Ocean Model Intercomparison Project"

        with self.assertRaises(convoc.InvalidCVAttribError):
            res = convoc.ConVoc().getCVValue(key, attr)
            self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getCVValue04(self):
        "Invalid key, expect KeyError raiesd"
        attr = 'activity_id'
        key = 'invalid_key'
        ref = "Ocean Model Intercomparison Project"

        with self.assertRaises(KeyError):
            res = convoc.ConVoc().getCVValue(key, attr)
            self.assertEqual(ref, res)

    @unittest.skipUnless(os.environ.get('CVPATH'), 'since CVPATH not defined')
    def test_04_getCVValue05(self):
        "This CV has no values, just keys only"
        attr = 'nominal_resolution'
        key = '1 km'
        ref = None

        res = convoc.ConVoc().getCVValue(key, attr)
        self.assertEqual(ref, res)


def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()
