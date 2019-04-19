#!/usr/bin/env python3
# -*- 

import convoc
import unittest
import os


class ConVoc_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_getCVPaths01(self):
        os.environ['CVPATH'] = '.:./CMIP6_CVs/:$HOME:$HOME/CMIP6_CVs'
        ref = ['.', '$HOME']
        ref = [os.path.expandvars(d) for d in ref]

        res = convoc.getCVPaths()

        self.assertEqual(ref, res)

    def test_getCVPaths02(self):
        os.environ['CVPATH'] = '/some/nonexistent/path'
        ref = []

        res = convoc.getCVPaths()

        self.assertEqual(ref, res)


    def test_getCVPaths11(self):
        ref = ['.', '$HOME']
        ref = [os.path.expandvars(d) for d in ref]

        res = convoc.getCVPaths('.:./CMIP6_CVs/:$HOME:$HOME/CMIP6_CVs')

        self.assertEqual(ref, res)


    def test_getCV01(self):
        attr = 'activity_id'
        ref = 'CMIP DECK: 1pctCO2, abrupt4xCO2, amip, esm-piControl, esm-historical, historical, and piControl experiments'

        cv = convoc.getCV(attr)
        res = cv[attr]['CMIP']

        self.assertEqual(len(cv),2)
        self.assertEqual(len(cv[attr]),24)
        self.assertEqual(ref, res)

    def test_getCV02(self):
        attr = 'invalid_id'

        cv = convoc.getCV(attr)
        self.assertTrue(cv is None)

    def test_checkCV01(self):
        attr = 'activity_id'
        value = 'CMIP'

        res = convoc.checkCV(value, attr)
        self.assertTrue(res)

    def test_checkCV02(self):
        attr = 'activity_id'
        value = 'invalid_value'

        res = convoc.checkCV(value, attr)
        self.assertFalse(res)



def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()


