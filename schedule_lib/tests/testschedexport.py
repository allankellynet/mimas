# -----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from mock import Mock, patch, call

from google.appengine.ext import testbed

from conference_lib import conference
from schedule_lib import schedule, schedexport

class TestScheduleExport(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.c = conference.Conference()

    def tearDown(self):
        self.testbed.deactivate()

    def test_dummy(self):
        self.assertTrue(True)

    @patch('schedule_lib.schedexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_schedule_to_excel(self, mock_storage_open, mock_sheet_write):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()

        print "---------------------"
        print sched

        sched.add_day("Monday")

        self.assertEquals(0, mock_storage_open.call_count)
        url = schedexport.schedule_to_excel(sched)
        self.assertEquals(1, mock_storage_open.call_count)
        self.assertEquals(0, mock_sheet_write.call_count)

        self.assertEquals("https:///mimas-aotb.appspot.com.storage.googleapis.com/Schedule", url[0:63])
        self.assertEquals(".xlsx", url[70:])

# https:///mimas-aotb.appspot.com.storage.googleapis.com/Schedule2271133.xlsx
