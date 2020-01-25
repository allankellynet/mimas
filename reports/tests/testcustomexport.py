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

        customexport.mk_report(self.conf.key, "Potter")
        self.assertEquals(["Potter"], customexport.list_all_report_names(self.conf.key))

        customexport.mk_report(self.conf.key, "Weesley")
        self.assertEquals(["Potter", "Weesley"], customexport.list_all_report_names(self.conf.key))
