#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import unittest

from google.appengine.ext import testbed

# local imports
from conference_lib import conference
from conference_lib import confstate
from submission_lib import submissionrecord, voterecord
from subreview_lib import roundreviews
from talk_lib import talk


class TestTalk(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_submit_decision(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        t1 = talk.Talk()
        t1.title = "Talk T1 - Accept"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, c.key, "track 1", "format")

        t2 = talk.Talk()
        t2.title = "Talk T2 - Reject"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, c.key, "track 1", "format")

        decisions_map = { sub_key1.urlsafe() : "Accept",
                          sub_key2.urlsafe() : "Decline" }

        t3 = talk.Talk()
        t3.title = "Talk T3 - No decision, different track"
        t3.put()
        sub_key3 = submissionrecord.make_submission(t3.key, c.key, "track 2", "format")

        c.start_round1_reviews()

        roundreviews.submit_decisions(c.key, "track 1", 1, decisions_map)

        self.assertEquals(sub_key1.get().review_decision(1), "Accept")
        self.assertEquals(sub_key2.get().review_decision(1), "Decline")
        self.assertEquals(sub_key3.get().review_decision(1), "No decision")

        decisions_map = {sub_key3.urlsafe(): "Accept" }
        roundreviews.submit_decisions(c.key, "track 2", 1, decisions_map)

        self.assertEquals(sub_key1.get().review_decision(1), "Accept")
        self.assertEquals(sub_key2.get().review_decision(1), "Decline")
        self.assertEquals(sub_key3.get().review_decision(1), "Accept")

    def test_retrieve_all_reviews(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        t = talk.Talk()
        t.title = "A testing talk"
        t.put()

        sub_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(c.key)), 1)

        self.assertEquals(len(roundreviews.retrieve_all_reviews(sub_key.get())), 0)

        voterecord.cast_new_vote(sub_key, "Fred", -2, "I hate this talk", 1)
        reviews = roundreviews.retrieve_all_reviews(sub_key.get())
        self.assertEquals(len(roundreviews.retrieve_all_reviews(sub_key.get())), 1)
        voterecord.cast_new_vote(sub_key, "Jim", 1, "I sort of like this talk", 1)

        t2 = talk.Talk()
        t2.title = "Another talk"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, c.key, "track", "format")
        voterecord.cast_new_vote(sub_key2, "Barney", 1, "Yo ho ho", 1)

        reviews = roundreviews.retrieve_all_reviews(sub_key.get())
        self.assertEquals(len(reviews), 2)
        self.assertEquals(reviews[0].reviewer, "Fred")
        self.assertEquals(reviews[1].reviewer, "Jim")

        sub_key.get().set_review_decision(1, "Round2")
        sub_key2.get().set_review_decision(1, "Decline")
        confstate.close_round1_and_open_round2(c)

        voterecord.cast_new_vote(sub_key, "Sheila", 1, "Yes please", 2)

        reviews = roundreviews.retrieve_all_reviews(sub_key.get())
        self.assertEquals(len(reviews), 3)
        self.assertEquals(reviews[0].reviewer, "Fred")
        self.assertEquals(reviews[1].reviewer, "Jim")
        self.assertEquals(reviews[2].reviewer, "Sheila")

    def test_mass_track_change(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        ReviewRound = 1

        t1 = talk.Talk()
        t1.title = "Talk T1 - No decsion"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, c.key, "track 1", "format")
        self.assertEqual(sub_key1.get().review_decision(ReviewRound), "No decision")

        t2 = talk.Talk()
        t2.title = "Talk T2 - Accept"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, c.key, "track 1", "format")
        sub_key2.get().set_review_decision(ReviewRound, "Accept")

        t3 = talk.Talk()
        t3.title = "Talk T3 - No decsion"
        t3.put()
        sub_key3 = submissionrecord.make_submission(t1.key, c.key, "track 1", "format")
        self.assertEqual(sub_key3.get().review_decision(ReviewRound), "No decision")

        t4 = talk.Talk()
        t4.title = "Talk T4 - Shortlist"
        t4.put()
        sub_key4 = submissionrecord.make_submission(t4.key, c.key, "track 1", "format")
        sub_key4.get().set_review_decision(ReviewRound, "Shortlist")

        roundreviews.mass_track_change(c.key, "track 1", ReviewRound, "No decision", "Decline")
        self.assertEqual(sub_key1.get().review_decision(ReviewRound), "Decline")
        self.assertEqual(sub_key2.get().review_decision(ReviewRound), "Accept")
        self.assertEqual(sub_key3.get().review_decision(ReviewRound), "Decline")
        self.assertEqual(sub_key4.get().review_decision(ReviewRound), "Shortlist")
