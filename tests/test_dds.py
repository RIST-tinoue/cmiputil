#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pprint import pprint

from cmiputil import dds

# dds._enable_debug()
sample1_text = '''\
Dataset {
    Float64 lat[lat = 160];
    Float64 lat_bnds[lat = 160][bnds = 2];
    Float64 lon[lon = 320];
    Float64 lon_bnds[lon = 320][bnds = 2];
    Float64 height;
    Float64 time[time = 8412];
    Float64 time_bnds[time = 8412][bnds = 2];
    Grid {
     ARRAY:
        Float32 tas[time = 8412][lat = 160][lon = 320];
     MAPS:
        Float64 time[time = 8412];
        Float64 lat[lat = 160];
        Float64 lon[lon = 320];
    } tas;
} CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1;
'''
sample1_struct = dds.Dataset(
    'CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1',
    {
        'lat':
        dds.Var('lat', btype='Float64', arr=[dds.Arr('lat', 160)]),
        'lat_bnds':
        dds.Var('lat_bnds',
                btype='Float64',
                arr=[dds.Arr('lat', 160),
                     dds.Arr('bnds', 2)]),
        'lon':
        dds.Var('lon', btype='Float64', arr=[dds.Arr('lon', 320)]),
        'lon_bnds':
        dds.Var('lon_bnds',
                btype='Float64',
                arr=[dds.Arr('lon', 320),
                     dds.Arr('bnds', 2)]),
        'height':
        dds.Var('height', btype='Float64'),
        'time':
        dds.Var('time', btype='Float64', arr=[dds.Arr('time', 8412)]),
        'time_bnds':
        dds.Var('time_bnds',
                btype='Float64',
                arr=[dds.Arr('time', 8412),
                     dds.Arr('bnds', 2)]),
        'tas':
        dds.Grid(
            'tas',
            array=dds.Var('tas',
                          btype='Float32',
                          arr=[
                              dds.Arr('time', 8412),
                              dds.Arr('lat', 160),
                              dds.Arr('lon', 320)
                          ]),
            maps={
                'time':
                dds.Var('time', btype='Float64', arr=[dds.Arr('time', 8412)]),
                'lat':
                dds.Var('lat', btype='Float64', arr=[dds.Arr('lat', 160)]),
                'lon':
                dds.Var('lon', btype='Float64', arr=[dds.Arr('lon', 320)])
            })
    })

sample2_text = '''\
Dataset {
  Int32 catalog_number;
  Sequence {
    String experimenter;
    Int32 time;
    Structure {
      Float64 latitude;
      Float64 longitude;
    } location;
    Sequence {
      Float64 depth;
      Float64 salinity;
      Float64 oxygen;
      Float64 temperature;
    } cast;
  } station;
} data;
'''

sample2_struct = dds.Dataset(
    'data', {
        'catalog_number':
        dds.Var('catalog_number', 'Int32'),
        'station':
        dds.Sequence(
            'station', {
                'experimenter':
                dds.Var('experimenter', 'String'),
                'time':
                dds.Var('time', 'Int32'),
                'location':
                dds.Structure(
                    'location', {
                        'latitude': dds.Var('latitude', 'Float64'),
                        'longitude': dds.Var('longitude', 'Float64')
                    }),
                'cast':
                dds.Sequence(
                    'cast', {
                        'depth': dds.Var('depth', 'Float64'),
                        'salinity': dds.Var('salinity', 'Float64'),
                        'oxygen': dds.Var('oxygen', 'Float64'),
                        'temperature': dds.Var('temperature', 'Float64')
                    })
            })
    })

sample3_text = '''\
Dataset {
    Structure {
        Float64 lat;
        Float64 lon;
    } location;
    Structure {
        Int32 minutes;
        Int32 day;
        Int32 year;
    } time;
    Float64 depth[500];
    Float64 temperature[500];
} xbt-station;
'''

sample3_struct = dds.Dataset(
    'xbt-station', {
        'location':
        dds.Structure('location', {
            'lat': dds.Var('lat', 'Float64'),
            'lon': dds.Var('lon', 'Float64')
        }),
        'time':
        dds.Structure(
            'time', {
                'minutes': dds.Var('minutes', 'Int32'),
                'day': dds.Var('day', 'Int32'),
                'year': dds.Var('year', 'Int32')
            }),
        'depth':
        dds.Var('depth', 'Float64', arr=[dds.Arr('', 500)]),
        'temperature':
        dds.Var('temperature', 'Float64', arr=[dds.Arr('', 500)])
    })


class test_DDS(unittest.TestCase):
    def setUp(self):
        # dds._enable_debug()
        self.maxDiff = None
        pass

    def tearUp(self):
        pass

    def test_Arr(self):
        a = dds.Arr()
        self.assertIsInstance(a, dds.Arr)

        name = 'lat'
        val = 160
        text = r'[lat = 160] \n'

        # set attributes
        a = dds.Arr(name=name, val=val)
        self.assertEqual(a.name, 'lat')
        self.assertEqual(a.val, 160)

        # parse()
        a = dds.Arr(text=text)
        self.assertEqual(a.name, 'lat')
        self.assertEqual(a.val, 160)
        self.assertEqual(a, dds.Arr(name='lat', val=160))

        # Invalid text -> blank object
        text = 'lat = 160'
        a = dds.Arr(text=text)
        self.assertEqual(a.name, '')
        self.assertIsNone(a.val)
        self.assertEqual(a, dds.Arr())

        # test __repr__()
        text = '[time = 8412]'
        a = dds.Arr(text=text)
        ref = "Arr('time', 8412)"
        self.assertEqual(ref, a.__repr__())

        # test __str__()
        text = '[time = 8412]'
        a = dds.Arr(text=text)
        ref = "Arr(name='time', val=8412)"
        self.assertEqual(ref, a.__str__())

        # test text
        text = '[time = 8412]'
        ref = '[time = 8412]'
        a = dds.Arr(text=text)
        res = a.text
        self.assertEqual(ref, res)

        # test __eq__
        a1 = dds.Arr(text=text)
        a2 = dds.Arr(name='time', val=8412)
        self.assertEqual(a1, a2)
        a2 = dds.Arr(name='lon', val=8412)
        self.assertNotEqual(a1, a2)
        self.assertNotEqual(a1, text)

    def test_Var(self):
        text = '  Float64 height;'
        vl = dds.Var(text=text)
        self.assertEqual(vl.btype, dds.BType.Float64)
        self.assertEqual(vl.name, 'height')
        self.assertIsNone(vl.arr)

        text = 'Float32 time[time = 8412];\n'
        vl = dds.Var(text=text)
        self.assertEqual(vl.btype, dds.BType.Float32)
        self.assertEqual(vl.name, 'time')
        self.assertEqual(vl.arr, [dds.Arr('time', 8412)])

        text = 'Float64 time_bnds[time = 8412][bnds = 2];'
        vl = dds.Var(text=text)
        self.assertEqual(vl.btype, dds.BType.Float64)
        self.assertEqual(vl.arr, [dds.Arr('time', 8412), dds.Arr('bnds', 2)])

        # invalid text causes null object
        text = 'height;'
        vl = dds.Var(text=text)
        self.assertEqual(vl, dds.Var())

        # test __repr__()
        text = 'Float64 time_bnds[time = 8412][bnds = 2];'
        vl = dds.Var(text=text)
        ref = "Var('time_bnds', 'Float64', arr=[Arr('time', 8412), Arr('bnds', 2)])"
        self.assertEqual(ref, vl.__repr__())

        # test __str__()
        ref = 'Float64 time_bnds[time = 8412][bnds = 2];'
        self.assertEqual(ref, vl.__str__())

        # test text
        ref = 'Float64 time_bnds[time = 8412][bnds = 2];'
        self.assertEqual(ref, vl.text)

        # test __eq__()
        text = 'Float64 time_bnds[time = 8412][bnds = 2];'
        vl1 = dds.Var(text=text)
        vl2 = dds.Var('time_bnds',
                      btype='Float64',
                      arr=[dds.Arr('time', 8412),
                           dds.Arr('bnds', 2)])
        self.assertEqual(vl1, vl2)
        vl2 = dds.Var('time_bnds',
                      btype='Float32',
                      arr=[dds.Arr('time', 8412),
                           dds.Arr('bnds', 2)])
        self.assertNotEqual(vl1, vl2)

    def test_Structure(self):
        # test constructor
        ss = dds.Structure()
        self.assertIsInstance(ss, dds.Structure)

        # test parse()
        text = ('''Structure {
                  Float64 latitude;
                  Float64 longitude;
                } location; ''')
        res = dds.Structure(text=text)
        self.assertEqual(res.name, 'location')
        ref_decl = dict([('latitude', dds.Var('latitude', 'Float64')),
                         ('longitude', dds.Var('longitude', 'Float64'))])
        self.assertEqual(ref_decl, res.decl)

        # test __eq__
        s1 = dds.Structure(text=text)
        s2 = dds.Structure('location',
                           decl=dict([
                               ('latitude', dds.Var('latitude', 'Float64')),
                               ('longitude', dds.Var('longitude', 'Float64'))
                           ]))
        self.assertEqual(s1, s2)

        # test __repr__
        ss = dds.Structure(text=text)
        ref = "Structure('location', {'latitude': Var('latitude', 'Float64'), 'longitude': Var('longitude', 'Float64')})"
        self.assertEqual(ref, ss.__repr__())

        # test __str__
        ss = dds.Structure(text=text)
        ref = "Structure {\n    Float64 latitude;\n    Float64 longitude;\n} location;"
        self.assertEqual(ref, ss.__str__())

        # test __getattr__
        ss = dds.Structure(text=text)
        ref = dds.Var('latitude', 'Float64')
        self.assertEqual(ref, ss.latitude)

        # non existent attribute raises AttributeError
        with self.assertRaises(AttributeError):
            ss.hoge

        # test __getitem__
        ss = dds.Structure(text=text)
        ref = dds.Var('longitude', 'Float64')
        self.assertEqual(ref, ss['longitude'])

        # non existent item raises KeyError
        with self.assertRaises(KeyError):
            ss['hoge']

        # test __contains__
        ss = dds.Structure(text=text)
        self.assertTrue('name' in ss)
        self.assertTrue('latitude' in ss)
        self.assertFalse('hoge' in ss)

        # test text_formatted
        ref = 'Structure {\n    Float64 latitude;\n    Float64 longitude;\n} location;'
        self.assertEqual(ref, ss.text_formatted())
        ref = 'Structure {\n  Float64 latitude;\n  Float64 longitude;\n} location;'
        self.assertEqual(ref, ss.text_formatted(2))

        # test text
        ref = 'Structure {Float64 latitude;Float64 longitude;} location;'
        self.assertEqual(ref, ss.text)

        # Invalid text -> null object
        text = ('''Structue {
                  Float64 latitude;
                  Float64 longitude;
                } location; ''')
        ss = dds.Structure(text=text)
        self.assertEqual(ss, dds.Structure())

    def test_Sequence(self):
        # test constructor
        ss = dds.Sequence()
        self.assertIsInstance(ss, dds.Sequence)

        # test parse()
        text = ('''Sequence {
                  Float64 latitude;
                  Float64 longitude;
                } location; ''')
        res = dds.Sequence(text=text)
        self.assertEqual(res.name, 'location')
        ref_decl = dict([('latitude', dds.Var('latitude', 'Float64')),
                         ('longitude', dds.Var('longitude', 'Float64'))])
        self.assertEqual(ref_decl, res.decl)

        # test __eq__
        s1 = dds.Sequence(text=text)
        s2 = dds.Sequence('location',
                          decl=dict([
                              ('latitude', dds.Var('latitude', 'Float64')),
                              ('longitude', dds.Var('longitude', 'Float64'))
                          ]))
        self.assertEqual(s1, s2)

        # test __repr__
        ss = dds.Sequence(text=text)
        ref = "Sequence('location', {'latitude': Var('latitude', 'Float64'), 'longitude': Var('longitude', 'Float64')})"
        self.assertEqual(ref, ss.__repr__())

        # test __str__
        ss = dds.Sequence(text=text)
        ref = "Sequence {\n    Float64 latitude;\n    Float64 longitude;\n} location;"

        self.assertEqual(ref, ss.__str__())

        # test __getattr__
        ss = dds.Sequence(text=text)
        ref = dds.Var('latitude', 'Float64')
        self.assertEqual(ref, ss.latitude)

        # non existent attribute raises AttributeError
        with self.assertRaises(AttributeError):
            ss.hoge

        # test __getitem__
        ss = dds.Sequence(text=text)
        ref = dds.Var('longitude', 'Float64')
        self.assertEqual(ref, ss['longitude'])

        # non existent item raises KeyError
        with self.assertRaises(KeyError):
            ss['hoge']

        # test __contains__
        ss = dds.Sequence(text=text)
        self.assertTrue('name' in ss)
        self.assertTrue('latitude' in ss)
        self.assertFalse('hoge' in ss)

        # test text_formatted
        ref = 'Sequence {\n    Float64 latitude;\n    Float64 longitude;\n} location;'
        self.assertEqual(ref, ss.text_formatted())
        ref = 'Sequence {\n  Float64 latitude;\n  Float64 longitude;\n} location;'
        self.assertEqual(ref, ss.text_formatted(2))

        # test text
        ref = 'Sequence {Float64 latitude;Float64 longitude;} location;'
        self.assertEqual(ref, ss.text)

        # Invalid text -> null object
        text = ('''Structue {
                  Float64 latitude;
                  Float64 longitude;
                } location; ''')
        ss = dds.Sequence(text=text)
        self.assertEqual(ss, dds.Sequence())

    def test_Grid(self):
        # test constructor
        g = dds.Grid()
        self.assertIsInstance(g, dds.Grid)

        # test parse()
        text = ('Grid {'
                ' ARRAY:'
                '   Float32 tas[time = 8412][lat = 160][lon = 320];'
                ' MAPS:'
                '   Float64 time[time = 8412];'
                '   Float64 lat[lat = 160];'
                '   Float64 lon[lon = 320];'
                '} tas;')
        g = dds.Grid(text=text)
        self.assertEqual(g.name, 'tas')
        # self.assertEqual(g.stype, dds.SType.Grid)
        self.assertEqual(
            g.array,
            dds.Var('tas', 'Float32', '[time = 8412][lat = 160][lon = 320]'))
        self.assertEqual(
            g.maps,
            dict([('time', dds.Var('time', 'Float64', '[time = 8412]')),
                  ('lat', dds.Var('lat', 'Float64', '[lat= 160]')),
                  ('lon', dds.Var('lon', 'Float64', '[lon= 320]'))]))

        # test __eq__
        ref = dds.Grid('tas',
                       array=dds.Var('tas', 'Float32',
                                     '[time = 8412][lat = 160][lon = 320]'),
                       maps=dict([
                           ('time', dds.Var('time', 'Float64',
                                            '[time = 8412]')),
                           ('lat', dds.Var('lat', 'Float64', '[lat= 160]')),
                           ('lon', dds.Var('lon', 'Float64', '[lon= 320]'))
                       ]))
        self.assertEqual(ref, g)

        # test __repr__
        ref = "Grid('tas', array=Var('tas', 'Float32', arr=[Arr('time', 8412), Arr('lat', 160), Arr('lon', 320)]), maps={'time': Var('time', 'Float64', arr=[Arr('time', 8412)]), 'lat': Var('lat', 'Float64', arr=[Arr('lat', 160)]), 'lon': Var('lon', 'Float64', arr=[Arr('lon', 320)])})"
        res = g.__repr__()

        self.assertEqual(ref, res)

        # test __str__
        ref = 'Grid {\n ARRAY:\n    Float32 tas[time = 8412][lat = 160][lon = 320];\n MAPS:\n    Float64 time[time = 8412];\n    Float64 lat[lat = 160];\n    Float64 lon[lon = 320];\n} tas;'
        res = g.__str__()
        self.assertEqual(ref, res)

        # test __getattr__
        ss = dds.Grid(text=text)
        ref = dds.Var('lat', 'Float64', arr=[dds.Arr('lat', 160)])
        self.assertEqual(ref, ss.lat)

        # non existent attribute raises AttributeError
        with self.assertRaises(AttributeError):
            ss.hoge

        # test __getitem__
        ss = dds.Grid(text=text)
        ref = dds.Var('lon', 'Float64', arr=[dds.Arr('lon', 320)])
        self.assertEqual(ref, ss['lon'])

        # non existent item raises KeyError
        with self.assertRaises(KeyError):
            ss['hoge']

        # test __contains__
        ss = dds.Grid(text=text)
        self.assertTrue('name' in ss)
        self.assertTrue('lat' in ss)
        self.assertTrue('tas' in ss)
        self.assertFalse('hoge' in ss)

        # test text_formatted
        ref = 'Grid {\n ARRAY:\n    Float32 tas[time = 8412][lat = 160][lon = 320];\n MAPS:\n    Float64 time[time = 8412];\n    Float64 lat[lat = 160];\n    Float64 lon[lon = 320];\n} tas;'
        res = g.text_formatted()
        self.assertEqual(ref, res)

        # test text
        ref = 'Grid { ARRAY:Float32 tas[time = 8412][lat = 160][lon = 320]; MAPS:Float64 time[time = 8412];Float64 lat[lat = 160];Float64 lon[lon = 320];} tas;'
        res = g.text
        self.assertEqual(ref, res)

    def test_check_braces_matching(self):
        dds.check_braces_matching(sample1_text)
        dds.check_braces_matching(sample2_text)
        dds.check_braces_matching(sample3_text)

        text = '{ { }{ {}'
        with self.assertRaises(ValueError):
            dds.check_braces_matching(text)

        text = '{ { } }}}{}'
        with self.assertRaises(ValueError):
            dds.check_braces_matching(text)

    def test_parse_dataset(self):

        ref = sample1_struct
        res = dds.parse_dataset(sample1_text)

        for a in ref.__dict__:
            self.assertEqual(getattr(ref, a), getattr(res, a))
        self.assertEqual(ref, res)

        res = dds.parse_dataset(sample2_text)
        ref = sample2_struct
        for a in ref.__dict__:
            self.assertEqual(getattr(ref, a), getattr(res, a))
        self.assertEqual(ref, res)

        ref = sample3_struct
        res = dds.parse_dataset(sample3_text)
        self.assertEqual(ref.text, res.text)
        self.assertEqual(ref, res)

        ### not-valid Dataset text, raises ValueError.
        text = '''\
          Sequence {
            String experimenter;
            Int32 time;
            Structure {
              Float64 latitude;
              Float64 longitude;
            } location;
            Sequence {
              Float64 depth;
              Float64 salinity;
              Float64 oxygen;
              Float64 temperature;
            } cast;
          } station;'''
        with self.assertRaises(ValueError):
            dds.parse_dataset(text)

    def test_parse_declarations(self):
        text = '''\
        Int32 catalog_number;
        Sequence {
            String experimenter;
            Int32 time;
            Structure {
                Float64 latitude;
                Float64 longitude;
            } location;
            Sequence {
                Float64 depth;
                Float64 salinity;
                Float64 oxygen;
                Float64 temperature;
            } cast;
        } station;
        '''

        ref = dict([
            ('catalog_number', dds.Var(name='catalog_number', btype='Int32')),
            ('station',
             dds.Sequence(
                 'station',
                 decl=dict([
                     ('experimenter', dds.Var('experimenter', btype='String')),
                     ('time', dds.Var('time', btype='Int32')),
                     ('location',
                      dds.Structure('location',
                                    decl=dict([('latitude',
                                                dds.Var('latitude',
                                                        btype='Float64')),
                                               ('longitude',
                                                dds.Var('longitude',
                                                        btype='Float64'))]))),
                     ('cast',
                      dds.Sequence('cast',
                                   decl=dict([('depth',
                                               dds.Var('depth',
                                                       btype='Float64')),
                                              ('salinity',
                                               dds.Var('salinity',
                                                       btype='Float64')),
                                              ('oxygen',
                                               dds.Var('oxygen',
                                                       btype='Float64')),
                                              ('temperature',
                                               dds.Var('temperature',
                                                       btype='Float64'))])))
                 ])))
        ])

        res = dds.parse_declarations(text)
        self.assertEqual(ref, res)

    def test_pop_struct(self):
        text = ('Structure {'
                '  Float64 latitude;'
                '  Float64 longitude;'
                '} location;'
                'Sequence {'
                '  Float64 depth;'
                '  Float64 salinity;'
                '  Float64 oxygen;'
                '  Float64 temperature;'
                '} cast;')
        s, rest = dds.pop_struct(text)
        ref = dds.Structure('location',
                            decl=dict([('latitude',
                                        dds.Var('latitude', btype='Float64')),
                                       ('longitude',
                                        dds.Var('longitude',
                                                btype='Float64'))]))
        self.assertEqual(ref, s)
        ref = ('Sequence {'
               '  Float64 depth;'
               '  Float64 salinity;'
               '  Float64 oxygen;'
               '  Float64 temperature;'
               '} cast;')
        self.assertEqual(ref, rest)

    def test_pop_varline(self):
        text = ('Float64 depth;' 'Float64 salinity;' 'Float64 oxygen;')
        v, rest = dds.pop_varline(text)
        ref = dds.Var('depth', 'Float64')
        self.assertEqual(ref, v)
        ref = 'Float64 salinity;Float64 oxygen;'
        self.assertEqual(ref, rest)

    def test_parse_arrdecls(self):
        text = '[time = 8412]'
        ref = [dds.Arr('time', 8412)]
        res = dds.parse_arrdecls(text=text)
        self.assertEqual(ref, res)

        text = '[time = 8412][lat = 160][lon = 320]'
        ref = [dds.Arr('time', 8412), dds.Arr('lat', 160), dds.Arr('lon', 320)]
        res = dds.parse_arrdecls(text=text)
        self.assertEqual(ref, res)

        # invalid text -> blank list
        text = 'height;'
        res = dds.parse_arrdecls(text=text)
        ref = None
        self.assertEqual(ref, res)


def main():
    print('calling unittest:')
    unittest.main()


if __name__ == '__main__':
    main()
