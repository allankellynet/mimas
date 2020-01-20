#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from submission_lib import submissionrecord, voterecord
from subreview_lib import votesummary
from talk_lib import talk


class TestVoteRecord(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def data_setup(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        t = talk.Talk()
        t.title = "A testing talk"
        t.put()

        return c,t

    def test_vote_summary_list_empty(self):
        lst = votesummary.VoteSummaryList("Harry", 1)

        self.assertEquals(lst.get_vote_score("key"), 0)
        self.assertEquals(lst.get_shared_comment("key"), "")
        self.assertEquals(lst.get_private_comment("key"), "")

        self.assertEquals(lst.get_vote_score("none"), 0)
        self.assertEquals(lst.get_shared_comment("sense"), "")
        self.assertEquals(lst.get_private_comment("no"), "")


    def test_summary(self):
        c, t = self.data_setup()
        round = 1

        sub_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(c.key)), 1)

        summary = votesummary.retrieve_vote_summary("Reviewer1", round)
        self.assertEquals(len(summary), 0)

        voterecord.cast_new_vote(sub_key, "Reviewer1", 2, "No comment", 1)
        summary = votesummary.retrieve_vote_summary("Reviewer1", round)

        self.assertEquals(len(summary), 1)
        self.assertTrue(summary.has_key(sub_key.urlsafe()))
        self.assertTrue(summary[sub_key.urlsafe()].score, 2)
        self.assertTrue(summary[sub_key.urlsafe()].shared_comment, "Yes comment")
        self.assertTrue(summary[sub_key.urlsafe()].shared_comment, "")

        t2 = talk.Talk()
        t2.title = "Another talk"
        t2.put()

        sub_key2 = submissionrecord.make_submission(t2.key, c.key, "track", "format")
        voterecord.cast_new_vote(sub_key2, "Reviewer1", 2, "Comments", 1)
        summary = votesummary.retrieve_vote_summary("Reviewer1", round)

        self.assertEquals(len(summary), 2)
        self.assertTrue(summary.has_key(sub_key2.urlsafe()))
        self.assertTrue(summary[sub_key2.urlsafe()].score, 1)
        self.assertTrue(summary[sub_key2.urlsafe()].shared_comment, "Comment2")
        self.assertTrue(summary[sub_key2.urlsafe()].shared_comment, "PRIVATE")

        voterecord.cast_new_vote(sub_key2, "Reviewer2", 2, "Comments", 1)
        self.assertEquals(len(votesummary.retrieve_vote_summary("Reviewer1", round)), 2)
        self.assertEquals(len(votesummary.retrieve_vote_summary("Reviewer2", round)), 1)
        self.assertEquals(len(votesummary.retrieve_vote_summary("Reviewer3", round)), 0)

