#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to parse DDS (Dataset Descriptor Structure) used in OPeNDAP.

DDS
---

For the definition of DDS, see `OpenDAP UserGuide`_.
In this module, we change the notation in the DDS syntax as follows:

    | *declarations* := list(*declaration*)
    | *declaration* := *Var* | *Struct*
    | *Struct* := *stype* { *declarations* } (*name* | *name* *arr*)
    | *stype* := Dataset|Structure|Sequence|Grid
    | *Grid* := Grid { ARRAY: *declaration* MAPS: *declarations* } (*name* | *name* *arr*)
    | *Var* := *btype* (*name* | *name* *arr*)
    | *btype* := Byte|Int32|UInt32|Float64|String|Url| ...
    | *arr* := [integer] | [*name* = integer]

As you can see from above syntax, one *Struct* can contain other *Struct* recursively, and consists
the tree structure. The root of the tree must be one "Dataset".

In this module, each element of above syntax is implemented as one class.

Basic Usage
-----------

Text form of DDS will be obtained by, for example,
:meth:`.ESGFDataInfo.getDDS`. Use :func:`parse_dataset` to parse it to
get the tree structure. The root of the tree is a :class:`Dataset`
instance, and you can access nodes and leafs of the tree by dot
notation (see also 'Example' section below)::

    ds = parse_dataset(text=sample1)
    ds.tas  # Grid('tas, arrary=Var(tas, ...), maps={'time':..., 'lat':..., 'lon':...})
    ds.tas.array.arr[0]  # Arr('time', 8412)


.. _OpenDAP UserGuide: https://opendap.github.io/documentation/UserGuideComprehensive.html#DDS

Example:

    >>> sample1 = '''
    ... Dataset {
    ...     Float64 lat[lat = 160];
    ...     Float64 lat_bnds[lat = 160][bnds = 2];
    ...     Float64 lon[lon = 320];
    ...     Float64 lon_bnds[lon = 320][bnds = 2];
    ...     Float64 height;
    ...     Float64 time[time = 8412];
    ...     Float64 time_bnds[time = 8412][bnds = 2];
    ...     Grid {
    ...      ARRAY:
    ...         Float32 tas[time = 8412][lat = 160][lon = 320];
    ...      MAPS:
    ...         Float64 time[time = 8412];
    ...         Float64 lat[lat = 160];
    ...         Float64 lon[lon = 320];
    ...     } tas;
    ... } CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1;'''
    >>> sample1_struct = Dataset(
    ...    'CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1',
    ...    {
    ...        'lat':
    ...        Var('lat', 'Float64', arr=[Arr('lat', 160)]),
    ...        'lat_bnds':
    ...        Var('lat_bnds', 'Float64', arr=[Arr('lat', 160),
    ...                                        Arr('bnds', 2)]),
    ...        'lon':
    ...        Var('lon', 'Float64', arr=[Arr('lon', 320)]),
    ...        'lon_bnds':
    ...        Var('lon_bnds', 'Float64', arr=[Arr('lon', 320),
    ...                                        Arr('bnds', 2)]),
    ...        'height':
    ...        Var('height', 'Float64'),
    ...        'time':
    ...        Var('time', 'Float64', arr=[Arr('time', 8412)]),
    ...        'time_bnds':
    ...        Var('time_bnds', 'Float64', arr=[Arr('time', 8412),
    ...                                         Arr('bnds', 2)]),
    ...        'tas':
    ...        Grid('tas',
    ...             array=Var(
    ...                 'tas',
    ...                 'Float32',
    ...                 arr=[Arr('time', 8412),
    ...                      Arr('lat', 160),
    ...                      Arr('lon', 320)]),
    ...             maps={
    ...                 'time': Var('time', 'Float64', arr=[Arr('time', 8412)]),
    ...                 'lat': Var('lat', 'Float64', arr=[Arr('lat', 160)]),
    ...                 'lon': Var('lon', 'Float64', arr=[Arr('lon', 320)])
    ...             })
    ...    })
    >>> sample1_struct == parse_dataset(sample1)
    True

    >>> from cmiputil import dds
    >>> sample2 = '''
    ... Dataset {
    ...   Int32 catalog_number;
    ...   Sequence {
    ...     String experimenter;
    ...     Int32 time;
    ...     Structure {
    ...       Float64 latitude;
    ...       Float64 longitude;
    ...     } location;
    ...     Sequence {
    ...       Float64 depth;
    ...       Float64 salinity;
    ...       Float64 oxygen;
    ...       Float64 temperature;
    ...     } cast;
    ...   } station;
    ... } data;
    ... '''
    >>> sample2_struct = Dataset(
    ...     'data', {
    ...         'catalog_number':
    ...         Var('catalog_number', 'Int32'),
    ...         'station':
    ...         Sequence(
    ...             'station', {
    ...                 'experimenter':
    ...                 Var('experimenter', 'String'),
    ...                 'time':
    ...                 Var('time', 'Int32'),
    ...                 'location':
    ...                 Structure(
    ...                     'location', {
    ...                         'latitude': Var('latitude', 'Float64'),
    ...                         'longitude': Var('longitude', 'Float64')
    ...                     }),
    ...                 'cast':
    ...                 Sequence(
    ...                     'cast', {
    ...                         'depth': Var('depth', 'Float64'),
    ...                         'salinity': Var('salinity', 'Float64'),
    ...                         'oxygen': Var('oxygen', 'Float64'),
    ...                         'temperature': Var('temperature', 'Float64')
    ...                     })
    ...             })
    ...     })
    >>> sample2_struct == parse_dataset(sample2)
    True

    >>> sample3 = '''
    ... Dataset {
    ...     Structure {
    ...         Float64 lat;
    ...         Float64 lon;
    ...     } location;
    ...     Structure {
    ...         Int32 minutes;
    ...         Int32 day;
    ...         Int32 year;
    ...     } time;
    ...     Float64 depth[500];
    ...     Float64 temperature[500];
    ... } xbt-station;
    ... '''
    >>> sample3_struct = Dataset(
    ...     'xbt-station', {
    ...         'location':
    ...         Structure('location', {
    ...             'lat': Var('lat', 'Float64'),
    ...             'lon': Var('lon', 'Float64')
    ...         }),
    ...         'time':
    ...         Structure(
    ...             'time', {
    ...                 'minutes': Var('minutes', 'Int32'),
    ...                 'day': Var('day', 'Int32'),
    ...                 'year': Var('year', 'Int32')
    ...             }),
    ...         'depth':
    ...         Var('depth', 'Float64', arr=[Arr('', 500)]),
    ...         'temperature':
    ...         Var('temperature', 'Float64', arr=[Arr('', 500)])
    ...     })
    >>> sample3_struct == parse_dataset(sample3)
    True
"""

import enum
import re
import textwrap as tw
from pprint import pprint

_debug = False


def _enable_debug():
    global _debug
    _debug = True


def _disable_debug():
    global _debug
    _debug = False


def _debug_write(text):
    global _debug
    if _debug:
        print(text)


class BType(enum.Enum):
    """
    Values for :attr:`.Var.btype`.
    """
    Byte = 'Byte'
    Int16 = 'Int16'
    Int32 = 'Int32'
    UInt32 = 'UInt32'
    Float32 = 'Float32'
    Float64 = 'Float64'
    String = 'String'
    Url = 'Url'


class SType(enum.Enum):
    """
    Values for :attr:`Struct.stype`
    """
    Dataset = 'Dataset'
    Structure = 'Structure'
    Sequence = 'Sequence'
    Grid = 'Grid'


_idents_btype = [t.name for t in BType]
_idents_stype = [t.name for t in SType]
_idents = _idents_btype + _idents_stype
_pat_idents_stype = re.compile(r'^\s*(' + '|'.join(_idents_stype) + ')')
_pat_ident = re.compile(r'^\s*(' + '|'.join(_idents) + ')')
_pat_struct = re.compile(
    r'^\s*(' + r'|'.join(_idents_stype) + r')\s*\{(.*)\}\s*(\S+);\s*',
    re.DOTALL)
_pat_dataset = re.compile(r'^\s*Dataset\s+'
                          r'\{(.+)\}\s*(\S+);\s*$', re.DOTALL)
_pat_grid = re.compile(
    r'^\s*Grid\s*\{\s*Array:(.+)Maps:'
    r'\s*(.+)\s*\}\s*(\w+);', re.IGNORECASE | re.DOTALL)
_pat_varline = re.compile(r'^\s*(\w+)\s*(\w+)(\[.+\])*;\s*$', re.DOTALL)
_pat_arrdecl = re.compile(r'\[(\w+?)\s*=\s*(\d+)\]')
_pat_arrdecl_valonly = re.compile(r'^s*\[(\d+)]')
_pat_arrdecl_line = re.compile(r'\[(?:\w+?\s*=)*\s*\d+\]')


class Decls(dict):
    """
    Class for *declarations*.

    | *declarations* := list(*declaration*)

    In this module, *declarations* are expressed as `dict`, not
    `list`. At this point, this class is just an alias for `dict`.

    """
    pass


class Decl:
    """
    Class for *declaration*, that is, base class for :class:`Var`
    and :class:`Struct`. No need to use this class explicitly.

    | *declaration* := *Var* | *Struct*

    """

    def __init__(self, name=''):
        self.name = name

    def __eq__(self, other):
        _debug_write(f'Decl.__eq__():{type(self)},{type(other)}')
        if not isinstance(other, type(self)):
            return False
        res = [getattr(self, a) == getattr(other, a) for a in self.__dict__]
        return all(res)

    def text_formatted(self, indent=None, linebreak=True):
        pass


class Struct(Decl):
    """
    Class for *struct*, that is, base class for :class:`Structure`,
    :class:`Sequence`, :class:`Grid` and :class:`Dataset`.
    Do not use this directly.

    | *struct* := *stype* { *declarations* } *var*
    | *stype* := Dataset|Structure|Sequence|Grid

    You can access items of ``self.decl`` as if they are the attribute
    of this class, via dot notation.

    Examples:

        >>> text = '''
        ... Sequence {
        ...   Float64 depth;
        ...     Float64 salinity;
        ...     Float64 oxygen;
        ...     Float64 temperature;
        ...   } cast;'''
        >>> s = Sequence(text=text)
        >>> s.salinity
        Var('salinity', 'Float64')

        >>> text = '''
        ... Dataset {
        ...   Int32 catalog_number;
        ...   Sequence {
        ...     String experimenter;
        ...     Int32 time;
        ...     Structure {
        ...       Float64 latitude;
        ...       Float64 longitude;
        ...     } location;
        ...   } station;
        ... } data;'''
        >>> d = parse_dataset(text)
        >>> d.station.location.latitude
        Var('latitude', 'Float64')

    Attributes:
        name(str): *name*
        stype(SType): *stype*
        decl(Decls)): *declarations*

    """

    stype = None

    def __init__(self, name='', decl=None, text=None):
        """
        Parameters:
            name(str): *name*
            decl(str or Decls)): *declarations*
            text(str): text to be parsed.

        If `text` is *not* ``None``, other attributes are overridden by
        the result of :meth:`.parse` or left untouced..
        """

        if text:
            _debug_write(f'{self.__class__.__name__}' f"text='{text}'")
            self.parse(text)
        else:
            self.name = name

            if decl is None:
                self.decl = None
            elif isinstance(decl, dict):
                self.decl = decl
            elif type(decl) is str:
                self.decl = parse_declarations(decl)
            else:
                raise TypeError(f'decl={decl} is invalid type: {type(decl)}')

    def parse(self, text):
        """
        Parse `text` to construct :class:`Struct`.

        If given `text` is not valid for each subclass, the instance
        is left as 'null' instance.
        """
        _debug_write(f'{self.__class__.__name__}.parse: text="{text}"')
        res = _pat_struct.match(text)
        if not res:
            return None

        _debug_write(f'{self.__class__.__name__}.parse:name="{res.group(3)}"')
        _debug_write(f'{self.__class__.__name__}.parse:decl="{res.group(2)}"')
        if self.stype and self.stype == SType(res.group(1)):
            self.decl = parse_declarations(res.group(2))
            self.name = res.group(3)

    def __getattr__(self, key):
        # print('__getattr__() called')
        if key in self.decl:
            return self.decl[key]
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __getitem__(self, key):
        # print('__getitem__() called')
        if key in self.decl:
            return self.decl[key]
        else:
            raise KeyError(f"'{key}'")

    def __contains__(self, item):
        # print('__contains__() called')
        return (item in self.__dict__) or (item in self.decl)

    def __repr__(self):
        if self.name:
            name = f"'{self.name}'"
        else:
            name = ''
        if self.decl:
            # decl = f'decl={self.decl.__repr__()}'
            decl = f'{self.decl.__repr__()}'
        else:
            decl = ''

        res = ', '.join([l for l in [name, decl] if l])
        return (f'{self.__class__.__name__}({res})')

    def __str__(self):
        return self.text_formatted()

    def text_formatted(self, indent=4, linebreak=True):
        """
        Return formatted text.
        """
        _debug_write(
            f'{self.__class__.__name__}.text_formatted:indent={indent},linebreak={linebreak}'
        )
        if self.name:
            name = self.name + ';'
        else:
            name = ''
        if self.stype:
            stype = f'{self.stype.name}'
        else:
            stype = ''
        if self.decl:
            if linebreak:
                lb = '\n'
            else:
                lb = ''

            decl = f'{lb}'.join([
                self.decl[d].text_formatted(indent, linebreak)
                for d in self.decl if d
            ])
            decl = tw.indent(decl, ' ' * indent)
            decl = f'{lb}'.join(('{', decl, '}'))
        else:
            decl = ''
        if name == '' and decl == '':
            res = ''
        else:
            res = ' '.join([l for l in [stype, decl, name] if l])
        return res

    @property
    def text(self):
        """
        Text to construct this instance.
        """
        return self.text_formatted(indent=0, linebreak=False)


class Dataset(Struct):
    """
    Class for *Dataset*.

    See :class:`Struct`.
    """

    stype = SType.Dataset

    def __init__(self, name='', decl=None, text=None):
        super().__init__(name, decl=decl)
        if text:
            super().__init__(text=text)


class Structure(Struct):
    """
    Class for *Structure*.

    See :class:`Struct`.
    """

    stype = SType.Structure

    def __init__(self, name='', decl=None, text=None):
        super().__init__(name, decl=decl)
        if text:
            super().__init__(text=text)


class Sequence(Struct):
    """
    Class for *Sequence*.

    See :class:`Struct`.


    Examples:

        >>> text = '''
        ...     Sequence {
        ...       Float64 depth;
        ...       Float64 salinity;
        ...       Float64 oxygen;
        ...       Float64 temperature;
        ...     } cast;'''
        >>> Sequence(text=text)
        Sequence('cast', {'depth': Var('depth', 'Float64'), 'salinity': Var('salinity', 'Float64'), 'oxygen': Var('oxygen', 'Float64'), 'temperature': Var('temperature', 'Float64')})
    """

    stype = SType.Sequence

    def __init__(self, name='', decl=None, text=None):
        super().__init__(name, decl=decl)
        if text:
            super().__init__(text=text)


class Grid(Struct):
    """
    Class for *Grid*.

    | *Grid* := Grid { ARRAY: *declaration* MAPS: *declarations* } (*name* | *name* *arr*)

    Attributes:

        name(str): *name*
        stype(SType): *stype*
        array(Decl): ARRAY *declaration*
        maps(Decls): MAPS *declarations*


    Examples:

        >>> text = '''
        ...     Grid {
        ...      ARRAY:
        ...         Float32 tas[time = 8412][lat = 160][lon = 320];
        ...      MAPS:
        ...         Float64 time[time = 8412];
        ...         Float64 lat[lat = 160];
        ...         Float64 lon[lon = 320];
        ...     } tas;'''
        >>> Grid(text=text)
        Grid('tas', array=Var('tas', 'Float32', arr=[Arr('time', 8412), Arr('lat', 160), Arr('lon', 320)]), maps={'time': Var('time', 'Float64', arr=[Arr('time', 8412)]), 'lat': Var('lat', 'Float64', arr=[Arr('lat', 160)]), 'lon': Var('lon', 'Float64', arr=[Arr('lon', 320)])})

    """

    stype = SType.Grid

    def __init__(self, name='', array=None, maps=None, text=None):
        """
        Parameters:
            name(str): *name*
            stype(str or SType): *stype*
            array(Decl): ARRAY *declaration*
            maps(Decls): MAPS *declarations*
            text(str): text to be parsed.

        If `text` is not ``None``, other attributes are overridden by
        the result of :meth:`.parse`.
        """
        super().__init__(name, decl=None)
        self.array = array
        self.maps = maps
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`Grid`.
        """
        _debug_write(f"{self.__class__.__name__}.parse: text='{text}'")
        res = _pat_grid.match(text)
        if res:
            _debug_write(
                f"{self.__class__.__name__}.parse: array_line='{res.group(1).strip()}'"
            )
            _debug_write(
                f"{self.__class__.__name__}.parse: maps_line='{res.group(2).strip()}'"
            )
            self.array = Var(text=res.group(1))
            self.maps = parse_declarations(res.group(2))
            self.name = res.group(3)

    def __getattr__(self, key):
        # print('__getattr__() called')
        if key == self.array.name:
            return self.array
        elif key in self.maps:
            return self.maps[key]
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __getitem__(self, key):
        # print('__getitem__() called')
        if key == self.array.name:
            return self.array
        elif key in self.maps:
            return self.maps[key]
        else:
            raise KeyError(f"'{key}'")

    def __contains__(self, item):
        # print('__contains__() called')
        return (item in self.__dict__) or (item in self.maps) or (
            item == self.array.name)

    def __repr__(self):
        if self.name:
            name = f"'{self.name}'"
        else:
            name = ''
        if self.array:
            array = f'array={self.array.__repr__()}'
        else:
            array = ''
        if self.maps:
            maps = f'maps={self.maps.__repr__()}'
        else:
            maps = ''

        res = ', '.join([l for l in [name, array, maps] if l])
        return (f'{self.__class__.__name__}({res})')

    def __str__(self):
        return self.text_formatted()

    def text_formatted(self, indent=4, linebreak=True):
        """
        Return formatted text.
        """
        _debug_write(
            f'{self.__class__.__name__}.text_formatted:indent={indent},linebreak={linebreak}'
        )
        if self.name:
            name = self.name + ';'
        else:
            name = ''
        if self.stype:
            stype = f'{self.stype.name}'
        else:
            stype = ''
        if self.array is None or self.maps is None:
            decl = ''
        else:
            if linebreak:
                lb = '\n'
            else:
                lb = ''

            array = f' ARRAY:{lb}' + tw.indent(self.array.text, ' ' * indent)
            ll = f'{lb}'.join([
                self.maps[d].text_formatted(indent, linebreak)
                for d in self.maps if d
            ])
            maps = f' MAPS:{lb}' + tw.indent(ll, ' ' * indent)
            decl = f'{lb}'.join(('{', array, maps, '}'))
        if name == '' and decl == '':
            res = ''
        else:
            res = ' '.join([l for l in [stype, decl, name] if l])
        return res

    @property
    def text(self):
        """
        Text to construct this instance.
        """
        return self.text_formatted(indent=0, linebreak=False)


class Var(Decl):
    """
    Class for *Var*.

    | *Var* := *basetype* (*name*|*name* *arr*)

    Attributes:
        name (str): *name*
        btype (BType): *basetype*
        arr (list(Arr)): *array-decl*
    """

    def __init__(self, name='', btype=None, arr=None, text=None):
        """
        Parameters:
            name(str): *name*
            btype(str or BType): *basetype*
            arr(Arr or list(Arr)): *array-decl*
            text(str): text to be parsed

        Raises:
            TypeError: if `btype` or `arr` is invalid

        If `text` is not ``None``, other attributes are overridden by
        the result of :meth:`.parse`.
        """
        self.name = name
        if btype is None:
            self.btype = btype
        elif isinstance(btype, BType):
            self.btype = btype
        elif type(btype) is str:
            self.btype = BType(btype)
        else:
            raise TypeError(f'btype={btype} is invalid type: {type(btype)}')
        if arr is None or arr == []:
            self.arr = None
        elif isinstance(arr, Arr):
            self.arr = arr
        elif type(arr) is list and isinstance(arr[0], Arr):
            self.arr = arr
        elif isinstance(arr, str):
            self.arr = parse_arrdecls(arr)
        else:
            raise TypeError(f'arr={arr} is invalid type: {type(arr)}')
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`Var`.
        """

        _debug_write(f'Var.parse():text="{text[:60]}"')
        res = _pat_varline.match(text)
        if res:
            try:
                self.btype = BType(res.group(1))
            except ValueError:
                return None
            self.name = res.group(2)
            if res.group(3):
                self.arr = parse_arrdecls(res.group(3))

    def __repr__(self):
        if self.name == '':
            name = ''
        else:
            name = f"'{self.name}'"
        if self.btype is None:
            btype = ''
        else:
            btype = f"'{self.btype.name}'"

        if self.arr:
            arr = 'arr=' + str([a for a in self.arr])
        else:
            arr = ''

        args = ', '.join([elem for elem in [name, btype, arr] if elem != ''])

        return f'Var({args})'

    def __str__(self):
        return self.text_formatted()

    def text_formatted(self, indent=None, linebreak=None):
        """
        Formatted text expression of this instance.

        `indent` and `linebreak` are dummy arguments here.
        """
        if self.btype is None:
            res = ''
        else:
            res = f'{self.btype.name}'
        if self.name != '':
            res += f' {self.name}'
        if self.arr:
            res += ''.join([a.text for a in self.arr])
        if res:
            res += ';'
        return res

    @property
    def text(self):
        """
        Text to construct this instance.
        """
        return self.text_formatted()


class Arr():
    """
    Class for *arr*.

    | *arr* := [integer] | [*name* = integer]

    As a text form::

        text = '[time = 8412]'
        text = '[500]'

    Example:

        >>> text = '[lat = 160];'
        >>> Arr(text=text)
        Arr('lat', 160)

        >>> text = '[500];'
        >>> Arr(text=text)
        Arr('', 500)

    Attributes:
        name (str) : *name*
        val (int) : integer

    """

    def __init__(self, name='', val=None, text=None):
        self.name = name
        self.val = val
        if text:
            self.parse(text)

    def parse(self, text):
        _debug_write(f"{self.__class__.__name__}.parse():text='{text}'")
        res = _pat_arrdecl.match(text)
        if res:
            self.name = res.group(1)
            self.val = int(res.group(2))
        else:
            res = _pat_arrdecl_valonly.match(text)
            if res:
                self.val = int(res.group(1))
        _debug_write(
            f"{self.__class__.__name__}.parse():name='{self.name}',val='{self.val}'"
        )

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        res = [getattr(self, a) == getattr(other, a) for a in self.__dict__]
        return all(res)

    def __repr__(self):
        if self.name:
            return f"Arr('{self.name}', {self.val})"
        elif self.val:
            return f"Arr('', {self.val})"
        else:
            return ''

    def __str__(self):
        if self.name:
            return f"Arr(name='{self.name}', val={self.val})"
        elif self.val:
            return f"[{self.val}]"
        else:
            return ''

    def text_formatted(self, indent=None, linebreak=None):
        """
        Text form of *arr*.

        `indent` and `linebreak` are dummy here.
        """
        if self.name:
            return f"[{self.name} = {self.val}]"
        elif self.val:
            return f"[{self.val}]"
        else:
            return ''

    @property
    def text(self):
        return self.text_formatted()


def check_braces_matching(text):
    """
    Check if braces(``{`` and ``}``) in given `text` match.

    Raises `ValueError` unless match.

    Examples:

        >>> text = 'Dataset{varline} hoge'
        >>> check_braces_matching(text)  # True

        >>> text = 'Struct{ Sequence{Var} fuga }} hoge'
        >>> check_braces_matching(text)
        Traceback (most recent call last):
            ...
        ValueError: braces do not match: too many right braces: 1 more.

        >>> text = 'Struct{ Sequence{{Var} fuga } hoge'
        >>> check_braces_matching(text)
        Traceback (most recent call last):
            ...
        ValueError: braces do not match: too many left braces: 1 more.

    """

    count = 0
    maxcount = 0
    _debug_write('check_braces_matching:')
    for n, c in enumerate(text):
        if c == '{':
            count += 1
            maxcount = max(maxcount, count)
            _debug_write(f'n={n}, count={count}')
        if c == '}':
            count -= 1
            _debug_write(f'n={n}, count={count}')
        if (count < 0):
            raise ValueError(f'braces do not match: '
                             f'too many right braces: {abs(count)} more.')
    if count > 0:
        raise ValueError(f'braces do not match: '
                         f'too many left braces: {count} more.')


def parse_dataset(text):
    """
    Parse toplevel *dataset*.

    *dataset* := Dataset { *declarations* } *name*;
    """
    check_braces_matching(text)

    # Dataset is the toplevel, *greedy* is preferable.
    res = _pat_dataset.match(text)
    if res:
        dataset = Dataset(text=text)
    else:
        raise ValueError('Given text is not the Dataset definition.')

    return dataset


def parse_declarations(text):
    """
    Return :class:`Decls`, dict of {`name`: *Decl*} parsed from `text`.
    """
    # _debug_write(f'parse_declarations:text="{text}"')
    # _debug_write('======parse_declarations======')
    res = Decls()
    while text != '':
        _debug_write('=' * 20)
        _debug_write(f"parse_declarations:text='{text}'")
        res_ident = _pat_ident.match(text)
        if res_ident:
            ident = res_ident.group(1)
            _debug_write(f"parse_declarations:ident:'{ident}'")
            if ident in _idents_stype:
                ss, rest = pop_struct(text)
                # res.append(ss)
                res[ss.name] = ss
                text = rest.strip()
            elif ident in _idents_btype:
                vl, rest = pop_varline(text)
                # res.append(vl)
                res[vl.name] = vl
                text = rest.strip()
        else:
            return None
    return res


def pop_struct(text):
    """
    Pop one :class:`Struct`-derived instance parsed from the
    first part of `text`, return it and the rest of `text`.
    """

    leftpos = text.find('{')
    if (leftpos < 0):  # no braces, no Struct instance.
        return None

    nestlevel = 0
    for n, c in enumerate(text[leftpos:]):
        if c == '{':
            nestlevel += 1
        if c == '}':
            nestlevel -= 1
        if nestlevel == 0:
            rightpos = leftpos + n
            break

    lastdelim = rightpos + text[rightpos:].find(';') + 1
    _debug_write(f"parse_struct:lastdelim='{lastdelim}'")

    sline = text[:lastdelim].strip()
    rest = text[lastdelim:].strip()

    res = _pat_idents_stype.match(text)
    if res:
        ident = res.group(1)
        _debug_write(f"parse_struct:ident='{ident}'")
        _debug_write(f"parse_struct:sline='{sline}'")
        if ident == 'Grid':
            ss = Grid(text=sline)
        elif ident == 'Dataset':
            ss = Dataset(text=sline)
        elif ident == 'Structure':
            ss = Structure(text=sline)
        elif ident == 'Sequence':
            ss = Sequence(text=sline)
    else:
        raise ValueError('Invalid text')

    return ss, rest


def pop_varline(text):
    """
    Pop one :class:`Var` instance parsed from the first part of
    `text`, return it and rest of the `text`.
    """
    _debug_write(f"pop_varline:text='{text}'")
    pat_split = re.compile(r' *(.+?;) *(.*)', re.DOTALL)

    res = pat_split.match(text)
    vline = res.group(1)
    try:
        rest = res.group(2).strip()
    except AttributeError:
        rest = ''
    _debug_write(f"pop_varline:vline='{vline}'")
    _debug_write(f"pop_varline:rest='{rest}'")

    vl = Var(text=vline)

    return vl, rest


def parse_arrdecls(text):
    """
    Parse `text` contains multiple :class:`Arr` definitions and return
    a list of them.
    """
    _debug_write(f"parse_arrdecls:text='{text}'")
    res = _pat_arrdecl_line.findall(text)
    if res:
        return [Arr(text=l) for l in res]
    else:
        return None


# for debug use...
_sample1 = '''
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

_sample1_struct = Dataset(
    'CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1',
    {
        'lat':
        Var('lat', 'Float64', arr=[Arr('lat', 160)]),
        'lat_bnds':
        Var('lat_bnds', 'Float64', arr=[Arr('lat', 160),
                                        Arr('bnds', 2)]),
        'lon':
        Var('lon', 'Float64', arr=[Arr('lon', 320)]),
        'lon_bnds':
        Var('lon_bnds', 'Float64', arr=[Arr('lon', 320),
                                        Arr('bnds', 2)]),
        'height':
        Var('height', 'Float64'),
        'time':
        Var('time', 'Float64', arr=[Arr('time', 8412)]),
        'time_bnds':
        Var('time_bnds', 'Float64', arr=[Arr('time', 8412),
                                         Arr('bnds', 2)]),
        'tas':
        Grid('tas',
             array=Var(
                 'tas',
                 'Float32',
                 arr=[Arr('time', 8412),
                      Arr('lat', 160),
                      Arr('lon', 320)]),
             maps=Decls({
                 'time': Var('time', 'Float64', arr=[Arr('time', 8412)]),
                 'lat': Var('lat', 'Float64', arr=[Arr('lat', 160)]),
                 'lon': Var('lon', 'Float64', arr=[Arr('lon', 320)])
             }))
    })

_sample2 = '''
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

_sample2_struct = Dataset(
    'data', {
        'catalog_number':
        Var('catalog_number', 'Int32'),
        'station':
        Sequence(
            'station', {
                'experimenter':
                Var('experimenter', 'String'),
                'time':
                Var('time', 'Int32'),
                'location':
                Structure(
                    'location', {
                        'latitude': Var('latitude', 'Float64'),
                        'longitude': Var('longitude', 'Float64')
                    }),
                'cast':
                Sequence(
                    'cast', {
                        'depth': Var('depth', 'Float64'),
                        'salinity': Var('salinity', 'Float64'),
                        'oxygen': Var('oxygen', 'Float64'),
                        'temperature': Var('temperature', 'Float64')
                    })
            })
    })

_sample3 = '''\
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

_sample3_struct = Dataset(
    'xbt-station', {
        'location':
        Structure('location', {
            'lat': Var('lat', 'Float64'),
            'lon': Var('lon', 'Float64')
        }),
        'time':
        Structure(
            'time', {
                'minutes': Var('minutes', 'Int32'),
                'day': Var('day', 'Int32'),
                'year': Var('year', 'Int32')
            }),
        'depth':
        Var('depth', 'Float64', arr=[Arr('', 500)]),
        'temperature':
        Var('temperature', 'Float64', arr=[Arr('', 500)])
    })

# _enable_debug()
#_disable_debug()


def _test_mod():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test_mod()
