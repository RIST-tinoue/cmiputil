from drs import DRS
import unittest
from pprint import pprint
class DRS_Test(unittest.TestCase):
    def setUp(self):
        DRS.DEBUG = False
        self.ga = {
            'activity_id' : 'CMIP',
            'experiment_id':'piControl',
            'grid_label':'gn',
            'institution_id' : 'MIROC',
            'source_id': 'MIROC6',
            'table_id': 'Amon',
            'variable_id' : 'tas',
            'variant_label': 'r1i1p1f1',
            'version':'v20190308',
            }
        self.ga_w_sub = {
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
        # print(self.ga)
        pass

    def tearDown(self):
        pass

    @unittest.skip('To be implemented')
    def testRepl(self):
        d0 = DRS(**self.ga)
        line = repr(d0)
        # print(line)
        d1=eval(line)
        # print(type(d0))
        # print(type(d1))
        self.assertTrue(d0 == d1)


    @unittest.skip('To be implemented')
    def testStr(self):
        d0 = DRS(**self.ga)
        line = str(d0)
        print(line)


    def test_fileNameUseClass01(self):
        "Construct filename by class method."
        ref = 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc'

        res = DRS(**self.ga).fileName()

        self.assertEqual(ref, res)


    def test_fileNameUseClass11(self):
        "Construct filename by class method, with `time_range`."
        self.ga['time_range'] = '185001-194912'
        ref = 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_185001-194912.nc'

        res = DRS(**self.ga).fileName()

        self.assertEqual(ref, res)


    def test_fileNameUseClass21(self):
        "invalid attribute, expect AttributeError."
        self.ga['table_id'] = 'invalid'
        ref = 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_185001-194912.nc'

        with self.assertRaises(AttributeError):
            res = DRS(**self.ga).fileName()
            self.assertEqual(ref, res)



    def test_fileNameUseInstance01(self):
        "Construct filename by instance method, reusing one instance."
        variants = ['r1i1p1f1', 'r2i1p1f1', 'r3i1p1f1']
        ref = ['tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc',
               'tas_Amon_MIROC6_piControl_r2i1p1f1_gn.nc',
               'tas_Amon_MIROC6_piControl_r3i1p1f1_gn.nc']

        drs = DRS(**self.ga)
        res = [drs.set(variant_label=v).fileName()
               for v in variants]

        self.assertEqual(ref, res)



    def test_splitFileName01(self):
        "Split fname without `time_range`"
        fname = 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc'
        ref = {'experiment_id': 'piControl',
               'grid_label': 'gn',
               'source_id': 'MIROC6',
               'sub_experiment_id': None,
               'table_id': 'Amon',
               'time_range': None,
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1'}

        res = DRS().splitFileName(fname)
        # pprint(res)
        self.assertEqual(ref, res)


    def test_splitFileName02(self):
        "Split fname with `time_range`"
        fname = 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_185001-194912.nc'
        ref = {'experiment_id': 'piControl',
               'grid_label': 'gn',
               'source_id': 'MIROC6',
               'sub_experiment_id': None,
               'table_id': 'Amon',
               'time_range': '185001-194912',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1'}

        res = DRS().splitFileName(fname)
        # pprint(res)
        self.assertEqual(ref, res)


    def test_splitFileName03(self):
        "Split fname with `sub_experiment_id`"
        fname = 'rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker_s1950-r1i1p1f1_gr_192001-201412.nc'
        ref = {'experiment_id': 'dcppC-atl-pacemaker',
               'grid_label': 'gr',
               'source_id': 'IPSL-CM6A-LR',
               'sub_experiment_id': 's1950',
               'table_id': 'Amon',
               'time_range': '192001-201412',
               'variable_id': 'rsdscs',
               'variant_label': 'r1i1p1f1'}

        res = DRS().splitFileName(fname)
        # pprint(res)
        self.assertEqual(ref, res)



    def test_dirNameUseClass01(self):
        "Construct dirname by class method."
        ref = "CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20190308"
        res = DRS(**self.ga).dirName()

        self.assertEqual(ref, res)


    def test_dirNameUseClass02(self):
        "Construct dirname with sub_experiment_id by class method."

        ref = "CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/s1950-r1i1p1f1/Amon/rsdscs/gr/v20190110"
        res = DRS(**self.ga_w_sub).dirName()

        self.assertEqual(ref, res)


    def test_dirNameUseInstance01(self):
        "Construct dirname by istance method, reusing one instance."
        variants = ['r1i1p1f1', 'r2i1p1f1', 'r3i1p1f1']
        ref = ['CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20190308',
               'CMIP6/CMIP/MIROC/MIROC6/piControl/r2i1p1f1/Amon/tas/gn/v20190308',
               'CMIP6/CMIP/MIROC/MIROC6/piControl/r3i1p1f1/Amon/tas/gn/v20190308']

        drs = DRS(**self.ga)
        res = [drs.set(variant_label=v).dirName()
               for v in variants]

        self.assertEqual(ref, res)


    def test_splitDirName01(self):
        "Split dirname without prefix"
        dname = 'CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20190308'
        ref = {'activity_id': 'CMIP',
               'experiment_id': 'piControl',
               'grid_label': 'gn',
               'institution_id': 'MIROC',
               'mip_era': 'CMIP6',
               'source_id': 'MIROC6',
               'sub_experiment_id': None,
               'table_id': 'Amon',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1',
               'version': 'v20190308',
               'prefix': '' }
        res = DRS().splitDirName(dname)

        self.assertEqual(ref, res)


    def test_splitDirName02(self):
        "Split dirname with prefix"
        dname = '/work/data/CMIP6/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20190308'
        ref = {'activity_id': 'CMIP',
               'experiment_id': 'piControl',
               'grid_label': 'gn',
               'institution_id': 'MIROC',
               'mip_era': 'CMIP6',
               'prefix': '/work/data/CMIP6',
               'source_id': 'MIROC6',
               'sub_experiment_id': None,
               'table_id': 'Amon',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1',
               'version': 'v20190308'}

        res = DRS().splitDirName(dname)
        self.assertEqual(ref, res)

        
def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()

    
