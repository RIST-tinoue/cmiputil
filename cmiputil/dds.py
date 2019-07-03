#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to parse DDS.

Example:

    >>> text = '''
    ... Grid {
    ...  ARRAY:
    ...     Float32 tas[time = 8412][lat = 160][lon = 320];
    ...  MAPS:
    ...     Float64 time[time = 8412];
    ...     Float64 lat[lat = 160];
    ...     Float64 lon[lon = 320];
    ... } tas;'''.replace('\\n','').strip()

    >>> d = parse_declarations(text)
    >>> d[0].text
    Grid { ARRAY:    Float32 tas[time = 8412][lat = 160][lon = 320]; MAPS:    Float64 time[time = 8412];    Float64 lat[lat = 160];    Float64 lon[lon = 320];} tas;

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
    ... '''.replace('\\n','')

    >>> d = Struct(text=sample1)
    >>> print(d)

    >>> sample2 = '''
    ...  Dataset {
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
    ... '''.replace('\\n','').strip()

    >>> sample2
    >>> d = Struct(text=sample2)
    >>> d

    ref2 = \
           Struct('data',stype='Dataset', decl=[
               VarLine('catalog_number', btype=BType.Int32),
               Struct('station', stype='Sequence', decl=[
                   VarLine('experimenter', btype=BType.String),
                   VarLine('time', btype=BType.Int32),
                   Struct('location', stype='Structure', decl=[
                       VarLine('latitude', btype=BType.Float64),
                       VarLine('longitude', btype=BType.Float64)
                   ]),
                   Struct('cast', stype='Sequence', decl=[
                       VarLine('depth', btype=BType.Float64),
                       VarLine('salinity', btype=BType. Float64),
                       VarLine('oxygen', btype=BType.Float64),
                       VarLine('temperature', btype=BType.Float64)
                   ])
               ])                          # end of Sequence
           ])                              # endo of Dataset

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


def debugwrite(text):
    global _debug
    if _debug:
        print(text)


class BType(enum.Enum):
    Byte = 'Byte'
    Int16 = 'Int16'
    Int32 = 'Int32'
    UInt32 = 'UInt32'
    Float32 = 'Float32'
    Float64 = 'Float64'
    String = 'String'
    Url = 'Url'


class SType(enum.Enum):
    Dataset = 'Dataset'
    Structure = 'Structure'
    Sequence = 'Sequence'
    Grid = 'Grid'


class ArrDecl():
    """
    "array-decl" := [integer] or ["name" = integer]
    """
    def __init__(self, name='', val=None, text=None):
        self.name = name   # "name"
        self.val = val    # "integer"
        if text:
            self.parse(text)

    def parse(self, text):
        pat = re.compile(r'\[(\w+?) = (\d+)\]')
        res = pat.match(text)
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


def parse_arrdecls(text):
    """
    return list(ArrDecl)
    """
    pat = re.compile(r'(\[\w+ = \d+\])', re.S)
    res = pat.findall(text)
    if res:
        return [ArrDecl(text=l) for l in res]
    else:
        return None


class Declaration:
    """
    Base class for :class:`VarLine` and :class:`Struct`

    *declarations* := list(*declaration*)
    *declaration* := *VarLine* or *Struct*
    """
    def __init__(self, name, decl=None):
        self.name = name
        self.decl = decl


class VarLine(Declaration):
    """
    *VarLine* := *basetype* *var*;
    *var* := *name* or *name array-decl*
    """
    pat = re.compile(r'^ *(\w+) (\w+)(\[.+\])*;$')

    def __init__(self, name='', btype=None, arr=None, text=None):
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
        debugwrite(shorten(f'VarLine.parse():text="{text[:120]}"', 60))
        res = self.pat.match(text)
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


class Struct(Declaration):
    """
    *Struct* := *stype* { *declarations* } *var*
    *stype* := Dataset|Structure|Sequence|Grid
    """
    pat = re.compile(r'(Dataset|Structure|Sequence|Grid) \{(.*)\} (\S+);')

    def __init__(self, name='', stype=None, decl=None, text=None):
        super().__init__(name=name, decl=decl)
        if type(stype) is str:
            self.stype = SType(stype)
        else:
            self.stype = stype
        if text:
            self.parse(text)

    def parse(self, text):
        debugwrite(fill(f'Struct.parse: text="{text}"'))
        res = self.pat.match(text)
        if res:
            debugwrite(fill(f'Struct.parse:name="{res.group(3)}"'))
            debugwrite(fill(f'Struct.parse:decl="{res.group(2).strip()}"'))
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
        return self.text_formatted(linebreak=False)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        res = [getattr(self, a) == getattr(other, a)
               for a in self.__dict__]
        return all(res)


class Grid(Struct):
    """
    *Grid* := Grid { ARRAY: *declaration* MAPS: *declarations* } *var*
    """
    pat = re.compile(r'Grid\s*\{\s*Array:(.+)Maps:'
                     r'\s*(.+)\s*\}\s*(\w+);', re.I)

    def __init__(self, name='', stype='Grid', ARRAY=None, MAPS=None,
                 decl=None, text=None):
        super().__init__(name, stype, decl)
        self.array = ARRAY      # Declaration()
        self.maps = MAPS        # list(Declaration())
        if text:
            self.parse(text)

    def parse(self, text):
        debugwrite(f'Struct.parse: text="{text}"')
        res = self.pat.match(text)
        debugwrite(f'Struct.parse: array_line="{res.group(1).strip()}"')
        debugwrite(f'Struct.parse: maps_line="{res.group(2).strip()}"')
        if res:
            self.array = VarLine(res.group(1).strip())
            self.maps = parse_declarations(res.group(2).strip())
            self.name = res.group(3)


def parse_dataset(text):
    """
    Parse toplevel dataset

    dataset := Dataset { declarations } name;
    """
    # Dataset is the toplevel, *greedy* is preferable.
    pat = re.compile(r'^ *Dataset \{(.+)\} (.+);$')
    res = pat.match(text)
    declarations = res.group(1).strip()
    name = res.group(2)

    return name, declarations


def parse_declarations(text):
    """
    Return list of Declaration()
    """
    # debugwrite(f'parse_declarations:text="{text}"')
    # debugwrite('======parse_declarations======')
    res = []
    while text != '':
        debugwrite('='*20)
        debugwrite(fill(f'parse_declarations:text="{text}"'))
        type_ident = find_type_identifier(text)
        debugwrite(f'type_ident:"{type_ident}"')
        if type_ident == 'G':
            sline, rest = find_struct_block(text)
            res.append(Grid(text=sline))
            text = rest.strip()
        elif type_ident == 'B':            # BType
            vl, rest = parse_varline(text)
            res.append(vl)
            text = rest.strip()
        elif type_ident == 'S':          # SType
            sline, rest = find_struct_block(text)
            res.append(Struct(text=sline))
            text = rest.strip()

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
    debugwrite(shorten(f'find_type_identifier:text="{text}"', 60))

    btype_idents = [t.name for t in BType]
    stype_idents = [t.name for t in SType]
    idents = btype_idents + stype_idents
    pat_ident = re.compile('|'.join(idents))
    res_ident = pat_ident.match(text)

    ident = res_ident.group(0)
    debugwrite(f'ident="{ident}"')

    if ident == 'Grid':
        return 'G'
    elif ident in stype_idents:
        return 'S'
    elif ident in btype_idents:
        return 'B'
    else:
        return None


def parse_varline(text):
    """
    Return :class:`VarLine` instance parsed from the first part of
    `text` and rest text.

    This should be called after :meth:`find_type_identifier` returning
    ``B``.
    """
    debugwrite(f'parse_varline:text="{text}"')
    pat_vl = re.compile(r' *(.+?;) *(.*)')

    res = pat_vl.match(text)
    vline = res.group(1)
    try:
        rest = res.group(2).strip()
    except AttributeError:
        rest = ''
    debugwrite(f'parse_varline:vline="{vline}"')
    debugwrite(f'parse_varline:rest="{rest}"')

    vl = VarLine(text=vline)

    return vl, rest


def find_struct_block(text):
    """
    Split `text` to first Struct definition lines and rest.
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
    debugwrite(f'parse_struct:lastdelim="{lastdelim}"')

    sline = text[:lastdelim].strip()
    rest = text[lastdelim:].strip()

    return sline, rest


def check_braces(text):
    count = 0
    maxcount = 0
    debugwrite('check_braces:')
    for n, c in enumerate(text):
        if c == '{':
            count += 1
            maxcount = max(maxcount, count)
            debugwrite(f'n={n}, count={count}')
        if c == '}':
            count -= 1
            debugwrite(f'n={n}, count={count}')
        if (count < 0):
            raise ValueError(f'braces do not match: '
                             f'too many right braces:{count} more.')
    if count > 0:
        raise ValueError(f'braces do not match: '
                         f'too many left braces:{count} more.')


def main():
    import doctest
    doctest.testmod()

# if __name__ == '__main__':
#     main()

import doctest
doctest.testmod()
