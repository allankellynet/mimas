#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

import unittest

# Library imports
from google.appengine.ext import testbed

from conference_lib import conference
from speaker_lib import speaker
from submission_lib import submissionrecord, submission_queries
# Local imports
from talk_lib import talk


class TestMsgTemplate(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def create_conference(self):
        self.c = conference.Conference()
        self.c.name = "Wizard Con 2018"
        self.c.put()

        self.s = speaker.make_new_speaker("harry@hogwarts.com")
        self.s.name = "Harry Potter"
        self.s.put()

        self.t = talk.Talk(parent=self.s.key)
        self.t.title = "Fighting Voldermort"
        self.t.put()

        self.sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")

    def test_is_submitted(self):
        self.create_conference()

        self.assertFalse(submission_queries.is_submitted(self.c.key, "harry@hogwarts.com", "How to fly"))
        self.assertFalse(submission_queries.is_submitted(self.c.key, "ron@hogwarts.com", "Fighting Voldermort"))
        self.assertTrue(submission_queries.is_submitted(self.c.key, "harry@hogwarts.com", "Fighting Voldermort"))

    def test_count_submissions(self):
        self.create_conference()

        spk1 = speaker.make_new_speaker("who@email")
        spk1.put()

        t1 = talk.Talk(parent=spk1.key)
        t1.title = "Talk T1"
        t1.put()
        sub_key = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")

        self.assertEquals(submission_queries.count_submissions(self.c.key, spk1.key), 1)

        t2 = talk.Talk(parent=spk1.key)
        t2.title = "Talk T2"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "track", "format")

        self.assertEquals(submission_queries.count_submissions(self.c.key, spk1.key), 2)

        spk2 = speaker.make_new_speaker("you@email")
        spk2.put()

        t3 = talk.Talk(parent=spk2.key)
        t3.title = "Talk T3 speaker 2"
        t3.put()
        sub_key3 = submissionrecord.make_submission(t3.key, self.c.key, "track", "format")

        self.assertEquals(submission_queries.count_submissions(self.c.key, spk1.key), 2)
        self.assertEquals(submission_queries.count_submissions(self.c.key, spk2.key), 1)

        c2 = conference.Conference()
        c2.name = "TestConf2"
        c2.put()

        self.assertEquals(submission_queries.count_submissions(c2.key, spk1.key), 0)
        self.assertEquals(submission_queries.count_submissions(c2.key, spk2.key), 0)

        t4 = talk.Talk(parent=spk1.key)
        t4.title = "Talk T4"
        t4.put()
        sub_key4 = submissionrecord.make_submission(t4.key, c2.key, "track", "format")

        self.assertEquals(submission_queries.count_submissions(c2.key, spk1.key), 1)
        self.assertEquals(submission_queries.count_submissions(c2.key, spk2.key), 0)
        self.assertEquals(submission_queries.count_submissions(self.c.key, spk1.key), 2)
        self.assertEquals(submission_queries.count_submissions(self.c.key, spk2.key), 1)

        sub_key2.get().withdraw()
        self.assertEquals(submission_queries.count_submissions(c2.key, spk1.key), 1)
        self.assertEquals(submission_queries.count_submissions(c2.key, spk2.key), 0)
        self.assertEquals(submission_queries.count_submissions(self.c.key, spk1.key), 1)
        self.assertEquals(submission_queries.count_submissions(self.c.key, spk2.key), 1)
