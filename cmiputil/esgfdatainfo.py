#!/usr/bin/env python3
"""
Supporting module for :mod:`esgfsearch`.

Class :class:`ESGFDataInfo` holds and manages search result
of ESGF RESTful API, issued by :meth:`esgfsearch.ESGFSearch.doSearch`.

One instance of this class corresponds to one search result, and a
list of instances is set as the attribute of
:attr:`esgfsearch.ESGFSearch.datainfo`.

This class also have some methods to access OPeNDAP catalog and
retrieve additional information, search local (pre-downloaded) files
to match the search result, etc.

Example:

    >>> from cmiputil import esgfdatainfo
    >>> import urllib3, json
    >>> keywords = {
    ... 'distrib':'true',
    ... 'type':'Dataset',
    ... 'format':r'application/solr+json',
    ... 'offset':0,
    ... 'replica':'False'}
    >>> params = {
    ... 'experiment_id':'piControl',
    ... 'variable_id':'tas',
    ... 'table_id':'Amon',
    ... 'source_id':'BCC-CSM2-MR'}
    >>> base_url = 'http://esgf-node.llnl.gov/esg-search/' 'search'
    >>> params.update(keywords)
    >>> http = urllib3.PoolManager()
    >>> r = http.request('GET', base_url, fields=params)
    >>> result = json.loads(r.data.decode())
    >>> attrs = result['response']['docs'][0]
    >>> dinfo = esgfdatainfo.ESGFDataInfo(attrs)
    >>> dinfo.id
    'CMIP6.CMIP.BCC.BCC-CSM2-MR.piControl.r1i1p1f1.Amon.tas.gn.v20181016|cmip.bcc.cma.cn'

Actually, doing search as above is done by
:class:`esgfsearch.ESGFSearch`.  A list of instances of this class
is set as the attribute :attr:`esgfsearch.ESGFSearch.datainfo`.
"""
from cmiputil import drs
from siphon.catalog import TDSCatalog
from collections.abc import MutableMapping
import re
from pprint import pprint


__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190619'
__date__ = '2019/06/19'


class ESGFDataInfo(MutableMapping):
    """
    Holds and maintains search result of ESGF dataset.

    Among attributes obtained from one search result, you can access
    several useful ones via :attr:`managedAttribs`.

    As this class inherits MutableMapping ABC, you can access an
    instance of this class as *mapping*, such as ``datainfo['source_id']``.

    Attributes:
        cat_url: URL of OPeNDAP catalog
        data_url: URL of dataset
        agg_data_url: URL of aggregated dataset
        mf_data_url: URL of multi-files dataset
        local_files: Paths of local file corresponding to the search result.
    """
    _debug = False

    @classmethod
    def _enable_debug(cls):
        cls._debug = True

    @classmethod
    def _disable_debug(cls):
        cls._debug = True

    # @property
    # def debug(cls):
    #     return cls._debug


    def __init__(self, attribs={}):
        """
        Args:
            attribs (dict): attributes to be set, see :meth:`.setFrom`:.

        """
        self.setFrom(attribs)

        if self._debug:
            print('dbg:ESGFDataInfo.__init__():')
            pprint(vars(self))

    def setFrom(self, attribs):
        """
        Set attributes from one ESGF RESTful API search result.

        Args:
            attribs (dict): attributes to be set.

        """
        # flatten list, except `url`
        for a, v in attribs.items():
            if type(v) is list and len(v) == 1:
                if (a != 'url'):
                    v = v[0]
            setattr(self, a, v)

        # extract THREDDS URL
        # if hasattr(self, 'url'):
        if 'url' in self:
            for l in self.url:
                (url, mime, service) = l.split('|')
                # select TDS catalog
                if (service == 'THREDDS'):
                    self.cat_url = url

        #  in drs <version> must be 'vYYYYMMDD'.
        if hasattr(self, 'version'):
            pat = re.compile(r'\d{8}')
            if pat.fullmatch(self.version):
                self.version = 'v'+self.version
        if self._debug:
            print('dbg:ESGFDataInfo.set():modified version:', self.version)

    @property
    def managedAttribs(self):
        """dict of useful global attributes."""
        attributes = [
            'data_node',
            # 'dataset_id',
            'id',
            'instance_id',
            'master_id',
            'number_of_aggregations',
            'number_of_files',
            'title',
            'type',
            'url',
            'version',
            'mip_era',
            'activity_drs',
            'activity_id',
            'institution_id',
            'source_id',
            'experiment_id',
            'member_id',
            'table_id',
            'variable_id',
            'variant_label',
            'grid_label',
            'sub_experiment_id'
        ]

        return {a: self[a]
                for a in attributes
                if a in self}

    def getDataURL(self, aggregate):
        """
        Get URL(s) of dataset from the OPeNDAP Catalog.

        Results are set as :attr:`.data_url`

        Args:
            aggregate (bool): retrieve aggregated dataset, or not.
        """
        try:
            cat = TDSCatalog(self.cat_url)
        except Exception as e:
            print('Error in siphon.TDSCatalog():', e.args)
            raise

        self.agg_data_url = (cat.base_tds_url + 
                             _getServiceBase(cat.services) +
                             cat.datasets[-1].url_path)  # Is this universal ?

        self.mf_data_url = [x.access_urls['OpenDAPServer']
                    for x in cat.datasets.values()
                    if 'OpenDAPServer' in x.access_urls]
        self.mf_data_url.sort()

        if aggregate:
            self.data_url = self.agg_data_url
        else:
            self.data_url = self.mf_data_url

    def getDDS(self):
        """
        Get OPeNDAP DDS (Dataset Descriptor Structure).

        Example of DDS::

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
        self.agg_dds = _getDDS(self.agg_data_url)

        self.mf_dds = [_getDDS(url) for url in self.mf_data_url]


    def findLocalFile(self, base_dir):
        """
        Find local (pre-downloaded) files corresponds to the search
        result.

        See **Local data store** section in :mod:`esgfsearch`.

        """

        d = drs.DRS(**self.managedAttribs)
        dname = d.dirName(prefix=base_dir)
        fname = str(d.fileName())
        self.local_files = list(dname.glob(fname))

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if type(key) == str:
            setattr(self, key, value)
        else:
            raise TypeError(key,type(key))

    def __delitem__(self, key):
        if hasattr(self, key):
            delattr(self, key)
        else:
            raise KeyError(key)

    def __missing__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return self.__dict__.__iter__()

    def __str__(self):
        res = {k: getattr(self, k)
               for k in self.__dict__}
        return str(res)

    def __len__(self):
        return len(self.__dict__)

def _getServiceBase(services):
    # `services` must be a list of SimpleService or CompoundService
    # class, attribute of TDSCatalog instance.

    for s in services:
        # search 'OpenDAP' service.
        if (s.service_type.lower() == 'opendap'):
            return s.base
        # if service_type is compound, do recursive call.
        elif (s.service_type.lower() == 'compound'):
            return _getServiceBase(s.services)


import urllib3
_http = None


def _getDDS(url):
    global _http

    if not _http:
        _http = urllib3.PoolManager()

    r = _http.request('GET', url + '.dds')
    if (r.status == 200):
        result = r.data.decode()
    else:
        result = None

    return result



if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
