#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
import datetime

from google.appengine.ext import testbed

from conference_lib import conference
from schedule_lib import schedule, schedelement

class TestScheduleElement(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.c = conference.Conference()

    def tearDown(self):
        self.testbed.deactivate()

    def testMakeRetrieve(self):
        sched_key = schedule.get_conference_schedule(self.c.key)

        self.assertEquals([], schedelement.retreieve_elements(sched_key))

        element_key = schedelement.mk_element(sched_key, "Coffee")
        element = element_key.get()
        self.assertEquals("Coffee", element.title())
        self.assertEquals([element], schedelement.retreieve_elements(sched_key))

        element_key2 = schedelement.mk_element(sched_key, "Lunch")
        element2 = element_key2.get()
        self.assertEquals("Lunch", element2.title())
        elements = schedelement.retreieve_elements(sched_key)
        sorted_elements = sorted(elements, key=(lambda t: t.title_db))
        self.assertEquals([element, element2], sorted_elements)
