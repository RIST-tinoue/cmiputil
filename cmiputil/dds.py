#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to parse DDS.

Text form of DDS will be obtained by :meth:`.ESGFDataInfo.getDDS`. Use :func:`parse_dataset` to parse it and return the tree structure of DDS.

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
    >>> ref = Struct('CMIP6.CMIP.MRI.MRI-ESM2-0.piControl.r1i1p1f1.Amon.tas.gn.tas.20190222.aggregation.1', stype='Dataset', decl=[
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
    ...     Grid("tas", stype="Grid",
    ...         ARRAY = VarLine("tas", btype="Float32", arr=[
    ...            ArrDecl(name="time", val=8412),
    ...            ArrDecl(name="lat", val=160),
    ...            ArrDecl(name="lon", val=320)]),
    ...         MAPS = [
    ...            VarLine("time", btype="Float64", arr=[
    ...               ArrDecl(name="time", val=8412)]),
    ...            VarLine("lat", btype="Float64", arr=[
    ...               ArrDecl(name="lat", val=160)]),
    ...            VarLine("lon", btype="Float64", arr=[
    ...               ArrDecl(name="lon", val=320)])])])
    >>> ref == res

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
    >>> ref = Struct('data',stype='Dataset', decl=[
    ...     VarLine('catalog_number', btype=BType.Int32),
    ...     Struct('station', stype='Sequence', decl=[
    ...         VarLine('experimenter', btype=BType.String),
    ...         VarLine('time', btype=BType.Int32),
    ...         Struct('location', stype='Structure', decl=[
    ...             VarLine('latitude', btype=BType.Float64),
    ...             VarLine('longitude', btype=BType.Float64) ]),
    ...         Struct('cast', stype='Sequence', decl=[
    ...             VarLine('depth', btype=BType.Float64),
    ...             VarLine('salinity', btype=BType.Float64),
    ...             VarLine('oxygen', btype=BType.Float64),
    ...             VarLine('temperature', btype=BType.Float64)])])])
    >>> res == ref
    True


"""














import re
from textwrap import shorten, fill
from pprint import pprint
import enum

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
_pat_idents_stype = re.compile('|'.join(_idents_stype))
_pat_ident = re.compile('|'.join(_idents))
_pat_struct = re.compile(r'^\s*(' + r'|'.join(_idents_stype)
                         + r')\s*\{(.*)\}\s*(\S+);\s*', re.DOTALL)
_pat_dataset = re.compile(r'^\s*Dataset\s+'
                          r'\{(.+)\}\s*(\S+);\s*$', re.DOTALL)
_pat_grid = re.compile(r'Grid\s*\{\s*Array:(.+)Maps:'
                       r'\s*(.+)\s*\}\s*(\w+);', re.I)
_pat_varline = re.compile(r'^\s*(\w+)\s*(\w+)(\[.+\])*;\s*$', re.DOTALL)
_pat_arrdecl = re.compile(r'\[(\w+?) = (\d+)\]')


class Declaration:
    """
    Base class for :class:`VarLine` and :class:`Struct`

    | *declarations* := list(*declaration*)
    | *declaration* := *VarLine* or *Struct*

    """
    def __init__(self, name='', decl=None):
        self.name = name
        self.decl = decl


class Struct(Declaration):
    """
    Class for *Struct*.

    | *Struct* := *stype* { *declarations* } *var*
    | *stype* := Dataset|Structure|Sequence|Grid

    For *Grid* use :class:`Grid` instead.

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
        super().__init__(name=name, decl=decl)
        if stype is None:
            self.stype = stype
        elif isinstance(stype, SType):
            self.stype = stype
        elif type(stype) is str:
            self.stype = SType(stype)
        else:
            raise TypeError(f'Invalid type for stype:'
                            f'type={type(stype)}, val={stype}')
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`Struct`.
        """
        _debug_write(fill(f'Struct.parse: text="{text}"'))
        res = _pat_struct.match(text)
        if res:
            _debug_write(fill(f'Struct.parse:name="{res.group(3)}"'))
            _debug_write(fill(f'Struct.parse:decl="{res.group(2).strip()}"'))
            self.stype = SType(res.group(1))
            self.decl = parse_declarations(res.group(2).strip())
            self.name = res.group(3)

    def __repr__(self):
        if self.name == '':
            name = ''
        else:
            name = f'name="{self.name}"'
        if self.stype is None:
            stype = ''
        else:
            stype = f', stype="{self.stype.name}"'
        if self.decl is None:
            decl = ''
        else:
            decl = ', decl='
            for d in self.decl:
                if d:
                    decl += d.text

        return (f'{type(self).__name__}({name}'
                f'{stype} decl={self.decl})')

    def __str__(self):
        if self.decl is None:
            decl = ''
        else:
            decl = '  '.join([d.text for d in self.decl if d is not None])
        lb = '{'
        rb = '}'
        return (f'{type(self).__name__}(name="{self.name}",'
                f' stype="{self.stype}", decl="{decl}")')

    def text_formatted(self, linebreak=False):
        """
        Return formatted text.
        """
        if self.decl is None:
            decl = ''
            lb, rb = '', ''
        else:
            if linebreak:
                decl = '\n  '.join([d.text for d in self.decl
                                    if d is not None])
                lb, rb = '{\n  ', '\n}'
            else:
                decl = '  '.join([d.text for d in self.decl
                                  if d is not None])
                lb, rb = '{  ',  '}'
        if self.stype is None:
            stype = ''
        else:
            stype = f'{self.stype.name}'
        return f'{stype} {lb}{decl}{rb} {self.name};'

    @property
    def text(self):
        """
        Text to construct this instance.
        """
        return self.text_formatted(linebreak=False)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        res = [getattr(self, a) == getattr(other, a)
               for a in self.__dict__]
        return all(res)


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

    def __init__(self, name='', stype='Grid', ARRAY=None, MAPS=None,
                 decl=None, text=None):
        """
        Parameters:
            name(str): *name*
            stype(str or SType): *stype*
            decl(list(Declarations): *declarations*
            ARRAY(ArrDecl): ARRAY *declaration*
            MAPS(list(ArrDecl): MAPS *declarations*
            text(str): text to be parsed.

        Raises:
            TypeError: if `stype` is invalid.

        If `text` is not ``None``, other attributes are overridden by
        the result of :meth:`.parse`.
        """
        super().__init__(name, stype, decl)
        self.array = ARRAY      # Declaration()
        self.maps = MAPS        # list(Declaration())
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`Struct`.
        """
        _debug_write(f'Struct.parse: text="{text}"')
        res = _pat_grid.match(text)
        if res:
            _debug_write(f'Struct.parse: array_line="{res.group(1).strip()}"')
            _debug_write(f'Struct.parse: maps_line="{res.group(2).strip()}"')
            self.array = VarLine(res.group(1).strip())
            self.maps = parse_declarations(res.group(2).strip())
            self.name = res.group(3)


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

        super().__init__(name)
        if btype is None:
            self.btype = btype
        elif isinstance(btype, BType):
            self.btype = btype
        elif type(btype) is str:
            self.btype = BType(btype)
        else:
            raise TypeError(f'Invalid type for btype:'
                            f'type={type(btype)}, val={btype}')
        if arr is None:
            self.arr = None
        elif type(arr) is ArrDecl:
            self.arr = arr
        elif type(arr) is str:
            self.arr = parse_arrdecls(arr)
        else:
            raise TypeError(f'Invalid type for arr:'
                            f'type={type(arr)}, val={arr}')
        if text:
            self.parse(text)

    def parse(self, text):
        """
        Parse `text` to construct :class:`VarLine`.
        """

        _debug_write(shorten(f'VarLine.parse():text="{text[:120]}"', 60))
        res = _pat_varline.match(text)
        if res:
            self.btype = BType(res.group(1))
            self.name = res.group(2)
            if res.group(3):
                self.arr = parse_arrdecls(res.group(3))

    def __repr__(self):
        if self.name == '':
            name = ''
        else:
            name = f'name="{self.name}"'
        if self.btype is None:
            btype = ''
        else:
            btype = f', btype="{self.btype.name}"'

        if self.arr:
            arr = ', arr='+str([a for a in self.arr])
        else:
            arr = ''

        args = ''.join([name, btype, arr])

        return f'VarLine({args})'

    def __str__(self):
        if self.name == '':
            name = ''
        else:
            name = f'name="{self.name}"'
        if self.btype is None:
            btype = ''
        else:
            btype = f', btype="{self.btype.name}"'

        if self.arr:
            arr = ', arr='+str([a for a in self.arr])
        else:
            arr = ''

        args = ''.join([name, btype, arr])

        return f'VarLine({args})'

    @property
    def text(self):
        """
        Text to construct this instance.
        """
        if self.btype is None:
            res = ''
        else:
            res = f'{self.btype.name}'
        if self.name != '':
            res += f' {self.name}'
        if self.arr:
            res += ''.join([a.text for a in self.arr])
        return res.strip()+';'

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        res = [getattr(self, a) == getattr(other, a)
               for a in self.__dict__]
        return all(res)


class ArrDecl():
    """
    Class for *array-decl*

    | *array-decl* := [integer] or [*name* = integer]

    """
    def __init__(self, name='', val=None, text=None):
        self.name = name   # "name"
        self.val = val    # "integer"
        if text:
            self.parse(text)

    def parse(self, text):
        res = _pat_arrdecl.match(text)
        if res:
            self.name = res.group(1)
            self.val = int(res.group(2))

    @property
    def text(self):
        return f"[{self.name} = {self.val}]"

    def __str__(self):
        return f'ArrDecl(name="{self.name}", val={self.val})'

    def __repr__(self):
        return f'ArrDecl(name="{self.name}", val={self.val})'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        res = [getattr(self, a) == getattr(other, a) for a in self.__dict__]
        return all(res)


def check_braces_matching(text):
    """
    Check if braces(``{`` and ``}``) in given `text` match or not.

    Raises ValueError unless match.

    Examples:

        >>> text = 'Dataset{varline} hoge'
        >>> check_braces_matching(text)

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
    Parse toplevel dataset

    *dataset* := Dataset { *declarations* } *name*;
    """
    check_braces_matching(text)

    # Dataset is the toplevel, *greedy* is preferable.
    res = _pat_dataset.match(text)
    if res:
        dataset = Struct(text=text)
    else:
        raise ValueError('Given text is not the Dataset definition.')

    return dataset


def parse_declarations(text):
    """
    Return list of Declaration()
    """
    # _debug_write(f'parse_declarations:text="{text}"')
    # _debug_write('======parse_declarations======')
    res = []
    while text != '':
        _debug_write('='*20)
        _debug_write(fill(f'parse_declarations:text="{text}"'))
        type_ident = find_type_identifier(text)
        _debug_write(f'type_ident:"{type_ident}"')
        if type_ident == 'G' or type_ident == 'S':
            ss, rest = pop_struct(text)
            res.append(ss)
            text = rest.strip()
        elif type_ident == 'B':
            vl, rest = pop_varline(text)
            res.append(vl)
            text = rest.strip()
        else:
            raise ValueError('Invalid text: no type identifier found.')
    return res


def find_type_identifier(text):
    """
    Find `type_identifier` at the fron to of `text`, showing the type
    of following declaration.

    If `type_identifier` is one of :class:`SType`, :class:`BType` or
    ``Grid``, following declaration is :class:`Struct`,
    :class:`VarLine`, :class:`Grid`, respectively.

    Return value is one of single character ``S``, ``B`` or ``G`` for
    each `type_identifier`, or ``None`` if not found valid identifyer.
    """
    _debug_write(shorten(f'find_type_identifier:text="{text}"', 60))

    res_ident = _pat_ident.search(text)

    ident = res_ident.group(0)
    _debug_write(f'ident="{ident}"')

    if ident == 'Grid':
        return 'G'
    elif ident in _idents_stype:
        return 'S'
    elif ident in _idents_btype:
        return 'B'
    else:
        return None


# def find_struct_block(text):
def pop_struct(text):
    """
    Pop one :class:`Struct` or :class:`Grid` instance parsed from the
    first part of `text, return it and the rest of `text`.

    This should be called after :meth:`find_type_identifier` returning
    ``S`` or ``G``.
    """

    leftpos = text.find('{')
    if (leftpos < 0):               # no braces, no Struct instance.
        return None

    nestlevel = 0
    for n, c in enumerate(text[leftpos:]):
        if c == '{':
            nestlevel += 1
        if c == '}':
            nestlevel -= 1
        if nestlevel == 0:
            rightpos = leftpos+n
            break

    lastdelim = rightpos+text[rightpos:].find(';')+1
    _debug_write(f'parse_struct:lastdelim="{lastdelim}"')

    sline = text[:lastdelim].strip()
    rest = text[lastdelim:].strip()

    res = _pat_idents_stype.match(text)
    if res:
        ident = res.group()
        if ident == 'Grid':
            ss = Grid(text=sline)
        else:
            ss = Struct(text=sline)
    else:
        raise ValueError('Invalid text')

    return ss, rest


def pop_varline(text):
    """
    Pop one :class:`VarLine` instance parsed from the first part of
    `text`, return it and rest of the `text`.

    This should be called after :meth:`find_type_identifier` returning
    ``B``.
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
    pat = re.compile(r'(\[\w+ = \d+\])', re.S)
    res = pat.findall(text)
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

#_enable_debug()
_disable_debug()

def _test_mod():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test_mod()


