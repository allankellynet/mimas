#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from conference_lib import confstate
from submission_lib import submissionrecord
from talk_lib import talk


class TestConferenceState(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_review_round_progress_and_retrieval(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        t1 = talk.Talk()
        t1.title = "Talk 1"
        t1.put()
        t1_sub = submissionrecord.make_submission(t1.key, c.key, "track", "format").get()

        t2 = talk.Talk()
        t2.title = "Talk 2"
        t2.put()
        t2_sub = submissionrecord.make_submission(t2.key, c.key, "track", "format").get()

        t3 = talk.Talk()
        t3.title = "Talk 3 in another track should always be ignored"
        t3.put()
        t3_sub = submissionrecord.make_submission(t3.key, c.key, "different track", "format").get()

        t4 = talk.Talk()
        t4.title = "Talk 4 will be withdrawn"
        t4.put()
        t4_sub = submissionrecord.make_submission(t4.key, c.key, "track", "format").get()

        c.start_round1_reviews()
        self.assertTrue(c.is_round1)
        self.assertEquals(t1_sub.last_review_round, 1)
        self.assertEquals(t2_sub.last_review_round, 1)
        self.assertEquals(t3_sub.last_review_round, 1)
        self.assertEquals(t4_sub.last_review_round, 1)

        submissions = submissionrecord.retrieve_conference_submissions_by_track_and_round(c.key, "track", 1)
        self.assertEquals(len(submissions), 3)

        t4_sub.withdraw()
        submissions = submissionrecord.retrieve_conference_submissions_by_track_and_round(c.key, "track", 1)
        self.assertEquals(len(submissions), 2)

        t1_sub.set_review_decision(1, "Decline")
        t1_sub.put()

        t2_sub.set_review_decision(1, "Round2")
        t2_sub.put()

        confstate.close_round1_and_open_round2(c)
        self.assertTrue(c.is_round2)
        self.assertEquals(t1_sub.last_review_round, 1)
        self.assertEquals(t2_sub.last_review_round, 2)
        self.assertEquals(t3_sub.last_review_round, 1)
        self.assertEquals(t2_sub.review_decision(1), "Round2")
        self.assertEquals(t2_sub.review_decision(2), "No decision")

        submissions2 = submissionrecord.retrieve_conference_submissions_by_track_and_round(c.key, "track", 2)
        self.assertEquals(len(submissions2), 1)
        self.assertEquals(submissions2[0].title(), "Talk 2")

        self.assertEquals(t1_sub.last_review_round, 1)
        self.assertEquals(t2_sub.last_review_round, 2)
        self.assertEquals(t3_sub.last_review_round, 1)

        submissions3 = submissionrecord.retrieve_conference_submissions_by_track_round_and_decision(
            c.key, "track", 2, "Accept")
        self.assertEquals(len(submissions3), 0)

        t2_sub.set_review_decision(2, "Accept")
        t2_sub.put()
        submissions4 = submissionrecord.retrieve_conference_submissions_by_track_round_and_decision(
            c.key, "track", 2, "Accept")
        self.assertEquals(len(submissions4), 1)

        submissions5 = submissionrecord.retrieve_conference_submissions_by_track_round_and_decision(
            c.key, "track", 2, "Reject")
        self.assertEquals(len(submissions5), 0)

        # ---------------------------------------------------------------------
        # Imagine reoppening sumissions, taking a late one and then continuing
        c.open_for_submissions()
        t_late = talk.Talk()
        t_late.title = "Late submission"
        t_late.put()
        t_late_sub = submissionrecord.make_submission(t_late.key, c.key, "track", "format").get()

        c.start_round1_reviews()

        # check nothing is lost
        self.assertEquals(t1_sub.last_review_round, 1)
        self.assertEquals(t1_sub.review_decision(1), "Decline")
        self.assertEquals(t2_sub.last_review_round, 2)
        self.assertEquals(t2_sub.review_decision(1), "Round2")
        self.assertEquals(t2_sub.review_decision(2), "Accept")
        self.assertEquals(t3_sub.last_review_round, 1)
        self.assertEquals(t3_sub.review_decision(1), "No decision")

        self.assertEquals(t_late_sub.last_review_round, 1)
        self.assertEquals(t_late_sub.review_decision(1), "No decision")

        t_late_sub.set_review_decision(1, "Round2")
        confstate.close_round1_and_open_round2(c)
        self.assertEquals(t1_sub.last_review_round, 1)
        self.assertEquals(t2_sub.last_review_round, 2)
        self.assertEquals(t3_sub.last_review_round, 1)
        self.assertEquals(t2_sub.review_decision(1), "Round2")
        self.assertEquals(t2_sub.review_decision(2), "Accept")

        self.assertEquals(t_late_sub.last_review_round, 2)
        self.assertEquals(t_late_sub.review_decision(2), "No decision")

    def test_can_close_conference(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        # No submissions so no outstanding decisions
        self.assertTrue(confstate.can_close_conference(c.key, 1))

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, c.key, "track", "format")

        # can't close while submission is undecided
        self.assertFalse(confstate.can_close_conference(c.key, 1))

        sub = sub_key1.get()
        sub.set_review_decision(1, "Accept")
        sub.put()

        self.assertTrue(confstate.can_close_conference(c.key, 1))

        t2 = talk.Talk()
        t2.title = "Talk T2"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, c.key, "track", "format")
        self.assertFalse(confstate.can_close_conference(c.key, 1))

    def test_conference_options(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.max_submissions(), 3)
        self.assertFalse(c.conf_review_comments_visible)
        self.assertTrue(c.pays_expenses())
