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
            'version': 'v20181212',
            }
        self.fname = 'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_185001-194912.nc'
        self.dname = 'CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212'

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
        self.fname_w_subexp = (
            'rsdscs_Amon_IPSL-CM6A-LR_dcppC-atl-pacemaker_s1950-r1i1p1f1_'
            'gr_192001-201412.nc')
        self.dname_w_subexp = (
            'CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/'
            's1950-r1i1p1f1/Amon/rsdscs/gr/v20190110')

        self.ga_no_trange ={
            'activity_id': 'CMIP',
            'experiment_id': 'historical',
            'grid_label': 'gn',
            'institution_id': 'MIROC',
            'mip_era': 'CMIP6',
            'prefix': '',
            'source_id': 'MIROC6',
            'table_id': 'fx',
            'variable_id': 'areacella',
            'variant_label': 'r1i1p1f1',
            'version': 'v20190311'}
        self.fname_no_trange = 'areacella_fx_MIROC6_historical_r1i1p1f1_gn.nc'

        self.url = (
            'http://esgf.nci.org.au/thredds/fileServer/replica/CMIP6/CMIP/'
            'MIROC/MIROC6/piControl/r1i1p1f1/Amon/tas/gn/v20181212/'
            'tas_Amon_MIROC6_piControl_r1i1p1f1_gn_360001-369912.nc')

        self.url_w_subexp = (
            'http://vesg.ipsl.upmc.fr/thredds/fileServer/cmip6/DCPP/IPSL/'
            'IPSL-CM6A-LR/dcppC-pac-pacemaker/s1920-r1i1p1f1/Amon/rsdscs/'
            'gr/v20190110/rsdscs_Amon_IPSL-CM6A-LR_dcppC-pac-pacemaker_s1920-'
            'r1i1p1f1_gr_192001-201412.nc')

        pass

    def tearDown(self):
        pass

    def test_init_w_filename01(self):
        "Constructor with filename."
        fname = self.fname
        ref = {'experiment_id': 'piControl', 'grid_label': 'gn',
               'mip_era': 'CMIP6', 'source_id': 'MIROC6', 'table_id':
               'Amon', 'time_range': '185001-194912', 'variable_id':
               'tas', 'variant_label': 'r1i1p1f1'}
        d = drs.DRS(filename=fname)
        res = {a: getattr(d, a)
               for a in d.requiredAttribs
               if hasattr(d, a)}
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            print(d.sub_experiment_id)

    def test_init_w_dirname01(self):
        "Constructor with dirname."
        dname = self.dname
        ref = {'activity_id': 'CMIP', 'experiment_id': 'piControl',
               'grid_label': 'gn', 'institution_id': 'MIROC',
               'mip_era': 'CMIP6', 'source_id': 'MIROC6', 'table_id':
               'Amon', 'variable_id': 'tas', 'variant_label':
               'r1i1p1f1', 'version': 'v20181212'}
        d = drs.DRS(dirname=dname)
        res = {a: getattr(d, a)
               for a in d.requiredAttribs
               if hasattr(d, a)}
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            print(d.sub_experiment_id)

    def test_repr01(self):
        "repr() constructed from dict"
        ref = ("DRS("
               "activity_id='CMIP', experiment_id='piControl', "
               "grid_label='gn', institution_id='MIROC', "
               "mip_era='CMIP6', source_id='MIROC6', "
               "table_id='Amon', time_range='320001-329912', "
               "variable_id='tas', variant_label='r1i1p1f1', "
               "version='v20181212')")

        d0 = drs.DRS(**self.ga)
        res = repr(d0)
        self.assertEqual(ref, res)
        d1 = eval('drs.'+res)
        self.assertEqual(d0, d1)


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


    def test_repr11(self):
        "repr() with multiple values"
        ref = ("DRS("
               "activity_id='CMIP', experiment_id='amip, piControl', "
               "grid_label='gn', institution_id='MIROC', "
               "mip_era='CMIP6', source_id='MIROC6', "
               "table_id='Amon', time_range='320001-329912', "
               "variable_id='tas', variant_label='r1i1p1f1', "
               "version='v20181212')")
        attrs = {a: v for a,v in self.ga.items()}
        attrs.update({'experiment_id': 'amip,piControl'})

        d0 = drs.DRS(**attrs)
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
               "version: 'v20181212'")
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

    def test_str11(self):
        "str() with multiple values"
        ref = ("activity_id: 'CMIP'\n"
               "experiment_id: ['amip', 'piControl']\n"
               "grid_label: 'gn'\n"
               "institution_id: 'MIROC'\n"
               "mip_era: 'CMIP6'\n"
               "source_id: 'MIROC6'\n"
               "table_id: 'Amon'\n"
               "time_range: '320001-329912'\n"
               "variable_id: 'tas'\n"
               "variant_label: 'r1i1p1f1'\n"
               "version: 'v20181212'")
        attrs = {a: v for a,v in self.ga.items()}
        attrs.update({'experiment_id': 'amip,piControl'})
        d0 = drs.DRS(**attrs)
        res = str(d0)
        self.assertEqual(ref, res)

    def test_fileNameUseClass01(self):
        "Construct filename by class method."
        ref = Path('tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc')
        res = drs.DRS(**self.ga).fileName()
        self.assertEqual(ref, res)

    def test_fileNameUseClass02(self):
        "Construct filename by class method, without `time_range`."
        attrs = {a: v for a,v in self.ga_no_trange.items()}
        ref = Path(self.fname_no_trange)
        res = drs.DRS(**attrs).fileName()
        self.assertEqual(ref, res)

    def test_fileNameUseClass03(self):
        "fileName() with missing attribute"
        attrs = {k:v for k,v in self.ga.items()}
        del attrs['table_id']
        ref = Path('tas_*_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc')
        res = drs.DRS(**attrs).fileName()
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            res = drs.DRS(**attrs).fileName(allow_asterisk=False)

    def test_fileNameUseClass04(self):
        "fileName() with invalid value for valid attribute"
        attrs = {k:v for k,v in self.ga.items()}
        attrs['table_id'] = 'invalid'
        ref = Path('tas_*_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc')
        res = drs.DRS(**attrs).fileName()
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            res = drs.DRS(**attrs).fileName(allow_asterisk=False)

    def test_fileNameUseInstance01(self):
        "Construct filename by instance method, reusing one instance."
        variants = ['r1i1p1f1', 'r2i1p1f1', 'r3i1p1f1']
        refs = [
            Path('tas_Amon_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc'),
            Path('tas_Amon_MIROC6_piControl_r2i1p1f1_gn_320001-329912.nc'),
            Path('tas_Amon_MIROC6_piControl_r3i1p1f1_gn_320001-329912.nc')]
        d = drs.DRS(**self.ga)
        for v, r in zip(variants, refs):
            d.set(variant_label=v)
            res = d.fileName()
            self.assertEqual(r, res)

    def test_splitFileName01(self):
        "Split fname without `time_range`"
        fname = self.fname_no_trange
        ref = {'experiment_id': 'historical', 'grid_label': 'gn',
               'source_id': 'MIROC6', 'table_id': 'fx', 'variable_id':
               'areacella', 'variant_label': 'r1i1p1f1'}
        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_splitFileName02(self):
        "Split fname with `time_range`"
        fname = self.fname
        ref = {'experiment_id': 'piControl', 'grid_label': 'gn',
               'source_id': 'MIROC6', 'table_id': 'Amon',
               'time_range': '185001-194912', 'variable_id': 'tas',
               'variant_label': 'r1i1p1f1'}
        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_splitFileName03(self):
        "Split fname with `sub_experiment_id`"
        fname = self.fname_w_subexp
        ref = {'experiment_id': 'dcppC-atl-pacemaker', 'grid_label':
               'gr', 'source_id': 'IPSL-CM6A-LR', 'sub_experiment_id':
               's1950', 'table_id': 'Amon', 'time_range':
               '192001-201412', 'variable_id': 'rsdscs',
               'variant_label': 'r1i1p1f1'}
        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_splitFileName04(self):
        "Split fname contains asterisk"
        fname = "tas_*_MIROC6_piControl_r1i1p1f1_gn_320001-329912.nc"
        ref = {'experiment_id': 'piControl', 'grid_label': 'gn',
               'source_id': 'MIROC6', 'table_id': '*', 'time_range':
               '320001-329912', 'variable_id': 'tas', 'variant_label':
               'r1i1p1f1'}
        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)

    def test_splitFileName05(self):
        "Split fname with invalid name"
        fname = fname='invalid_but_same_length_with_drs.nc'
        ref = {'experiment_id': 'length', 'grid_label': 'drs',
               'source_id': 'same', 'table_id': 'but', 'variable_id':
               'invalid', 'variant_label': 'with'}
        res = drs.DRS().splitFileName(fname)
        self.assertEqual(ref, res)
        with self.assertRaises(ValueError):
            res = drs.DRS().splitFileName(fname, validate=True)

    def test_dirNameUseClass01(self):
        "Construct dirname by class method."
        ref = Path("CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/"
                   "Amon/tas/gn/v20181212")
        res = drs.DRS(**self.ga).dirName()
        self.assertEqual(ref, res)

    def test_dirNameUseClass02(self):
        "Construct dirname with sub_experiment_id by class method."
        ref = Path("CMIP6/DCPP/IPSL/IPSL-CM6A-LR/dcppC-atl-pacemaker/"
                   "s1950-r1i1p1f1/Amon/rsdscs/gr/v20190110")
        res = drs.DRS(**self.ga_w_sub).dirName()
        self.assertEqual(ref, res)

    def test_dirNameUseClass03(self):
        "dirName() with missing attribute"
        attrs = {k:v for k,v in self.ga.items()}
        del attrs['table_id']
        ref = Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/*/tas/gn/v20181212')
        res = drs.DRS(**attrs).dirName()
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            res = drs.DRS(**attrs).dirName(allow_asterisk=False)

    def test_dirNameUseClass11(self):
        "dirName() with invalid value for valid attribute"
        attrs = {k:v for k,v in drs.sample_attrs.items()}
        attrs['table_id'] = 'invalid'
        ref = Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/*/tas/gn/v20181212')
        res = drs.DRS(**attrs).dirName()
        self.assertEqual(ref, res)
        with self.assertRaises(AttributeError):
            res = drs.DRS(**attrs).dirName(allow_asterisk=False)

    def test_dirNameUseInstance01(self):
        "Construct dirname by istance method, reusing one instance."
        variants = ['r1i1p1f1', 'r2i1p1f1', 'r3i1p1f1']
        refs = [Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/'
                     'Amon/tas/gn/v20181212'),
                Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r2i1p1f1/'
                     'Amon/tas/gn/v20181212'),
                Path('CMIP6/CMIP/MIROC/MIROC6/piControl/r3i1p1f1/'
                     'Amon/tas/gn/v20181212')]
        d = drs.DRS(**self.ga)
        for v,r in zip(variants, refs):
            d.set(variant_label=v)
            res = d.dirName()
            self.assertEqual(r, res)

    def test_splitDirName01a(self):
        "Split dirname without prefix"
        dname = self.dname
        ref = {'activity_id': 'CMIP', 'experiment_id': 'piControl',
               'grid_label': 'gn', 'institution_id': 'MIROC',
               'mip_era': 'CMIP6', 'source_id': 'MIROC6', 'table_id':
               'Amon', 'variable_id': 'tas', 'variant_label':
               'r1i1p1f1', 'version': 'v20181212', 'prefix': ''}
        res = drs.DRS().splitDirName(dname)
        self.assertEqual(ref, res)

    def test_splitDirName01b(self):
        "Split dirname with prefix"
        prefix = "/data"
        dname = self.dname
        ref = {'activity_id': 'CMIP', 'experiment_id': 'piControl',
               'grid_label': 'gn', 'institution_id': 'MIROC',
               'mip_era': 'CMIP6', 'prefix': '/data', 'source_id':
               'MIROC6', 'table_id': 'Amon', 'variable_id': 'tas',
               'variant_label': 'r1i1p1f1', 'version': 'v20181212'}
        res = drs.DRS().splitDirName(Path(prefix) / Path(dname))
        self.assertEqual(ref, res)

    def test_splitDirName02a(self):
        "Split dirname with sub_experiment_id, without prefix"
        dname = self.dname_w_subexp
        ref = {'activity_id': 'DCPP', 'experiment_id': 'dcppC-atl-pacemaker',
               'grid_label': 'gr', 'institution_id': 'IPSL', 'mip_era': 'CMIP6',
               'source_id': 'IPSL-CM6A-LR', 'sub_experiment_id': 's1950',
               'table_id': 'Amon', 'variable_id': 'rsdscs',
               'variant_label': 'r1i1p1f1', 'version': 'v20190110', 'prefix': ''}
        res = drs.DRS().splitDirName(dname)
        self.assertEqual(ref, res)

    def test_splitDirName02b(self):
        "Split dirname with sub_experiment_id, with prefix"
        prefix = '/data'
        dname = self.dname_w_subexp
        ref = {'activity_id': 'DCPP', 'experiment_id': 'dcppC-atl-pacemaker',
               'grid_label': 'gr', 'institution_id': 'IPSL', 'mip_era': 'CMIP6',
               'source_id': 'IPSL-CM6A-LR', 'sub_experiment_id': 's1950',
               'table_id': 'Amon', 'variable_id': 'rsdscs',
               'variant_label': 'r1i1p1f1', 'version': 'v20190110', 'prefix': '/data'}
        res = drs.DRS().splitDirName(Path(prefix) / Path(dname))
        self.assertEqual(ref, res)

    def test_splitDirName03(self):
        "Split dname contains asterisk"
        dname = 'CMIP6/CMIP/MIROC/MIROC6/*/r1i1p1f1/Amon/tas/gn/v20181212'
        ref = {'activity_id': 'CMIP', 'experiment_id': '*',
               'grid_label': 'gn', 'institution_id': 'MIROC',
               'mip_era': 'CMIP6', 'prefix': '', 'source_id':
               'MIROC6', 'table_id': 'Amon', 'variable_id': 'tas',
               'variant_label': 'r1i1p1f1', 'version': 'v20181212'}
        res = drs.DRS().splitDirName(dname)
        self.assertEqual(ref, res)

    def test_splitDirName04(self):
        "Split dname with invalid name"
        dname = 'Some/Invalid/Path'
        with self.assertRaises(ValueError):
            res = drs.DRS().splitDirName(dname)
        dname = ('Some/Invalid/but/has/occasionally/'
                 'the/same/number/of/component/')
        ref = {'activity_id': 'Invalid', 'experiment_id':
               'occasionally', 'grid_label': 'of', 'institution_id':
               'but', 'mip_era': 'Some', 'prefix': '', 'source_id':
               'has', 'table_id': 'same', 'variable_id': 'number',
               'variant_label': 'the', 'version': 'component'}
        res = drs.DRS().splitDirName(dname)
        self.assertEqual(ref, res)
        with self.assertRaises(ValueError):
            res = drs.DRS().splitDirName(dname, validate=True)

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
        "Valid dirname(-like) with/without directory=True"
        dname = dirname(self.url)
        res = drs.DRS().isValidPath(dname)
        self.assertFalse(res)
        res = drs.DRS().isValidPath(dname, directory=True)
        self.assertTrue(res)

    def test_isValidPath07(self):
        "Valid dirname, separaterd=True"
        dname = dirname(self.url)
        ref = ({'all': True},
               {'activity_id': True, 'experiment_id': True,
                'grid_label': True, 'institution_id': True,
                'mip_era': True, 'source_id': True, 'table_id': True,
                'variable_id': True, 'variant_label': True, 'version': True})
        res = drs.DRS().isValidPath(dname,
                                    directory=True, separated=True)
        self.assertEqual(ref, res)

    def test_isValidPath08(self):
        "Valid URL with sub_experiment_id, separated is True"
        ref = ({'experiment_id': True, 'grid_label': True,
                'source_id': True, 'sub_experiment_id': True,
                'table_id': True, 'time_range': True, 'variable_id': True,
                'variant_label': True},
               {'activity_id': True, 'experiment_id': True,
                'grid_label': True, 'institution_id': True, 'mip_era': True,
                'source_id': True, 'sub_experiment_id': True,
                'table_id': True, 'variable_id': True,
                'variant_label': True, 'version': True})
        res = drs.DRS().isValidPath(self.url_w_subexp, separated=True)
        self.assertEqual(ref, res)

    def test_isValid00(self):
        attrs = {a: v for a,v in self.ga.items()}
        d = drs.DRS(**attrs)
        self.assertTrue(d.isValid())

    def test_isValid01(self):
        attrs = {a: v for a,v in self.ga.items()}
        attrs.update({'experiment_id': 'invalid'})
        d = drs.DRS(**attrs)
        self.assertTrue(d.isValid())
        d = drs.DRS(**attrs, do_sanitize=False)
        self.assertFalse(d.isValid())

    def test_isValidValueForAttr00(self):
        "check time_range"
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
            self.assertTrue(drs.DRS().isValidValueForAttr(v, 'time_range'))
        for v in invalid_values:
            self.assertFalse(drs.DRS().isValidValueForAttr(v, 'time_range'))

    def test_isValidValueForAttr01(self):
        "check version"
        valid_values = [
            'v20190510',
            'v00000000']
        invalid_values = [
            None,
            "",
            'ver.1.0',
            '20190510',
            '2019',
            'vv20190510']
        for v in valid_values:
            res = drs.DRS().isValidValueForAttr(v, 'version')
            self.assertTrue(res)
        for v in invalid_values:
            res = drs.DRS().isValidValueForAttr(v, 'version')
            self.assertFalse(res)

    def test_isValidValueForAttr02(self):
        "check variant_label"
        valid_values = [
            'r1i1p1f1',
            'r10i1p1f1']
        invalid_values = [
            None,
            "",
            'r1i1p1',
            'r1f1f1p1',
            'rXiYfZpM',
            'hoge',
            '1357']
        for v in valid_values:
            res = drs.DRS().isValidValueForAttr(v, 'variant_label')
            self.assertTrue(res)
        for v in invalid_values:
            res = drs.DRS().isValidValueForAttr(v, 'variant_label')
            self.assertFalse(res)

    def test_doSanitize00(self):
        "doSanitize() will remove attribute with invalid value"
        attrs = {a: v for a,v in self.ga.items()}
        d = drs.DRS(**attrs)
        d.activity_id = 'InvalidMIP'
        self.assertTrue(hasattr(d, 'activity_id'))
        d.doSanitize()
        self.assertFalse(hasattr(d, 'activity_id'))

    def test_doSanitize01(self):
        "doSanitize() will remove attribute with invalid value only from multi values"
        attrs = {a: v for a,v in self.ga.items()}
        attrs.update({'experiment_id': 'amip, piControl'})
        ref = ['amip', 'piControl']
        d = drs.DRS(**attrs)
        res = d.experiment_id
        self.assertEqual(ref, res)
        attrs.update({'experiment_id': 'Invalid, piControl'})
        ref = ['piControl']
        d = drs.DRS(**attrs)
        res = d.experiment_id
        self.assertEqual(ref, res)

def main():
    unittest.main()


if __name__ == "__main__":
    main()
