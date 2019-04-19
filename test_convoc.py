#!/usr/bin/env python3
# -*- 

from convoc import ConVoc
import unittest
import os


class ConVoc_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init01(self):
        os.environ['CVPATH'] = '.:./CMIP6_CVs/:$HOME:$HOME/CMIP6_CVs'
        ref = ['.', "$HOME"]
        ref = [os.path.expandvars(d) for d in ref]

        cvs = ConVoc()

        self.assertTrue(isinstance(cvs, ConVoc))



    def test_getCVPaths01(self):
        os.environ['CVPATH'] = '.:./CMIP6_CVs/:$HOME:$HOME/CMIP6_CVs'
        ref = ['.', '$HOME']
        ref = [os.path.expandvars(d) for d in ref]

        cvs = ConVoc()
        res = cvs.getCVPaths()

        self.assertEqual(ref, res)

    def test_getCVPaths02(self):
        os.environ['CVPATH'] = '/some/nonexistent/path'
        ref = []

        cvs = ConVoc()
        res = cvs.getCVPaths()

        self.assertEqual(ref, res)


    def test_getCVPaths11(self):
        cvpath = '.:./CMIP6_CVs/:$HOME:$HOME/CMIP6_CVs'
        ref = ['.', '$HOME']
        ref = [os.path.expandvars(d) for d in ref]

        cvs = ConVoc(cvpath)
        res = cvs.getCVPaths()

        self.assertEqual(ref, res)


    def test_getCV01(self):
        attr = 'activity_id'
        ref = 'CMIP DECK: 1pctCO2, abrupt4xCO2, amip, esm-piControl, esm-historical, historical, and piControl experiments'

        cvs = ConVoc()
        cv = cvs.getCV(attr)
        res = cv['CMIP']

        self.assertEqual(len(cv),24)
        self.assertEqual(ref, res)

    def test_getCV02(self):
        attr = 'invalid_id'

        cvs = ConVoc()
        cv = cvs.getCV(attr)
        self.assertTrue(cv is None)

    def test_checkCV01(self):
        attr = 'activity_id'
        value = 'CMIP'

        cvs = ConVoc()
        res = cvs.checkCV(value, attr)
        self.assertTrue(res)

    def test_checkCV02(self):
        attr = 'activity_id'
        value = 'invalid_value'

        cvs = ConVoc()
        res = cvs.checkCV(value, attr)
        self.assertFalse(res)



def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()


