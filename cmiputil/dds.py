#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to parse DDS.

Text form of DDS will be obtained by :meth:`.ESGFDataInfo.getDDS`. Use
:func:`parse_dataset` to parse it and return the tree structure of
DDS.

You can get any attributes by :func:`hogehoge`.

For the definition of DDS, see `OpenDAP UserGuide`_.

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
    ... } CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1;
    ... '''
    >>> res = parse_dataset(text=sample1)
    >>> ref = Dataset('CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1', decl=[
    ...     VarLine("lat", btype="Float64", arr=[
    ...         ArrDecl(name="lat", val=160)]),
    ...     VarLine("lat_bnds", btype="Float64", arr=[
    ...         ArrDecl(name="lat", val=160),
    ...         ArrDecl(name="bnds", val=2)]),
    ...     VarLine("lon", btype="Float64", arr=[
    ...         ArrDecl(name="lon", val=320)]),
    ...     VarLine("lon_bnds", btype="Float64", arr=[
    ...         ArrDecl(name="lon", val=320),
    ...         ArrDecl(name="bnds", val=2)]),
    ...     VarLine("height", btype="Float64"),
    ...     VarLine("time", btype="Float64", arr=[
    ...         ArrDecl(name="time", val=8412)]),
    ...     VarLine("time_bnds", btype="Float64", arr=[
    ...         ArrDecl(name="time", val=8412),
    ...         ArrDecl(name="bnds", val=2)]),
    ...     Grid("tas",
    ...         array = VarLine("tas", btype="Float32", arr=[
    ...            ArrDecl(name="time", val=8412),
    ...            ArrDecl(name="lat", val=160),
    ...            ArrDecl(name="lon", val=320)]),
    ...         maps = [
    ...            VarLine("time", btype="Float64", arr=[
    ...               ArrDecl(name="time", val=8412)]),
    ...            VarLine("lat", btype="Float64", arr=[
    ...               ArrDecl(name="lat", val=160)]),
    ...            VarLine("lon", btype="Float64", arr=[
    ...               ArrDecl(name="lon", val=320)])])])
    >>> ref == res
    True

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
    >>> res = parse_dataset(text=sample2)
    >>> ref = Dataset('data', decl=[
    ...     VarLine('catalog_number', btype=BType.Int32),
    ...     Sequence('station', decl=[
    ...         VarLine('experimenter', btype=BType.String),
    ...         VarLine('time', btype=BType.Int32),
    ...         Structure('location', decl=[
    ...             VarLine('latitude', btype=BType.Float64),
    ...             VarLine('longitude', btype=BType.Float64) ]),
    ...         Sequence('cast', decl=[
    ...             VarLine('depth', btype=BType.Float64),
    ...             VarLine('salinity', btype=BType.Float64),
    ...             VarLine('oxygen', btype=BType.Float64),
    ...             VarLine('temperature', btype=BType.Float64)])])])
    >>> res == ref
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
    Values for :attr:`.VarLine.btype`.
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


class Declaration:
    """
    Base class for :class:`VarLine` and :class:`Struct`

    | *declarations* := list(*declaration*)
    | *declaration* := *VarLine* or *Struct*

    """

    def __init__(self, name=''):
        self.name = name

    def __eq__(self, other):
        _debug_write(f'Declaration.__eq__():{type(self)},{type(other)}')
        if not isinstance(other, type(self)):
            return False
        res = [getattr(self, a) == getattr(other, a) for a in self.__dict__]
        return all(res)

    def text_formatted(self, indent=None, linebreak=True):
        pass


class Struct(Declaration):
    """
    Base class for *Struct* type.

    Do not use this directly.

    | *Struct* := *stype* { *declarations* } *var*
    | *stype* := Dataset|Structure|Sequence|Grid

    Attributes:
        name(str): *name*
        stype(SType): *stype*
        decl(list(Declarations): *declarations*

    """

    def __init__(self, name='', stype=None, decl=None, text=None):
        """
        Parameters:
            name(str): *name*
            stype(str or SType): *stype*
            decl(list(Declarations): *declarations*
            text(str): text to be parsed.

        Raises:
            TypeError: if `stype` is invalid.

        If `text` is not ``None``, other attributes are overridden by
        the result of :meth:`.parse`.
        """

        if text:
            self.parse(text)
        else:
            self.name = name

            if isinstance(stype, SType):
                self.stype = stype
            elif isinstance(stype, str):
                self.stype = SType(stype)
            else:
                raise TypeError(
                    f'stype={stype} is invalid type: {type(stype)}')

            if decl is None:
                self.decl = None
            elif type(decl) is list and isinstance(decl[0], Declaration):
                self.decl = decl
            elif type(decl) is str:
                self.decl = parse_declarations(decl)
            else:
                raise TypeError(f'decl={decl} is invalid type: {type(decl)}')

    def parse(self, text):
        """
        Parse `text` to construct :class:`Struct`.
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

    def __repr__(self):
        if self.name:
            name = f'"{self.name}"'
        else:
            name = ''
        if self.decl:
            decl = f'decl={self.decl.__repr__()}'
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
        if self.name:
            name = self.name + ';'
        else:
            name = ''
        if self.decl:
            if linebreak:
                decl = '\n'.join([
                    d.text_formatted(indent, linebreak) for d in self.decl if d
                ])
                decl = tw.indent(decl, ' ' * indent)
                decl = '\n'.join(('{', decl, '}'))
            else:
                decl = ' '.join([d.text for d in self.decl if d])
                decl = ''.join(('{', decl, '}'))
        else:
            decl = ''
        if self.stype:
            stype = f'{self.stype.name}'
        else:
            stype = ''

        res = ' '.join([l for l in [stype, decl, name] if l])
        return res

    @property
    def text(self):
        """
        Text to construct this instance.
        """
        return self.text_formatted(indent=0, linebreak=False)

    # def __eq__(self, other):
    #     if not isinstance(other, type(self)):
    #         return False
    #     res = [getattr(self, a) == getattr(other, a)
    #            for a in self.__dict__]
    #     return all(res)


class Dataset(Struct):
    """
    Class for *Dataset*
    """

    def __init__(self, name='', decl=None, text=None):
        super().__init__(name, stype='Dataset', decl=decl)
        if text:
            super().__init__(text=text)


class Structure(Struct):
    """
    Class for *Structure*
    """

    def __init__(self, name='', decl=None, text=None):
        super().__init__(name, stype='Structure', decl=decl)
        if text:
            super().__init__(text=text)


class Sequence(Struct):
    """
    Class for *Sequence*
    """

    def __init__(self, name='', decl=None, text=None):
        super().__init__(name, stype='Sequence', decl=decl)
        if text:
            super().__init__(text=text)


class Grid(Struct):
    """
    Class for *Grid*.

    | *Grid* := Grid { ARRAY: *declaration* MAPS: *declarations* } *var*

    Attributes:
        name(str): *name*
        stype(SType): *stype*
        array(ArrDecl): ARRAY *declaration*
        maps(list(ArrDecl): MAPS *declarations*
        decl(list(Declarations): ignored

    """

    def __init__(self, name='', array=None, maps=None, decl=None, text=None):
        """
        Parameters:
            name(str): *name*
            stype(str or SType): *stype*
            decl(list(Declarations): *declarations*
            array(ArrDecl): ARRAY *declaration*
            maps(list(ArrDecl): MAPS *declarations*
            text(str): text to be parsed.

        Raises:
            TypeError: if `stype` is invalid.

        If `text` is not ``None``, other attributes are overridden by
        the result of :meth:`.parse`.
        """
        super().__init__(name, stype='Grid', decl=decl)
        self.array = array  # Declaration()
        self.maps = maps  # list(Declaration())
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`Grid`.
        """
        _debug_write(f'{self.__class__.__name__}.parse: text="{text}"')
        res = _pat_grid.match(text)
        if res:
            _debug_write(
                f'{self.__class__.__name__}.parse: array_line="{res.group(1).strip()}"'
            )
            _debug_write(
                f'{self.__class__.__name__}.parse: maps_line="{res.group(2).strip()}"'
            )
            self.array = VarLine(text=res.group(1))
            self.maps = parse_declarations(res.group(2))
            self.name = res.group(3)

    def __repr__(self):
        if self.name:
            name = f'"{self.name}"'
        else:
            name = ''
        if self.stype:
            stype = f'stype="{self.stype.name}"'
        else:
            stype = ''
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
            f'Grid.text_formatted:indent={indent},linebreak={linebreak}')
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
                array = ' ARRAY:\n' + tw.indent(self.array.text, ' ' * indent)
                ll = '\n'.join([
                    d.text_formatted(indent, linebreak) for d in self.maps if d
                ])
                maps = ' MAPS:\n' + tw.indent(ll, ' ' * indent)
                decl = '\n'.join(('{', array, maps, '}'))
            else:
                array = 'ARRAY:' + tw.indent(self.array.text, ' ' * indent)
                ll = ''.join([
                    d.text_formatted(indent, linebreak) for d in self.maps if d
                ])
                maps = 'MAPS:' + tw.indent(ll, ' ' * indent)
                decl = ' '.join(('{', array, maps, '}'))

        res = ' '.join([l for l in [stype, decl, name] if l])
        return res

    @property
    def text(self):
        return self.text_formatted(indent=0, linebreak=False)


class VarLine(Declaration):
    """
    Class for *VarLine*.

    | *VarLine* := *basetype* *var*;
    | *var* := *name* or *name array-decl*

    Attributes:
        name (str): *name*
        btype (BType): *basetype*
        arr (list(ArrDecl)): *array-decl*
    """

    def __init__(self, name='', btype=None, arr=None, text=None):
        """
        Parameters:
            name(str): *name*
            btype(str or BType): *basetype*
            arr(ArrDecl or list(ArrDecl)): *array-decl*
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
        elif isinstance(arr, ArrDecl):
            self.arr = arr
        elif type(arr) is list and isinstance(arr[0], ArrDecl):
            self.arr = arr
        elif isinstance(arr, str):
            self.arr = parse_arrdecls(arr)
        else:
            raise TypeError(f'arr={arr} is invalid type: {type(arr)}')
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`VarLine`.
        """

        _debug_write(f'VarLine.parse():text="{text[:60]}"')
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
            name = f'"{self.name}"'
        if self.btype is None:
            btype = ''
        else:
            btype = f'btype="{self.btype.name}"'

        if self.arr:
            arr = 'arr=' + str([a for a in self.arr])
        else:
            arr = ''

        args = ', '.join([elem for elem in [name, btype, arr] if elem != ''])
        args = ', '.join([elem for elem in [name, btype, arr] if elem != ''])

        return f'VarLine({args})'

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
        return self.text_formatted(linebreak=False)


class ArrDecl():
    """
    Class for *array-decl*

    | *array-decl* := [integer] or [*name* = integer]

    """

    def __init__(self, name='', val=None, text=None):
        self.name = name  # "name"
        self.val = val  # "integer"
        if text:
            self.parse(text)

    def parse(self, text):
        _debug_write(f'ArrDecl.parse():text="{text}"')
        res = _pat_arrdecl.match(text)
        if res:
            self.name = res.group(1)
            self.val = int(res.group(2))
        else:
            res = _pat_arrdecl_valonly.match(text)
            if res:
                self.val = int(res.group(1))
        _debug_write(f'ArrDecl.parse():name="{self.name}",val="{self.val}"')

    @property
    def text(self):
        if self.name:
            return f"[{self.name} = {self.val}]"
        elif self.val:
            return f"[{self.val}]"
        else:
            return ''

    def __str__(self):
        if self.name:
            return f'ArrDecl(name="{self.name}", val={self.val})'
        elif self.val:
            return f"[{self.val}]"
        else:
            return ''

    def __repr__(self):
        if self.name:
            return f'ArrDecl("{self.name}", {self.val})'
        elif self.val:
            return f'ArrDecl["", {self.val}]'
        else:
            return ''

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        res = [getattr(self, a) == getattr(other, a) for a in self.__dict__]
        return all(res)


def check_braces_matching(text):
    """
    Check if braces(``{`` and ``}``) in given `text` match.

    Raises `ValueError` unless match.

    Examples:

        >>> text = 'Dataset{varline} hoge'
        >>> check_braces_matching(text)  # True

        >>> text = 'Struct{ Sequence{VarLine} fuga }} hoge'
        >>> check_braces_matching(text)
        Traceback (most recent call last):
            ...
        ValueError: braces do not match: too many right braces: 1 more.

        >>> text = 'Struct{ Sequence{{VarLine} fuga } hoge'
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
    Return list of *Declaration* parsed from `text`.
    """
    # _debug_write(f'parse_declarations:text="{text}"')
    # _debug_write('======parse_declarations======')
    res = []
    while text != '':
        _debug_write('=' * 20)
        _debug_write(f'parse_declarations:text="{text}"')
        res_ident = _pat_ident.match(text)
        if res_ident:
            ident = res_ident.group(1)
            _debug_write(f'parse_declarations:ident:"{ident}"')
            if ident in _idents_stype:
                ss, rest = pop_struct(text)
                res.append(ss)
                text = rest.strip()
            elif ident in _idents_btype:
                vl, rest = pop_varline(text)
                res.append(vl)
                text = rest.strip()
        else:
            return None
    return res


def pop_struct(text):
    """
    Pop one :class:`Struct`-derived instance parsed from the
    first part of `text, return it and the rest of `text`.
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
    _debug_write(f'parse_struct:lastdelim="{lastdelim}"')

    sline = text[:lastdelim].strip()
    rest = text[lastdelim:].strip()

    res = _pat_idents_stype.match(text)
    if res:
        ident = res.group(1)
        _debug_write(f'parse_struct:ident="{ident}"')
        _debug_write(f'parse_struct:sline="{sline}"')
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
    Pop one :class:`VarLine` instance parsed from the first part of
    `text`, return it and rest of the `text`.
    """
    _debug_write(f'pop_varline:text="{text}"')
    pat_split = re.compile(r' *(.+?;) *(.*)', re.DOTALL)

    res = pat_split.match(text)
    vline = res.group(1)
    try:
        rest = res.group(2).strip()
    except AttributeError:
        rest = ''
    _debug_write(f'pop_varline:vline="{vline}"')
    _debug_write(f'pop_varline:rest="{rest}"')

    vl = VarLine(text=vline)

    return vl, rest


def parse_arrdecls(text):
    """
    Parse `text` contains multiple :class:`ArrDecl` definitions and return
    a list of them.
    """
    _debug_write(f'parse_arrdecls:text="{text}"')
    res = _pat_arrdecl_line.findall(text)
    if res:
        return [ArrDecl(text=l) for l in res]
    else:
        return None


sample1 = '''
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

sample2 = '''
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

# _enable_debug()
_disable_debug()


def _test_mod():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test_mod()
