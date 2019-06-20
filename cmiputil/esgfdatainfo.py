#!/usr/bin/env python3
"""
Supporting module for :mod:`esgfsearch`.

Class :class:`ESGFDataInfo` holds and manages research result
of ESGF RESTful API, issued by :meth:`esgfsearch.ESGFSearch.doSearch`.

One instance of this class corresponds to one search result, and a
list of instances is set as the attribute of
:attr:`esgfsearch.ESGFSearch.datainfo`.

This class also have some methods to access OPeNDAP catalog and
retrieve additional information, search local (pre-downloaded) files
to match the search result, etc.

Example:

    >>> from cmiputil import esgfdatainfo
    >>> import urllib3
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
    >>> dinfo = esgfdatainfo.ESGFDataInfo(**attrs)
    >>> dinfo.id
    'CMIP6.CMIP.BCC.BCC-CSM2-MR.piControl.r1i1p1f1.Amon.tas.gn.v20181016|cmip.bcc.cma.cn'

Actually, doing search as above is done by
:class:`esgfsearch.ESGFSearch`.  A list of instances of this class
is set as the attribute :attr:`esgfsearch.ESGFSearch.datainfo`.
"""
from cmiputil import drs
import re
from siphon.catalog import TDSCatalog
from pprint import pprint


__author__ = 'T.Inoue'
__credits__ = 'Copyright (c) 2019 RIST'
__version__ = 'v20190619'
__date__ = '2019/06/19'


class ESGFDataInfo():
    """
    Holds and maintains search result of ESGF dataset.

    Among attributes obtained from one search result, ones listed in
    :attr:`managed_attributes` are stored as attributes of this class.

    Attributes:
        cat_url: URL of OPeNDAP catalog
        data_url: URL of dataset
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

    #: stored global attributes in this class
    managed_attributes = [
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

    def __init__(self, **argv):
        """
        Args:
            argv (dict): attributes to be set, see :meth:`.set`:

        """
        self.set(**argv)

        if self._debug:
            print('dbg:ESGFDataInfo.__init__():')
            pprint(vars(self))

    def set(self, **argv):
        """
        Set attributes.

        Among the `argv`, that is a dict usually obtained from one
        result of the search via ESGF RESTful API, attributes listed
        in :attr:`managed_attributes` are set.

        Args:
            argv (dict): attributes to be set.

        """
        attribs = {a: argv[a] for a in argv
                   if a in self.managed_attributes}

        # flatten list, except `url`
        for a, v in attribs.items():
            if type(v) is list and len(v) == 1:
                if (a != 'url'):
                    v = v[0]
            setattr(self, a, v)

        # extract THREDDS URL
        for l in self.url:
            (url, mime, service) = l.split('|')
            # select TDS catalog
            if (service == 'THREDDS'):
                self.cat_url = url
        print('dbg:ESGFDataInfo.set():cat_url:', self.cat_url)

        #  in drs <version> must be 'vYYYYMMDD'.
        if hasattr(self, 'version'):
            pat = re.compile(r'\d{8}')
            if pat.fullmatch(self.version):
                self.version = 'v'+self.version
        if self._debug:
            print('dbg:ESGFDataInfo.set():modified version:', self.version)

    @property
    def managedAttribs(self):
        """Global attributes stored in the instance."""
        return {a: getattr(self, a)
                for a in self.managed_attributes
                if hasattr(self, a)}

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

        if aggregate:
            # construct base url
            data_url = cat.base_tds_url
            service_base = _getServiceBase(cat.services)
            data_url += service_base

            # url of Aggregated dataset
            ds = cat.datasets[-1]   # Is this universal ?

            data_url += ds.url_path
        else:
            data_url = [x.access_urls['OpenDAPServer']
                        for x in cat.datasets.values()
                        if 'OpenDAPServer' in x.access_urls]
            data_url.sort()

        self.data_url = data_url

    def findLocalFile(self, base_dir):
        """
        Find local (pre-downloaded) files corresponds to the search
        result.

        See **Local data store** section in :mod:`esgfsearch`.

        """

        d = drs.DRS(**self.managedAttribs)
        dname = d.dirName(prefix=base_dir)
        fname = str(d.fileName())
        self.localfiles = list(dname.glob(fname))


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


if (__name__ == '__main__'):
    import doctest
    doctest.testmod()
