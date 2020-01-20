#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

import unittest

# Library imports
from google.appengine.ext import testbed

# Local imports
from conference_lib import conference
from speaker_lib import speaker
from submission_lib import submissionrecord, submissions_aux

from talk_lib import talk


# submissions_aux is a set of stand alone auxillary functions which support
# SubmissionRecord

class TestSubsAux(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def create_conference(self):
        self.c = conference.Conference()
        self.c.name = "TestConf"
        self.c.put()

    def create_talks(self):
        self.s = speaker.make_new_speaker("mail@email")
        self.s.name = "Arnold Rimmer"
        self.s.put()

        self.t1 = talk.Talk(parent=self.s.key)
        self.t1.title = "Talk 1"
        self.t1.put()

        self.t2 = talk.Talk(parent=self.s.key)
        self.t2.title = "Talk 2"
        self.t2.put()

        self.t3 = talk.Talk(parent=self.s.key)
        self.t3.title = "Talk 3"
        self.t3.put()

        self.t4 = talk.Talk(parent=self.s.key)
        self.t4.title = "Talk 4"
        self.t4.put()

    def test_expenses_summary(self):
        self.create_conference()
        self.create_talks()

        submissions = [
            submissionrecord.make_submission_plus(self.t1.key, self.c.key, "Track", "format", "duration", "World wide").get(),
            submissionrecord.make_submission_plus(self.t2.key, self.c.key, "Track", "format", "duration", "Local").get(),
            submissionrecord.make_submission_plus(self.t3.key, self.c.key, "Track", "format", "duration", "None").get(),
            submissionrecord.make_submission_plus(self.t4.key, self.c.key, "Track", "format", "duration", "Local").get(),
        ]

        expenses = submissions_aux.expenses_summary(submissions)

        self.assertEqual(len(expenses), 3)
        self.assertEqual(expenses["World wide"], 1)
        self.assertEqual(expenses["None"], 1)
        self.assertEqual(expenses["Local"], 2)



