#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from schedule_lib import schedule

class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.c = conference.Conference()

    def tearDown(self):
        self.testbed.deactivate()

    def testGetSchedule(self):
        # get conference will either retried existing schedule_lib or make a new one
        sched_key = schedule.get_conference_schedule(self.c.key)
        self.assertNotEquals(None, sched_key)

        sched = sched_key.get()
        self.assertEquals([], sched.day_names())

    def testScheduleDays(self):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()
        self.assertEquals([], sched.day_names())

        sched.add_day("Thursday")
        self.assertEquals(["Thursday"], sched.day_names())

        sched.add_day("Friday")
        expected_days = ["Thursday", "Friday"]
        expected_days.sort()
        retrieved_days = sched.day_names()
        retrieved_days.sort()
        self.assertEquals(expected_days, retrieved_days)

        thursday = sched.get_day("Thursday")
        self.assertEquals([], sched.tracks("Thursday"))

        sched.delete_day("Thursday")
        self.assertEquals(["Friday"], sched.day_names())

        sched.delete_day("Monday")
        self.assertEquals(["Friday"], sched.day_names())

    def testTracks(self):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()
        sched.add_day("Thursday")

        self.assertEquals([], sched.tracks("Thursday"))
        sched.add_track("Thursday", "Software")
        self.assertEquals(["Software"], sched.tracks("Thursday"))
        sched.add_track("Thursday", "Hardware")
        self.assertEquals(["Software", "Hardware"], sched.tracks("Thursday"))

        sched.del_track("Thursday", "Software")
        self.assertEquals(["Hardware"], sched.tracks("Thursday"))
