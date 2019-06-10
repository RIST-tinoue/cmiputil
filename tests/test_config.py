#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmiputil import config
import unittest

from pathlib import Path


class test_Config(unittest.TestCase):
    def setUp(self):
        self.conftext = '\n'.join((
            "[ESGFSearch.facets]",
            "experiment_id = amip",
            "source_id = BCC-CSM2-MR",
            "table_id = Amon",
            "variable = pr",
            "variant_label = r1i1p1f1, r2i1p1f1, r3i1p1f1"))
        self.confdict = {
            'experiment_id': 'amip',
            'source_id': 'BCC-CSM2-MR',
            'table_id': 'Amon',
            'variable': 'pr',
            'variant_label': 'r1i1p1f1, r2i1p1f1, r3i1p1f1'}
        self.conffile = '/tmp/test_config_local.conf'
        pass

    def tearDown(self):
        pass

    def test_init00(self):
        ref = ''

        conf = config.Conf(None)
        res = conf.files
        self.assertIsInstance(conf, config.Conf)
        self.assertEqual(ref, res)

    def test_init01(self):
        ref = [Path(d).expanduser()/Path(config.conf_name)
               for d in config.conf_dir]

        conf = config.Conf()
        self.assertIsInstance(conf, config.Conf)
        res = conf.files
        self.assertEqual(ref, res)

    def test_init02(self):
        Path(self.conffile).write_text(self.conftext)
        ref = self.confdict

        conf = config.Conf(self.conffile)
        res = dict(conf['ESGFSearch.facets'].items())
        for k in ref:
            self.assertEqual(ref[k], res[k])

    def test_writeConf00(self):
        ref = self.conftext

        conf = config.Conf(None)  # to create config file
        conf.read_dict({"ESGFSearch.facets": self.confdict})
        conf.writeConf(self.conffile, overwrite=True)
        res = Path(self.conffile).read_text().strip()
        self.assertEqual(ref, res)

    def test_setDefaultSection00(self):
        ref = config.conf_default

        conf = config.Conf(None)
        conf.setDefaultSection()
        res = dict(conf[config.conf_section].items())
        self.assertEqual(ref, res)


def main():
    print('calling unittest:')
    unittest.main()


if __name__ == "__main__":
    main()
