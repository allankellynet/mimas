# -----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from mock import Mock, patch
import datetime

from google.appengine.ext import testbed

from conference_lib import conference
from schedule_lib import schedule, schedexport
from talk_lib import talk
from submission_lib import submissionrecord

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

    @patch('schedule_lib.schedexport.worksheet_merge_wrapper')
    @patch('schedule_lib.schedexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_schedule_to_excel(self, mock_storage_open, mock_sheet_write, mock_merge):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()

        sched.add_day("Monday")
        sched.add_track("Monday", "Software")
        sched.add_track("Monday", "Hardware")

        sched.add_slot("Monday", schedule.Slot(datetime.time(9,0), datetime.time(9,30), "Tracks"))
        sched.add_slot("Monday", schedule.Slot(datetime.time(10,0), datetime.time(10,30), "Plenary"))

        t = talk.mk_talk(None, "Random talk")
        sub = submissionrecord.make_submission(t, self.c.key, "Track1", "FormatX")
        sched.assign_talk(sub.urlsafe(), "Monday", "Hardware", datetime.time(9, 0))

        self.assertEquals(0, mock_storage_open.call_count)
        url = schedexport.schedule_to_excel(sched)
        self.assertEquals(1, mock_storage_open.call_count)
        self.assertEquals(8, mock_sheet_write.call_count)
        self.assertEquals(1, mock_merge.call_count)

        self.assertEquals("https:///mimas-aotb.appspot.com.storage.googleapis.com/Schedule", url[0:63])
        self.assertEquals(".xlsx", url[len(url)-5:])

        self.assertEquals((0, 2, "Software"), mock_sheet_write.mock_calls[0][1][1:])
        self.assertEquals((0, 3, "Hardware"), mock_sheet_write.mock_calls[1][1][1:])

        self.assertEquals((1, 0, "09:00"), mock_sheet_write.mock_calls[2][1][1:])
        self.assertEquals((1, 1, "09:30"), mock_sheet_write.mock_calls[3][1][1:])
        self.assertEquals((1, 2, "Empty"), mock_sheet_write.mock_calls[4][1][1:])
        self.assertEquals((1, 3, "Random talk"), mock_sheet_write.mock_calls[5][1][1:])

        self.assertEquals((2, 0, "10:00"), mock_sheet_write.mock_calls[6][1][1:])
        self.assertEquals((2, 1, "10:30"), mock_sheet_write.mock_calls[7][1][1:])
        self.assertEquals((2, 2, 2, 3, "Empty"), mock_merge.mock_calls[0][1][1:])
