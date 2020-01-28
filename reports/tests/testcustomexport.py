#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from reports import customexport

class TestCustomReport(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.conf = conference.Conference()
        self.conf.name = "Test Dummy Conf"
        self.conf.put()


    def tearDown(self):
        self.testbed.deactivate()

    def test_list_all_report_names(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        new_report_key = customexport.mk_report(self.conf.key, "Potter")
        self.assertEquals("Potter", new_report_key.get().report_name())
        self.assertEquals(["Potter"], customexport.list_all_report_names(self.conf.key))

        customexport.mk_report(self.conf.key, "Weesley")
        self.assertEquals(["Potter", "Weesley"], customexport.list_all_report_names(self.conf.key))

    def test_get_report_by_name(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        customexport.mk_report(self.conf.key, "Potter")
        potter_report = customexport.get_report_by_name(self.conf.key, "Potter")
        self.assertIsNotNone(potter_report)
        self.assertEquals("Potter", potter_report.report_name())

        customexport.mk_report(self.conf.key, "Weesley")
        weesley_report = customexport.get_report_by_name(self.conf.key, "Weesley")
        self.assertIsNotNone(weesley_report)
        self.assertEquals("Weesley", weesley_report.report_name())

    def test_delete_report(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        potter_report = customexport.mk_report(self.conf.key, "Potter")
        weesley_report = customexport.mk_report(self.conf.key, "Weesley")
        self.assertEquals(["Potter", "Weesley"], customexport.list_all_report_names(self.conf.key))

        potter_report.get().delete_report()

        self.assertEquals(["Weesley"], customexport.list_all_report_names(self.conf.key))
        self.assertIsNone(customexport.get_report_by_name(self.conf.key, "Potter"))

        weesley_report.get().delete_report()
        self.assertIsNone(customexport.get_report_by_name(self.conf.key, "Weesley"))

    def test_set_name(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        potter_report = customexport.mk_report(self.conf.key, "Potter")
        self.assertIsNone(customexport.get_report_by_name(self.conf.key, "Weesley"))

        potter_report.get().set_name("Weesley")
        self.assertIsNotNone(customexport.get_report_by_name(self.conf.key, "Weesley"))

    def test_submission_optoins(self):
        potter_report_key = customexport.mk_report(self.conf.key, "Potter")
        potter_report = potter_report_key.get()
        self.assertEquals([], potter_report.submission_options())

        potter_report.add_submission_options(["Hedwig"])
        self.assertEquals(["Hedwig"], potter_report.submission_options())

        potter_report.replace_submission_options(["Ernie", "Meenie", "Moo"])
        self.assertEquals(["Ernie", "Meenie", "Moo"], potter_report.submission_options())
