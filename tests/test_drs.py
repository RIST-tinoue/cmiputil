from cmiputil import drs
import unittest
from os.path import dirname
from pathlib import Path

class test_DRS(unittest.TestCase):
    def setUp(self):
        self.ga = {
            'activity_id': 'CMIP',
            'experiment_id': 'piControl',
            'grid_label': 'gn',
            'institution_id': 'MIROC',
            'source_id': 'MIROC6',
            'table_id': 'Amon',
            'time_range': '320001-329912',
            'variable_id': 'tas',
            'variant_label': 'r1i1p1f1',
            'version': 'v20190308',
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

        self.fname = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn_185001-194912.nc"
        self.fname_wo_trange = "tas_Amon_MIROC6_piControl_r1i1p1f1_gn.nc"
        self.fname_w_subexp = (
            "rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker_s1950-r1i1p1f1_"
            "gr_192001-201412.nc")
        self.url = (
            "http://esgf.nci.org.au/thredds/fileServer/replica/CMIP6/CMIP/"
            "MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/"
            "tas_Amon_MIROC6_piControl_r1i1p1f1_gn_360001-369912.nc")

        self.url_w_subexp = (
            "http://vesg.ipsl.upmc.fr/thredds/fileServer/cmip6/DCPP/IPSL/"
            "IPSL-CM6A-LR/dcppC-pac-pacemaker/s1920-r1i1p1f1/Amon/rsdscs/"
            "gr/v20190110/rsdscs_Amon_IPSL-CM6A-LR_dcppC-pac-pacemaker_s1920-"
            "r1i1p1f1_gr_192001-201412.nc")

        pass

    def tearDown(self):
        pass

    def test_repr01(self):
        "repr() constructed from dict"
        ref = ("DRS("
               "activity_id='CMIP', experiment_id='piControl', "
               "grid_label='gn', institution_id='MIROC', "
               "mip_era='CMIP6', source_id='MIROC6', "
               "table_id='Amon', time_range='320001-329912', "
               "variable_id='tas', variant_label='r1i1p1f1', "
               "version='v20190308')")

        d0 = drs.DRS(**self.ga)
        res = repr(d0)
        self.assertEqual(ref, res)
        d1 = eval('drs.'+res)
        self.assertEqual(type(d0), type(d1))
        res = [(getattr(d0, k) == getattr(d1, k))
               for k in drs.DRS.requiredAttribs
               if k in dir(d0)]
        self.assertTrue(all(res))

    def test_repr02(self):
        "repr() constructed from dict with sub_experiment_id"
        ref = (
            "DRS(activity_id='DCPP', experiment_id='dcppC-atl-pacemaker', "
            "grid_label='gr', institution_id='IPSL', mip_era='CMIP6', "
            "source_id='IPSL-CM6A-LR', sub_experiment_id='s1950', "
            "table_id='Amon', time_range='192001-201412', "
            "variable_id='rsdscs', variant_label='r1i1p1f1', "
            "version='v20190110')")

        d0 = drs.DRS(**self.ga_w_sub)
        res = repr(d0)
        self.assertEqual(ref, res)
        d1 = eval('drs.'+res)
        self.assertEqual(d0, d1)


    def test_repr03(self):
        "repr() constructed from filename"
        ref = (
            "DRS(experiment_id='piControl', grid_label='gn', "
            "mip_era='CMIP6', source_id='MIROC6', table_id='Amon', "
            "time_range='185001-194912', variable_id='tas', "
            "variant_label='r1i1p1f1')")

        d0 = drs.DRS(filename=self.fname)
        res = repr(d0)
        self.assertEqual(ref, res)
        d1 = eval('drs.'+res)
        self.assertEqual(d0, d1)

    def test_str01(self):
        "str() constructed from dict"
        ref = ("activity_id: 'CMIP'\n"
               "experiment_id: 'piControl'\n"
               "grid_label: 'gn'\n"
               "institution_id: 'MIROC'\n"
               "mip_era: 'CMIP6'\n"
               "source_id: 'MIROC6'\n"
               "table_id: 'Amon'\n"
               "time_range: '320001-329912'\n"
               "variable_id: 'tas'\n"
               "variant_label: 'r1i1p1f1'\n"
               "version: 'v20190308'")
        d0 = drs.DRS(**self.ga)
        res = str(d0)
        self.assertEqual(ref, res)

    def test_str02(self):
        "str() constructed from dict with sub_experiment_id"
        ref = ("activity_id: 'DCPP'\n"
               "experiment_id: 'dcppC-atl-pacemaker'\n"
               "grid_label: 'gr'\n"
               "institution_id: 'IPSL'\n"
               "mip_era: 'CMIP6'\n"
               "source_id: 'IPSL-CM6A-LR'\n"
               "sub_experiment_id: 's1950'\n"
               "table_id: 'Amon'\n"
               "time_range: '192001-201412'\n"
               "variable_id: 'rsdscs'\n"
               "variant_label: 'r1i1p1f1'\n"
               "version: 'v20190110'")
        d0 = drs.DRS(**self.ga_w_sub)
        res = str(d0)
        self.assertEqual(ref, res)

    def test_str03(self):
        "str() constructed from filename"
        ref = (
            "activity_id: 'DCPP'\n"
            "experiment_id: 'dcppC-atl-pacemaker'\n"
            "grid_label: 'gr'\n"
            "institution_id: 'IPSL'\n"
            "mip_era: 'CMIP6'\n"
            "source_id: 'IPSL-CM6A-LR'\n"
            "sub_experiment_id: 's1950'\n"
            "table_id: 'Amon'\n"
            "time_range: '192001-201412'\n"
            "variable_id: 'rsdscs'\n"
            "variant_label: 'r1i1p1f1'\n"
            "version: 'v20190110'")
        d0 = drs.DRS(**self.ga_w_sub)
        res = str(d0)
        self.assertEqual(ref, res)

    def test_fileNameUseClass01(self):
        "Construct filename by class method."
        ref = Path('tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc')

        res = drs.DRS(**self.ga).fileName()
        self.assertEqual(ref, res)

    def test_fileNameUseClass11(self):
        "Construct filename by class method, with `time_range`."
        self.ga['time_range'] = '185001-194912'
        ref = Path('tas_Amon_MIROC6_piControl_r1i1p1f1_gn_185001-194912.nc')

        res = drs.DRS(**self.ga).fileName()

        self.assertEqual(ref, res)

    def test_fileNameUseClass21(self):
        "invalid attribute, expect AttributeError."
        ga = {k:v for k,v in self.ga.items()}
        ga['table_id'] = 'invalid'
        ref = Path('tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc')

        with self.assertRaises(AttributeError):
            res = drs.DRS(**ga).fileName(allow_asterisk=False)
            self.assertEqual(ref, res)

    def test_fileNameUseInstance01(self):
        "Construct filename by instance method, reusing one instance."
        variants = ['r1i1p1f1', 'r2i1p1f1', 'r3i1p1f1']
        refs = [
            Path('tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc'),
            Path('tas_Amon_MIROC6_piControl_r2i1p1f1_gn_320001-329912.nc'),
            Path('tas_Amon_MIROC6_piControl_r3i1p1f1_gn_320001-329912.nc')]

        d = drs.DRS(**self.ga)
        for v, ref in zip(variants, refs):
            d.set(variant_label=v)
            res = d.fileName()
            self.assertEqual(ref, res)

    def test_splitFileName01(self):
        "Split fname without `time_range`"
        fname = self.fname_wo_trange
        ref = {'experiment_id': 'piControl',
               'grid_label': 'gn',
               'source_id': 'MIROC6',
               'table_id': 'Amon',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1'}

        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_splitFileName02(self):
        "Split fname with `time_range`"
        fname = self.fname
        ref = {'experiment_id': 'piControl',
               'grid_label': 'gn',
               'source_id': 'MIROC6',
               'table_id': 'Amon',
               'time_range': '185001-194912',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1'}

        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_splitFileName03(self):
        "Split fname with `sub_experiment_id`"
        fname = self.fname_w_subexp

        ref = {'experiment_id': 'dcppC-atl-pacemaker',
               'grid_label': 'gr',
               'source_id': 'IPSL-CM6A-LR',
               'sub_experiment_id': 's1950',
               'table_id': 'Amon',
               'time_range': '192001-201412',
               'variable_id': 'rsdscs',
               'variant_label': 'r1i1p1f1'}

        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_dirNameUseClass01(self):
        "Construct dirname by class method."
        ref = Path("CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/"
               "Amon/tas/gn/v20190308")
        res = drs.DRS(**self.ga).dirName()

        self.assertEqual(ref, res)

    def test_dirNameUseClass02(self):
        "Construct dirname with sub_experiment_id by class method."

        ref = Path("CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/"
               "s1950-r1i1p1f1/Amon/rsdscs/gr/v20190110")
        res = drs.DRS(**self.ga_w_sub).dirName()

        self.assertEqual(ref, res)

    def test_dirNameUseInstance01(self):
        "Construct dirname by istance method, reusing one instance."
        ref = {
            'r1i1p1f1': Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/'
                             'Amon/tas/gn/v20190308'),
            'r2i1p1f1': Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r2i1p1f1/'
                             'Amon/tas/gn/v20190308'),
            'r3i1p1f1': Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r3i1p1f1/'
                             'Amon/tas/gn/v20190308')}

        d = drs.DRS(**self.ga)
        for v,r in ref.items():
            d.set(return_self=True, variant_label=v)
            res = d.dirName()
            self.assertEqual(r, res)

    def test_splitDirName01(self):
        "Split dirname without prefix"
        dname = ("CMIP6/CMIP/MIROC/MIROC6/piControl/"
                 "r1i1p1f1/Amon/tas/gn/v20190308")
        ref = {'activity_id': 'CMIP',
               'experiment_id': 'piControl',
               'grid_label': 'gn',
               'institution_id': 'MIROC',
               'mip_era': 'CMIP6',
               'source_id': 'MIROC6',
               'table_id': 'Amon',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1',
               'version': 'v20190308',
               'prefix': ''}
        res = drs.DRS().splitDirName(dname)

        self.assertEqual(ref, res)

    def test_splitDirName02(self):
        "Split dirname with prefix"
        dname = ("/work/data/CMIP6/CMIP6/CMIP/MIROC/MIROC6/piControl/"
                 "r1i1p1f1/Amon/tas/gn/v20190308")
        ref = {'activity_id': 'CMIP',
               'experiment_id': 'piControl',
               'grid_label': 'gn',
               'institution_id': 'MIROC',
               'mip_era': 'CMIP6',
               'prefix': '/work/data/CMIP6',
               'source_id': 'MIROC6',
               'table_id': 'Amon',
               'variable_id': 'tas',
               'variant_label': 'r1i1p1f1',
               'version': 'v20190308'}

        res = drs.DRS().splitDirName(dname)
        self.assertEqual(ref, res)

    def test_init_w_filename01(self):
        "Constructor with filename."
        fname = self.fname
        ref = {
            'experiment_id': 'piControl',
            'grid_label': 'gn',
            'member_id': 'r1i1p1f1',
            'mip_era': 'CMIP6',
            'source_id': 'MIROC6',
            'table_id': 'Amon',
            'time_range': '185001-194912',
            'variable_id': 'tas',
            'variant_label': 'r1i1p1f1'}

        d = drs.DRS(filename=fname)
        res = {a: getattr(d, a) for a in ref.keys()}
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            v = d.activity_id

    def test_getAttribs01(self):
        "construct from dict"
        ref = {}
        d = drs.DRS(**self.ga)
        ref = self.ga
        ref['mip_era'] = 'CMIP6'
        res = d.getAttribs()
        self.assertEqual(ref, res)

    def test_getAttribs02(self):
        "construct from filename"
        d = drs.DRS(**self.ga)
        ref = self.ga
        ref['mip_era'] = 'CMIP6'
        res = d.getAttribs()
        self.assertEqual(ref, res)

    def test_isValidPath01(self):
        "Valid URL without sub_experiment_id"
        res = drs.DRS().isValidPath(self.url)
        self.assertTrue(res)

    def test_isValidPath02(self):
        "Valid URL with sub_experiment_id"
        res = drs.DRS().isValidPath(self.url_w_subexp)
        self.assertTrue(res)

    def test_isValidPath03(self):
        "Valid filename without sub_experiment_id"
        res = drs.DRS().isValidPath(self.fname)
        self.assertTrue(res)

    def test_isValidPath04(self):
        "Valid filename with sub_experiment_id"
        res = drs.DRS().isValidPath(self.fname_w_subexp)
        self.assertTrue(res)

    def test_isValidPath05(self):
        "Valid dirname(-like) but forget directory=True, expect False"
        res = drs.DRS().isValidPath(dirname(self.url))
        self.assertFalse(res)

    def test_isValidPath06(self):
        "Valid dirname(-like)"
        res = drs.DRS().isValidPath(dirname(self.url), directory=True)
        self.assertTrue(res)

    def test_isValidPath07(self):
        "Valid dirname, separaterd==True"
        ref = ({'all': True},
               {'activity_id': True,
                'experiment_id': True,
                'grid_label': True,
                'institution_id': True,
                'mip_era': True,
                'source_id': True,
                'table_id': True,
                'variable_id': True,
                'variant_label': True,
                'version': True})

        res = drs.DRS().isValidPath(dirname(self.url),
                                    directory=True, separated=True)
        self.assertEqual(ref, res)

    def test_isValidPath08(self):
        "Valid URL with sub_experiment_id, separated is True"
        ref = ({'experiment_id': True,
                'grid_label': True,
                'source_id': True,
                'sub_experiment_id': True,
                'table_id': True,
                'time_range': True,
                'variable_id': True,
                'variant_label': True},
               {'activity_id': True,
                'experiment_id': True,
                'grid_label': True,
                'institution_id': True,
                'mip_era': True,
                'source_id': True,
                'sub_experiment_id': True,
                'table_id': True,
                'variable_id': True,
                'variant_label': True,
                'version': True})

        res = drs.DRS().isValidPath(self.url_w_subexp, separated=True)
        self.assertEqual(ref, res)

    def test_check_time_range(self):
        valid_values = [
            '1920-2012',
            '192001-201212',
            '19200101-20121231',
            '1920-2012-clim',
            '192001-201212-clim',
            '192001-clim-201212-clim',
            '19200101-20121231-clim']
        invalid_values = [
            None,
            "", 
            'hoge',
            '1920',
            'v1920',
            '19201-201209',
            '192001-20129',
            '1920011-2012121'
            '19200101-2012121'
            '19200101-20121201'
            '1920-2012_clim',
            '192001-201212-clima',
            '19200101-20121231-climatology']
        for v in valid_values:
            self.assertTrue(drs.DRS()._check_time_range(v))
        for v in invalid_values:
            self.assertFalse(drs.DRS()._check_time_range(v))

    def test_check_version(self):
        valid_values = [
            'v20190510',
            'v00000000']
        invalid_values = [
            'ver.1.0',
            '20190510',
            '2019',
            'vv20190510']
        for v in valid_values:
            self.assertTrue(drs.DRS()._check_version(v))
        for v in invalid_values:
            self.assertFalse(drs.DRS()._check_version(v))

    def test_check_variant_label(self):
        valid_values = [
            'r1i1p1f1',
            'r10i1p1f1']
        invalid_values = [
            'r1i1p1',
            'r1f1f1p1',
            'rXiYfZpM',
            'hoge',
            '1357']
        for v in valid_values:
            self.assertTrue(drs.DRS()._check_variant_label(v))
        for v in invalid_values:
            self.assertFalse(drs.DRS()._check_variant_label(v))


def main():
    unittest.main()


if __name__ == "__main__":
    main()
