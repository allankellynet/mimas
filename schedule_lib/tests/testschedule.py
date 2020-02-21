#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
import datetime

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

    def testSlots(self):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()
        sched.add_day("Friday")

        self.assertEquals({}, sched.slots("Friday"))
        sched.add_slot("Friday", schedule.Slot(datetime.time(9,0), datetime.time(9,30), "Tracks"))
        self.assertEquals(1, len(sched.slots("Friday")))
        self.assertTrue(sched.slots("Friday").has_key(datetime.time(9,0)))
        first_slot = sched.slots("Friday")[datetime.time(9,0)]
        self.assertEquals(datetime.time(9,0), first_slot.start_time)
        self.assertEquals(datetime.time(9,30), first_slot.end_time)
        self.assertEquals("Tracks", first_slot.slot_type)

        sched.add_slot("Friday", schedule.Slot(datetime.time(9,30), datetime.time(10,30), "Plenary"))
        self.assertEquals(2, len(sched.slots("Friday")))
        self.assertTrue(sched.slots("Friday").has_key(datetime.time(9,30)))
        second_slot = sched.slots("Friday")[datetime.time(9,30)]
        self.assertEquals(datetime.time(9,30), second_slot.start_time)
        self.assertEquals(datetime.time(10,30), second_slot.end_time)
        self.assertEquals("Plenary", second_slot.slot_type)

        sched.add_slot("Friday", schedule.Slot(datetime.time(14,0), datetime.time(15,0), "Plenary"))
        self.assertEquals(3, len(sched.slots("Friday")))
        sched.delete_slot_by_start_time("Friday", datetime.time(9,30))
        self.assertEquals(2, len(sched.slots("Friday")))

        self.assertFalse(sched.slots("Friday").has_key(datetime.time(9,30)))
        self.assertTrue(sched.slots("Friday").has_key(datetime.time(9,0)))
        self.assertTrue(sched.slots("Friday").has_key(datetime.time(14,0)))

    def testOrderedSlots(self):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()
        sched.add_day("Friday")

        self.assertEquals({}, sched.slots("Friday"))
        sched.add_slot("Friday", schedule.Slot(datetime.time(9, 0), datetime.time(9, 0), "Nine"))
        sched.add_slot("Friday", schedule.Slot(datetime.time(9, 30), datetime.time(9, 30), "Nine thirty"))
        sched.add_slot("Friday", schedule.Slot(datetime.time(8, 30), datetime.time(8, 30), "Eight thirty"))
        sched.add_slot("Friday", schedule.Slot(datetime.time(9, 15), datetime.time(9, 15), "Nine ffiteen"))

        self.assertEquals([ datetime.time(8,30),
                            datetime.time(9,0),
                            datetime.time(9,15),
                            datetime.time(9,30)], sched.orderd_slot_keys("Friday"))

    def testAssignments(self):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()
        sched.add_day("Friday")
        sched.add_slot("Friday", schedule.Slot(datetime.time(9, 0), datetime.time(9, 0), "Nine"))
        self.assertEquals("Empty", sched.get_assignment("Friday", "Track1", datetime.time(9, 0)))
        sched.add_slot("Friday", schedule.Slot(datetime.time(10, 0), datetime.time(10, 30), "Ten"))
        self.assertEquals("Empty", sched.get_assignment("Friday", "Track1", datetime.time(10, 0)))
        sched.add_slot("Friday", schedule.Slot(datetime.time(11, 0), datetime.time(11, 30), "Elevent"))
        self.assertEquals("Empty", sched.get_assignment("Friday", "Track1", datetime.time(11,0)))

        sched.assign_talk("Random talk", "Friday", "Track1", datetime.time(9, 0))
        self.assertEquals("Random talk", sched.get_assignment("Friday", "Track1", datetime.time(9, 0)))

        sched.assign_talk("Another talk", "Friday", "Track1", datetime.time(10, 0))
        self.assertEquals("Another talk", sched.get_assignment("Friday", "Track1", datetime.time(10, 0)))

        sched.assign_talk("Last talk", "Friday", "Track1", datetime.time(11, 0))
        self.assertEquals("Last talk", sched.get_assignment("Friday", "Track1", datetime.time(11, 0)))

        sched.assign_talk("No such slot - accidentally supported but shouldnt happen talk",
                          "Friday", "Track1", datetime.time(12, 0))
        self.assertEquals("No such slot - accidentally supported but shouldnt happen talk",
                          sched.get_assignment("Friday", "Track1", datetime.time(12, 0)))

        sched.assign_talk("Allan talk", "Friday", "Track1", datetime.time(9, 0))
        self.assertEquals("Allan talk", sched.get_assignment("Friday", "Track1", datetime.time(9, 0)))

        self.assertEquals("Empty", sched.get_assignment("Friday", "Track1", datetime.time(13, 0)))

    def testClearAssignments(self):
        sched_key = schedule.get_conference_schedule(self.c.key)
        sched = sched_key.get()
        sched.add_day("Friday")
        sched.add_slot("Friday", schedule.Slot(datetime.time(9, 0), datetime.time(9, 0), "Nine"))
        self.assertEquals("Empty", sched.get_assignment("Friday", "Track1", datetime.time(9, 0)))

        sched.assign_talk("Random talk", "Friday", "Track1", datetime.time(9, 0))
        self.assertEquals("Random talk", sched.get_assignment("Friday", "Track1", datetime.time(9, 0)))

        sched.clear_slot("Friday", "Track1", datetime.time(9, 0))
        self.assertEquals("Empty", sched.get_assignment("Friday", "Track1", datetime.time(9, 0)))
