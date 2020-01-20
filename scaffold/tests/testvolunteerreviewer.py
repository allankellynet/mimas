#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from scaffold import volunteerreviewer

class TestVolunteerReviewer(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_volunteerreviewer(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        volunteer = volunteerreviewer.mk_volunteer_reviewer(c.key, "Harry", "harry@hogwarts.com", ["Track1", "Track2"])
        self.assertEqual("Harry", volunteer.name())
        self.assertEqual("harry@hogwarts.com", volunteer.email())
        self.assertEquals(["Track1", "Track2"], volunteer.tracks())
        self.assertEquals("", volunteer.accepted())

        volunteer.accept()
        self.assertEquals("Accepted", volunteer.accepted())
        volunteer.reject()
        self.assertEquals("Rejected", volunteer.accepted())

    def test_retreive(self):
        key = None
        volunteer1 = volunteerreviewer.mk_volunteer_reviewer(key, "Harry", "harry@hogwarts.com", ["Track1", "Track2"])
        volunteer2 = volunteerreviewer.mk_volunteer_reviewer(key, "Ron", "ron@hogwarts.com", ["Track1", "Track2"])
        volunteer3 = volunteerreviewer.mk_volunteer_reviewer(key, "Malfoy", "malfoy@hogwarts.com", ["TrackX"])

        all_volunteers = volunteerreviewer.retrieve_all_volunteers(key)
        self.assertEquals([volunteer1, volunteer2, volunteer3], all_volunteers)