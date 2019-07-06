#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pprint import pprint

from cmiputil import dds

sample1 = """\
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
"""

sample2 = """\
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
"""


class test_DDS(unittest.TestCase):
    def setUp(self):
        # dds._enable_debug()
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
        ref = 'ArrDecl("time", 8412)'
        self.assertEqual(ref, a.__repr__())

        # test __str__()
        text = '[time = 8412]'
        a = dds.ArrDecl(text=text)
        ref = 'ArrDecl(name="time", val=8412)'
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
        text = "  Float64 height;"
        vl = dds.VarLine(text=text)
        self.assertEqual(vl.btype, dds.BType.Float64)
        self.assertEqual(vl.name, 'height')
        self.assertIsNone(vl.arr)

        text = "Float32 time[time = 8412];\n"
        vl = dds.VarLine(text=text)
        self.assertEqual(vl.btype, dds.BType.Float32)
        self.assertEqual(vl.name, 'time')
        self.assertEqual(vl.arr, [dds.ArrDecl('time', 8412)])

        text = "Float64 time_bnds[time = 8412][bnds = 2];"
        vl = dds.VarLine(text=text)
        self.assertEqual(vl.btype, dds.BType.Float64)
        self.assertEqual(vl.arr,
                         [dds.ArrDecl('time', 8412),
                          dds.ArrDecl('bnds', 2)])

        # invalid text causes null object
        text = "height;"
        vl = dds.VarLine(text=text)
        self.assertEqual(vl, dds.VarLine())

        # test __repr__()
        text = "Float64 time_bnds[time = 8412][bnds = 2];"
        vl = dds.VarLine(text=text)
        ref = 'VarLine("time_bnds", btype="Float64", arr=[ArrDecl("time", 8412), ArrDecl("bnds", 2)])'
        self.assertEqual(ref, vl.__repr__())

        # test __str__()
        ref = 'VarLine(name="time_bnds", btype="Float64", arr=[ArrDecl("time", 8412), ArrDecl("bnds", 2)])'
        self.assertEqual(ref, vl.__str__())

        # test text
        ref = 'Float64 time_bnds[time = 8412][bnds = 2];'
        self.assertEqual(ref, vl.text)

        # test __eq__()
        text = "Float64 time_bnds[time = 8412][bnds = 2];"
        vl1 = dds.VarLine(text=text)
        vl2 = dds.VarLine(
            "time_bnds",
            btype="Float64",
            arr=[dds.ArrDecl("time", 8412),
                 dds.ArrDecl("bnds", 2)])
        self.assertEqual(vl1, vl2)
        vl2 = dds.VarLine(
            "time_bnds",
            btype="Float32",
            arr=[dds.ArrDecl("time", 8412),
                 dds.ArrDecl("bnds", 2)])
        self.assertNotEqual(vl1, vl2)

    def test_Struct(self):
        # test constructor
        ss = dds.Struct()
        self.assertIsInstance(ss, dds.Struct)

        # test parse()
        text = ("""Structure {
                  Float64 latitude;
                  Float64 longitude;
                } location; """)
        res = dds.Struct(text=text)
        self.assertEqual(res.name, 'location')
        self.assertEqual(res.stype, dds.SType.Structure)
        ref_decl = [
            dds.VarLine('latitude', 'Float64'),
            dds.VarLine('longitude', 'Float64')
        ]
        self.assertEqual(ref_decl, res.decl)

        # test __eq__
        s1 = dds.Struct(text=text)
        s2 = dds.Struct("location",
                        stype='Structure',
                        decl=[
                            dds.VarLine('latitude', 'Float64'),
                            dds.VarLine('longitude', 'Float64')
                        ])
        self.assertEqual(s1, s2)

        # test __repr__
        ss = dds.Struct(text=text)
        ref = 'Struct("location", stype="Structure", decl=[VarLine("latitude", btype="Float64"), VarLine("longitude", btype="Float64")])'
        self.assertEqual(ref, ss.__repr__())

        # test __str__
        ss = dds.Struct(text=text)
        ref = 'Struct("location", stype="Structure", decl=[VarLine("latitude", btype="Float64"), VarLine("longitude", btype="Float64")])'
        self.assertEqual(ref, ss.__repr__())

        # test text_formatted
        ref = 'Structure {\n    Float64 latitude;\n    Float64 longitude;\n} location;'
        self.assertEqual(ref, ss.text_formatted())
        ref = 'Structure {\n  Float64 latitude;\n  Float64 longitude;\n} location;'
        self.assertEqual(ref, ss.text_formatted(2))

        # test text
        ref = 'Structure {Float64 latitude; Float64 longitude;} location;'
        self.assertEqual(ref, ss.text)

        # Invalid text -> null object
        text = ("""Structue {
                  Float64 latitude;
                  Float64 longitude;
                } location; """)
        ss = dds.Struct(text=text)
        self.assertEqual(ss, dds.Struct())

    def test_Grid(self):
        # test constructor
        g = dds.Grid()
        self.assertIsInstance(g, dds.Grid)

        # test parse()
        text = ("Grid {"
                " ARRAY:"
                "   Float32 tas[time = 8412][lat = 160][lon = 320];"
                " MAPS:"
                "   Float64 time[time = 8412];"
                "   Float64 lat[lat = 160];"
                "   Float64 lon[lon = 320];"
                "} tas;")
        g = dds.Grid(text=text)
        self.assertEqual(g.name, 'tas')
        self.assertEqual(g.stype, dds.SType.Grid)
        self.assertEqual(
            g.array,
            dds.VarLine("tas", "Float32",
                        "[time = 8412][lat = 160][lon = 320]"))
        self.assertEqual(g.maps, [
            dds.VarLine('time', 'Float64', '[time = 8412]'),
            dds.VarLine('lat', 'Float64', '[lat= 160]'),
            dds.VarLine('lon', 'Float64', '[lon= 320]')
        ])

        # test __eq__
        ref = dds.Grid('tas',
                       dds.SType.Grid,
                       array=dds.VarLine(
                           "tas", "Float32",
                           "[time = 8412][lat = 160][lon = 320]"),
                       maps=[
                           dds.VarLine('time', 'Float64', '[time = 8412]'),
                           dds.VarLine('lat', 'Float64', '[lat= 160]'),
                           dds.VarLine('lon', 'Float64', '[lon= 320]')
                       ])
        self.assertEqual(ref, g)

        # test __repr__
        ref = (
            'Grid("tas", stype="Grid", array=VarLine("tas", btype="Float32", '
            'arr=[ArrDecl("time", 8412), ArrDecl("lat", 160), ArrDecl("lon", 320)]), '
            'maps=[VarLine("time", btype="Float64", arr=[ArrDecl("time", 8412)]), '
            'VarLine("lat", btype="Float64", arr=[ArrDecl("lat", 160)]), '
            'VarLine("lon", btype="Float64", arr=[ArrDecl("lon", 320)])])')
        res = g.__repr__()
        self.assertEqual(ref, res)

        # test __str__
        ref = (
            'Grid(name="tas", stype="Grid", array=VarLine("tas", btype="Float32", '
            'arr=[ArrDecl("time", 8412), ArrDecl("lat", 160), ArrDecl("lon", 320)]), '
            'maps=[VarLine("time", btype="Float64", arr=[ArrDecl("time", 8412)]), '
            'VarLine("lat", btype="Float64", arr=[ArrDecl("lat", 160)]), '
            'VarLine("lon", btype="Float64", arr=[ArrDecl("lon", 320)])])')
        res = g.__str__()
        self.assertEqual(ref, res)

        # test text_formatted
        ref = 'Grid {\n ARRAY:\n    Float32 tas[time = 8412][lat = 160][lon = 320];\n MAPS:\n    Float64 time[time = 8412];\n    Float64 lat[lat = 160];\n    Float64 lon[lon = 320];\n} tas;'
        res = g.text_formatted()
        self.assertEqual(ref, res)

        # test text
        ref = 'Grid { ARRAY:Float32 tas[time = 8412][lat = 160][lon = 320]; MAPS:Float64 time[time = 8412];Float64 lat[lat = 160];Float64 lon[lon = 320]; } tas;'
        res = g.text
        self.assertEqual(ref, res)

    def test_check_braces_matching(self):
        dds.check_braces_matching(sample1)
        dds.check_braces_matching(sample2)

        text = '{ { }{ {}'
        with self.assertRaises(ValueError):
            dds.check_braces_matching(text)

        text = '{ { } }}}{}'
        with self.assertRaises(ValueError):
            dds.check_braces_matching(text)

    def test_parse_dataset(self):
        ref1 = dds.Struct(
            'CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1',
            'Dataset',
            decl=[
                dds.VarLine('lat',
                            btype=dds.BType.Float64,
                            arr=[dds.ArrDecl('lat', val=160)]),
                dds.VarLine('lat_bnds',
                            btype=dds.BType.Float64,
                            arr=[
                                dds.ArrDecl('lat', val=160),
                                dds.ArrDecl('bnds', val=2)
                            ]),
                dds.VarLine('lon',
                            btype=dds.BType.Float64,
                            arr=[dds.ArrDecl('lon', val=320)]),
                dds.VarLine('lon_bnds',
                            btype=dds.BType.Float64,
                            arr=[
                                dds.ArrDecl('lon', val=320),
                                dds.ArrDecl('bnds', val=2)
                            ]),
                dds.VarLine('height', btype=dds.BType.Float64),
                dds.VarLine('time',
                            btype=dds.BType.Float64,
                            arr=[dds.ArrDecl('time', val=8412)]),
                dds.VarLine('time_bnds',
                            btype=dds.BType.Float64,
                            arr=[
                                dds.ArrDecl('time', val=8412),
                                dds.ArrDecl('bnds', val=2)
                            ]),
                dds.Grid('tas',
                         array=dds.VarLine('tas',
                                           dds.BType.Float32,
                                           arr=[
                                               dds.ArrDecl('time', 8412),
                                               dds.ArrDecl('lat', 160),
                                               dds.ArrDecl('lon', 320)
                                           ]),
                         maps=[
                             dds.VarLine('time',
                                         dds.BType.Float64,
                                         arr=[dds.ArrDecl('time', 8412)]),
                             dds.VarLine('lat',
                                         dds.BType.Float64,
                                         arr=[dds.ArrDecl('lat', 160)]),
                             dds.VarLine('lon',
                                         dds.BType.Float64,
                                         arr=[dds.ArrDecl('lon', 320)])
                         ])
            ])

        res1 = dds.parse_dataset(sample1)
        self.assertEqual(ref1, res1)

        ref2 = dds.Struct(
            'data',
            'Dataset',
            decl=[
                dds.VarLine('catalog_number', btype='Int32'),
                dds.Struct('station',
                           stype='Sequence',
                           decl=[
                               dds.VarLine('experimenter', btype='String'),
                               dds.VarLine('time', btype='Int32'),
                               dds.Struct('location',
                                          stype='Structure',
                                          decl=[
                                              dds.VarLine('latitude',
                                                          btype='Float64'),
                                              dds.VarLine('longitude',
                                                          btype='Float64')
                                          ]),
                               dds.Struct('cast',
                                          stype='Sequence',
                                          decl=[
                                              dds.VarLine('depth',
                                                          btype='Float64'),
                                              dds.VarLine('salinity',
                                                          btype='Float64'),
                                              dds.VarLine('oxygen',
                                                          btype='Float64'),
                                              dds.VarLine('temperature',
                                                          btype='Float64')
                                          ])
                           ])
            ])
        res2 = dds.parse_dataset(sample2)
        for a in ref2.__dict__:
            self.assertEqual(getattr(ref2, a), getattr(res2, a))
        self.assertEqual(ref2, res2)

        ### not Dataset text raises ValueError.
        sample3 = """\
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
          } station;"""
        with self.assertRaises(ValueError):
            ref3 = dds.parse_dataset(sample3)

    def test_parse_declarations(self):
        text = """\
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
        """

        ref = [
            dds.VarLine(name="catalog_number", btype="Int32"),
            dds.Struct("station",
                       stype="Sequence",
                       decl=[
                           dds.VarLine("experimenter", btype="String"),
                           dds.VarLine("time", btype="Int32"),
                           dds.Struct("location",
                                      stype="Structure",
                                      decl=[
                                          dds.VarLine("latitude",
                                                      btype="Float64"),
                                          dds.VarLine("longitude",
                                                      btype="Float64")
                                      ]),
                           dds.Struct("cast",
                                      stype="Sequence",
                                      decl=[
                                          dds.VarLine("depth",
                                                      btype="Float64"),
                                          dds.VarLine("salinity",
                                                      btype="Float64"),
                                          dds.VarLine("oxygen",
                                                      btype="Float64"),
                                          dds.VarLine("temperature",
                                                      btype="Float64")
                                      ])
                       ])
        ]

        res = dds.parse_declarations(text)
        self.assertEqual(ref, res)

    def test_find_type_identifier(self):
        text = "Int32 catalog_number;"
        self.assertEqual(dds.find_type_identifier(text), 'B')

        text = "Float32 tas[time = 8412][lat = 160][lon = 320];"
        self.assertEqual(dds.find_type_identifier(text), 'B')

        text = """\
            Structure {
                Float64 latitude;
                Float64 longitude;
            } location;"""
        self.assertEqual(dds.find_type_identifier(text), 'S')

        text = """\
            Sequence {
                Float64 depth;
                Float64 salinity;
                Float64 oxygen;
                Float64 temperature;
            } cast;"""
        self.assertEqual(dds.find_type_identifier(text), 'S')

        text = """\
        Dataset {
            Int32 catalog_number;
            Sequence {
                String experimenter;
                Int32 time;
                Structure {
                    Float64 latitude;
                    Float64 longitude;
                } location;
            } station;
        } data;
        """
        self.assertEqual(dds.find_type_identifier(text), 'S')

        text = ("Grid {"
                " ARRAY:"
                "   Float32 tas[time = 8412][lat = 160][lon = 320];"
                " MAPS:"
                "   Float64 time[time = 8412];"
                "   Float64 lat[lat = 160];"
                "   Float64 lon[lon = 320];"
                "} tas;")
        self.assertEqual(dds.find_type_identifier(text), 'G')

        text = (" ARRAY:"
                "   Float32 tas[time = 8412][lat = 160][lon = 320];"
                " MAPS:"
                "   Float64 time[time = 8412];"
                "   Float64 lat[lat = 160];"
                "   Float64 lon[lon = 320];")
        self.assertIsNone(dds.find_type_identifier(text))

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
        ref = dds.Struct("location",
                         stype="Structure",
                         decl=[
                             dds.VarLine("latitude", btype="Float64"),
                             dds.VarLine("longitude", btype="Float64")
                         ])
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
        ref = dds.VarLine("depth", "Float64")
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
        text = "height;"
        res = dds.parse_arrdecls(text=text)
        ref = None
        # print(res)
        self.assertEqual(ref, res)


def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()
