#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from mock import Mock, patch, call

import datetime

from google.appengine.ext import testbed

from conference_lib import conference
from reports import reportrecord

class TestReportRecord(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    @patch('reports.reportrecord.patchable_now_time')
    def testMkRecord(self, mock_now):
        c = conference.Conference()
        c.name = "TestConf"
        conf_key = c.put()

        self.assertEquals([], reportrecord.retrieve_reports_newest_to_oldset(conf_key))

        mock_now.return_value = (datetime.datetime(2020,2,24,9,0,0))
        rpt_key = reportrecord.mk_report_record(conf_key, "Excel report", "url.none.such.com")
        self.assertEquals([rpt_key.get()], reportrecord.retrieve_reports_newest_to_oldset(conf_key))
        report = rpt_key.get()
        self.assertEquals("Excel report", report.name_db)
        self.assertEquals("url.none.such.com", report.url_db)
        self.assertEquals(datetime.datetime(2020,2,24,9,0,0), report.created_db)


    @patch('reports.reportrecord.patchable_now_time')
    def testRetrieveOrdered(self, mock_now):
        c = conference.Conference()
        c.name = "TestConf"
        conf_key = c.put()

        mock_now.return_value = (datetime.datetime(2019,2,24,9,0,0))
        rpt_key = reportrecord.mk_report_record(conf_key, "Excel report", "url.none.such.com")
        self.assertEquals([rpt_key.get()], reportrecord.retrieve_reports_newest_to_oldset(conf_key))

        mock_now.return_value = (datetime.datetime(2020,2,24,9,0,0))
        rpt_key2 = reportrecord.mk_report_record(conf_key, "Another report", "url.none.such.com")
        self.assertEquals([rpt_key2.get(), rpt_key.get()], reportrecord.retrieve_reports_newest_to_oldset(conf_key))

        mock_now.return_value = (datetime.datetime(2018,2,24,9,0,0))
        rpt_key3 = reportrecord.mk_report_record(conf_key, "Third report", "url.none.such.com")
        self.assertEquals([rpt_key2.get(), rpt_key.get(), rpt_key3.get()], reportrecord.retrieve_reports_newest_to_oldset(conf_key))

