#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from collections import OrderedDict
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
    decl=OrderedDict([
        ('lat',
         dds.VarLine('lat',
                     btype=dds.BType.Float64,
                     arr=[dds.ArrDecl('lat', val=160)])),
        ('lat_bnds',
         dds.VarLine(
             'lat_bnds',
             btype=dds.BType.Float64,
             arr=[dds.ArrDecl('lat', val=160),
                  dds.ArrDecl('bnds', val=2)])),
        ('lon',
         dds.VarLine('lon',
                     btype=dds.BType.Float64,
                     arr=[dds.ArrDecl('lon', val=320)])),
        ('lon_bnds',
         dds.VarLine(
             'lon_bnds',
             btype=dds.BType.Float64,
             arr=[dds.ArrDecl('lon', val=320),
                  dds.ArrDecl('bnds', val=2)])),
        ('height', dds.VarLine('height', btype=dds.BType.Float64)),
        ('time',
         dds.VarLine('time',
                     btype=dds.BType.Float64,
                     arr=[dds.ArrDecl('time', val=8412)])),
        ('time_bnds',
         dds.VarLine(
             'time_bnds',
             btype=dds.BType.Float64,
             arr=[dds.ArrDecl('time', val=8412),
                  dds.ArrDecl('bnds', val=2)])),
        ('tas',
         dds.Grid('tas',
                  array=dds.VarLine('tas',
                                    dds.BType.Float32,
                                    arr=[
                                        dds.ArrDecl('time', 8412),
                                        dds.ArrDecl('lat', 160),
                                        dds.ArrDecl('lon', 320)
                                    ]),
                  maps=OrderedDict([
                      ('time',
                       dds.VarLine('time',
                                   dds.BType.Float64,
                                   arr=[dds.ArrDecl('time', 8412)])),
                      ('lat',
                       dds.VarLine('lat',
                                   dds.BType.Float64,
                                   arr=[dds.ArrDecl('lat', 160)])),
                      ('lon',
                       dds.VarLine('lon',
                                   dds.BType.Float64,
                                   arr=[dds.ArrDecl('lon', 320)]))
                  ])))
    ]))

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
    'data',
    decl=OrderedDict([
        ('catalog_number', dds.VarLine('catalog_number', btype='Int32')),
        ('station',
         dds.Sequence('station',
                      decl=OrderedDict([
                          ('experimenter',
                           dds.VarLine('experimenter', btype='String')),
                          ('time', dds.VarLine('time', btype='Int32')),
                          ('location',
                           dds.Structure('location',
                                         decl=OrderedDict([
                                             ('latitude',
                                              dds.VarLine('latitude',
                                                          btype='Float64')),
                                             ('longitude',
                                              dds.VarLine('longitude',
                                                          btype='Float64'))
                                         ]))),
                          ('cast',
                           dds.Sequence('cast',
                                        decl=OrderedDict([
                                            ('depth',
                                             dds.VarLine('depth',
                                                         btype='Float64')),
                                            ('salinity',
                                             dds.VarLine('salinity',
                                                         btype='Float64')),
                                            ('oxygen',
                                             dds.VarLine('oxygen',
                                                         btype='Float64')),
                                            ('temperature',
                                             dds.VarLine('temperature',
                                                         btype='Float64'))
                                        ])))
                      ])))
    ]))

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
    'xbt-station',
    decl=OrderedDict([
        ('location',
         dds.Structure('location',
                       decl=OrderedDict([
                           ('lat', dds.VarLine('lat', btype='Float64')),
                           ('lon', dds.VarLine('lon', btype='Float64')),
                       ]))),
        ('time',
         dds.Structure('time',
                       decl=OrderedDict([
                           ('minutes', dds.VarLine('minutes', btype='Int32')),
                           ('day', dds.VarLine('day', btype='Int32')),
                           ('year', dds.VarLine('year', btype='Int32')),
                       ]))),
        ('depth',
         dds.VarLine('depth', btype='Float64', arr=[dds.ArrDecl('', 500)])),
        ('temperature',
         dds.VarLine('temperature',
                     btype='Float64',
                     arr=[dds.ArrDecl('', 500)])),
    ]))


class test_DDS(unittest.TestCase):
    def setUp(self):
        # dds._enable_debug()
        self.maxDiff = None
        pass

    def tearUp(self):
        pass

    def test_ArrDecl(self):
        a = dds.ArrDecl()
        self.assertIsInstance(a, dds.ArrDecl)

        name = 'lat'
        val = 160
        text = r'[lat = 160] \n'

        # set attributes
        a = dds.ArrDecl(name=name, val=val)
        self.assertEqual(a.name, 'lat')
        self.assertEqual(a.val, 160)

        # parse()
        a = dds.ArrDecl(text=text)
        self.assertEqual(a.name, 'lat')
        self.assertEqual(a.val, 160)
        self.assertEqual(a, dds.ArrDecl(name='lat', val=160))

        # Invalid text -> blank object
        text = 'lat = 160'
        a = dds.ArrDecl(text=text)
        self.assertEqual(a.name, '')
        self.assertIsNone(a.val)
        self.assertEqual(a, dds.ArrDecl())

        # test __repr__()
        text = '[time = 8412]'
        a = dds.ArrDecl(text=text)
        ref = "ArrDecl('time', 8412)"
        self.assertEqual(ref, a.__repr__())

        # test __str__()
        text = '[time = 8412]'
        a = dds.ArrDecl(text=text)
        ref = "ArrDecl(name='time', val=8412)"
        self.assertEqual(ref, a.__str__())

        # test text
        text = '[time = 8412]'
        ref = '[time = 8412]'
        a = dds.ArrDecl(text=text)
        res = a.text
        self.assertEqual(ref, res)

        # test __eq__
        a1 = dds.ArrDecl(text=text)
        a2 = dds.ArrDecl(name='time', val=8412)
        self.assertEqual(a1, a2)
        a2 = dds.ArrDecl(name='lon', val=8412)
        self.assertNotEqual(a1, a2)
        self.assertNotEqual(a1, text)

    def test_VarLine(self):
        text = '  Float64 height;'
        vl = dds.VarLine(text=text)
        self.assertEqual(vl.btype, dds.BType.Float64)
        self.assertEqual(vl.name, 'height')
        self.assertIsNone(vl.arr)

        text = 'Float32 time[time = 8412];\n'
        vl = dds.VarLine(text=text)
        self.assertEqual(vl.btype, dds.BType.Float32)
        self.assertEqual(vl.name, 'time')
        self.assertEqual(vl.arr, [dds.ArrDecl('time', 8412)])

        text = 'Float64 time_bnds[time = 8412][bnds = 2];'
        vl = dds.VarLine(text=text)
        self.assertEqual(vl.btype, dds.BType.Float64)
        self.assertEqual(vl.arr,
                         [dds.ArrDecl('time', 8412),
                          dds.ArrDecl('bnds', 2)])

        # invalid text causes null object
        text = 'height;'
        vl = dds.VarLine(text=text)
        self.assertEqual(vl, dds.VarLine())

        # test __repr__()
        text = 'Float64 time_bnds[time = 8412][bnds = 2];'
        vl = dds.VarLine(text=text)
        ref = "VarLine('time_bnds', btype='Float64', arr=[ArrDecl('time', 8412), ArrDecl('bnds', 2)])"
        self.assertEqual(ref, vl.__repr__())

        # test __str__()
        ref = 'Float64 time_bnds[time = 8412][bnds = 2];'
        self.assertEqual(ref, vl.__str__())

        # test text
        ref = 'Float64 time_bnds[time = 8412][bnds = 2];'
        self.assertEqual(ref, vl.text)

        # test __eq__()
        text = 'Float64 time_bnds[time = 8412][bnds = 2];'
        vl1 = dds.VarLine(text=text)
        vl2 = dds.VarLine(
            'time_bnds',
            btype='Float64',
            arr=[dds.ArrDecl('time', 8412),
                 dds.ArrDecl('bnds', 2)])
        self.assertEqual(vl1, vl2)
        vl2 = dds.VarLine(
            'time_bnds',
            btype='Float32',
            arr=[dds.ArrDecl('time', 8412),
                 dds.ArrDecl('bnds', 2)])
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
        ref_decl = OrderedDict([
            ('latitude', dds.VarLine('latitude', 'Float64')),
            ('longitude', dds.VarLine('longitude', 'Float64'))
        ])
        self.assertEqual(ref_decl, res.decl)

        # test __eq__
        s1 = dds.Structure(text=text)
        s2 = dds.Structure('location',
                           decl=OrderedDict([
                               ('latitude', dds.VarLine('latitude', 'Float64')),
                               ('longitude', dds.VarLine('longitude', 'Float64'))
                           ]))
        self.assertEqual(s1, s2)

        # test __repr__
        ss = dds.Structure(text=text)
        ref = "Structure('location', decl=OrderedDict([('latitude', VarLine('latitude', btype='Float64')), ('longitude', VarLine('longitude', btype='Float64'))]))"
        self.assertEqual(ref, ss.__repr__())

        # test __str__
        ss = dds.Structure(text=text)
        ref = "Structure {\n    Float64 latitude;\n    Float64 longitude;\n} location;"
        self.assertEqual(ref, ss.__str__())

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
        ref_decl = OrderedDict([
            ('latitude', dds.VarLine('latitude', 'Float64')),
            ('longitude', dds.VarLine('longitude', 'Float64'))
        ])
        self.assertEqual(ref_decl, res.decl)

        # test __eq__
        s1 = dds.Sequence(text=text)
        s2 = dds.Sequence('location',
                          decl=OrderedDict([
                              ('latitude', dds.VarLine('latitude', 'Float64')),
                              ('longitude',
                               dds.VarLine('longitude', 'Float64'))
                          ]))
        self.assertEqual(s1, s2)

        # test __repr__
        ss = dds.Sequence(text=text)
        ref = "Sequence('location', decl=OrderedDict([('latitude', VarLine('latitude', btype='Float64')), ('longitude', VarLine('longitude', btype='Float64'))]))"
        self.assertEqual(ref, ss.__repr__())

        # test __str__
        ss = dds.Sequence(text=text)
        ref = "Sequence {\n    Float64 latitude;\n    Float64 longitude;\n} location;"

        self.assertEqual(ref, ss.__str__())

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
            dds.VarLine('tas', 'Float32',
                        '[time = 8412][lat = 160][lon = 320]'))
        self.assertEqual(
            g.maps,
            OrderedDict([('time',
                          dds.VarLine('time', 'Float64', '[time = 8412]')),
                         ('lat', dds.VarLine('lat', 'Float64', '[lat= 160]')),
                         ('lon', dds.VarLine('lon', 'Float64',
                                             '[lon= 320]'))]))

        # test __eq__
        ref = dds.Grid(
            'tas',
            array=dds.VarLine('tas', 'Float32',
                              '[time = 8412][lat = 160][lon = 320]'),
            maps=OrderedDict([
                ('time', dds.VarLine('time', 'Float64', '[time = 8412]')),
                ('lat', dds.VarLine('lat', 'Float64', '[lat= 160]')),
                ('lon', dds.VarLine('lon', 'Float64', '[lon= 320]'))
            ]))
        self.assertEqual(ref, g)

        # test __repr__
        ref = "Grid('tas', array=VarLine('tas', btype='Float32', arr=[ArrDecl('time', 8412), ArrDecl('lat', 160), ArrDecl('lon', 320)]), maps=OrderedDict([('time', VarLine('time', btype='Float64', arr=[ArrDecl('time', 8412)])), ('lat', VarLine('lat', btype='Float64', arr=[ArrDecl('lat', 160)])), ('lon', VarLine('lon', btype='Float64', arr=[ArrDecl('lon', 320)]))]))"
        res = g.__repr__()

        self.assertEqual(ref, res)

        # test __str__
        ref = 'Grid {\n ARRAY:\n    Float32 tas[time = 8412][lat = 160][lon = 320];\n MAPS:\n    Float64 time[time = 8412];\n    Float64 lat[lat = 160];\n    Float64 lon[lon = 320];\n} tas;'
        res = g.__str__()
        self.assertEqual(ref, res)

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

        ref = OrderedDict([
            ('catalog_number', dds.VarLine(name='catalog_number',
                                           btype='Int32')),
            ('station',
             dds.Sequence('station',
                          decl=OrderedDict([
                              ('experimenter',
                               dds.VarLine('experimenter', btype='String')),
                              ('time', dds.VarLine('time', btype='Int32')),
                              ('location',
                               dds.Structure('location',
                                             decl=OrderedDict([
                                                 ('latitude',
                                                  dds.VarLine(
                                                      'latitude',
                                                      btype='Float64')),
                                                 ('longitude',
                                                  dds.VarLine('longitude',
                                                              btype='Float64'))
                                             ]))),
                              ('cast',
                               dds.Sequence('cast',
                                            decl=OrderedDict([
                                                ('depth',
                                                 dds.VarLine('depth',
                                                             btype='Float64')),
                                                ('salinity',
                                                 dds.VarLine('salinity',
                                                             btype='Float64')),
                                                ('oxygen',
                                                 dds.VarLine('oxygen',
                                                             btype='Float64')),
                                                ('temperature',
                                                 dds.VarLine('temperature',
                                                             btype='Float64'))
                                            ])))
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
                            decl=OrderedDict([
                                ('latitude', dds.VarLine('latitude', btype='Float64')),
                                ('longitude', dds.VarLine('longitude', btype='Float64'))
                            ]))
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
        ref = dds.VarLine('depth', 'Float64')
        self.assertEqual(ref, v)
        ref = 'Float64 salinity;Float64 oxygen;'
        self.assertEqual(ref, rest)

    def test_parse_arrdecls(self):
        text = '[time = 8412]'
        ref = [dds.ArrDecl('time', 8412)]
        res = dds.parse_arrdecls(text=text)
        self.assertEqual(ref, res)

        text = '[time = 8412][lat = 160][lon = 320]'
        ref = [
            dds.ArrDecl('time', 8412),
            dds.ArrDecl('lat', 160),
            dds.ArrDecl('lon', 320)
        ]
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
