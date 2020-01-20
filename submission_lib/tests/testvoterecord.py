#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

import reports.commentreport
from conference_lib import conference
from submission_lib import submission_queries
from submission_lib import submissionrecord, voterecord
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

    def test_find_existing_vote(self):
        c, t = self.data_setup()

        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(len(submission_queries.retrieve_conference_submissions(c.key)), 1)

        existing_vote = voterecord.find_existing_votes(subs_key, 1)
        self.assertTrue(existing_vote is None)

        voterecord.cast_new_vote(subs_key, "Reviewer", 2, "No comment", 1)
        reviews = voterecord.find_existing_votes(subs_key, 1)
        self.assertEquals(len(reviews), 1)
        self.assertEquals(reviews[0].reviewer, "Reviewer")

        voterecord.cast_new_vote(subs_key, "Another Reviewer", 2, "yes comment", 1)
        reviews = voterecord.find_existing_votes(subs_key, 1)
        self.assertEquals(len(reviews), 2)
        self.assertEquals(reviews[0].reviewer, "Reviewer")
        self.assertEquals(reviews[1].reviewer, "Another Reviewer")

    def test_find_existing_vote_by_reviewer(self):
        c, t = self.data_setup()

        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(len(submission_queries.retrieve_conference_submissions(c.key)), 1)

        existing_vote = voterecord.find_existing_vote_by_reviewer(subs_key, "Reviewer", 1)
        self.assertTrue(existing_vote is None)

        vote = voterecord.VoteRecord(parent=subs_key)
        vote.cast_vote("Reviewer", 2, "Vote early, vote often", 1)

        existing_vote = voterecord.find_existing_vote_by_reviewer(subs_key, "Reviewer", 1)
        self.assertTrue(existing_vote is not None)

        existing_vote = voterecord.find_existing_vote_by_reviewer(subs_key, "Never voted reviewer", 1)
        self.assertTrue(existing_vote is None)

        # test cast_vote wrapper
        vote = voterecord.cast_new_vote(subs_key, "New reviewer", 1, "OK", 1)
        new_vote = voterecord.find_existing_vote_by_reviewer(subs_key, "New reviewer", 1)
        self.assertTrue(new_vote is not None)
        self.assertEquals(new_vote.comment, "OK")

    def test_count_reviewer_votes_cast(self):
        c, t = self.data_setup()

        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(0, voterecord.count_reviewer_votes(c.key, "lister", 1))

        # single reviewer, single round, single vote
        voterecord.cast_new_vote(subs_key, "lister", 99, "Nowt", round=1)
        self.assertEquals(1, voterecord.count_reviewer_votes(c.key, "lister", 1))

        # count is by round; single reviewer, second round
        self.assertEquals(0, voterecord.count_reviewer_votes(c.key, "lister", 2))
        voterecord.cast_new_vote(subs_key, "lister", 10, "No comment", round=2)
        self.assertEquals(1, voterecord.count_reviewer_votes(c.key, "lister", 2))
        self.assertEquals(1, voterecord.count_reviewer_votes(c.key, "lister", 1))

        # second submission in another track
        subs_key2 = submissionrecord.make_submission(t.key, c.key, "track2", "format")
        voterecord.cast_new_vote(subs_key, "lister", 10, "2 comment", round=1)
        self.assertEquals(2, voterecord.count_reviewer_votes(c.key, "lister", 1))

        # second reviewer
        voterecord.cast_new_vote(subs_key, "rimmer", 99, "Nowt", round=1)
        self.assertEquals(1, voterecord.count_reviewer_votes(c.key, "rimmer", 1))
        self.assertEquals(2, voterecord.count_reviewer_votes(c.key, "lister", 1))
        self.assertEquals(1, voterecord.count_reviewer_votes(c.key, "lister", 2))

    def test_count_votes_for_submissions(self):
        c, t = self.data_setup()
        round = 1

        sub_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(0, voterecord.count_votes_for_submission(sub_key, round))

        t2 = talk.Talk()
        t2.title = "Another talk"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, c.key, "track", "format")
        self.assertEquals(0, voterecord.count_votes_for_submission(sub_key2, round))

        self.assertItemsEqual({sub_key:0, sub_key2:0}, voterecord.count_votes_for_submissions([sub_key, sub_key2],1))

        voterecord.cast_new_vote(sub_key, "Reviewer1", 2, "No comment", 1)
        self.assertEquals(1, voterecord.count_votes_for_submission(sub_key, round))
        self.assertItemsEqual({sub_key:1, sub_key2:0}, voterecord.count_votes_for_submissions([sub_key, sub_key2],1))
        voterecord.cast_new_vote(sub_key, "Reviewer2", 2, "No comment", 1)
        self.assertItemsEqual({sub_key:2, sub_key2:0}, voterecord.count_votes_for_submissions([sub_key, sub_key2],1))
        voterecord.cast_new_vote(sub_key2, "Reviewer1", 2, "Comments", 1)
        self.assertItemsEqual({sub_key:2, sub_key2:1}, voterecord.count_votes_for_submissions([sub_key, sub_key2],1))

        self.assertItemsEqual({sub_key:0, sub_key2:0}, voterecord.count_votes_for_submissions([sub_key, sub_key2],2))
        voterecord.cast_new_vote(sub_key, "Reviewer1", 2, "No comment", 2)
        self.assertItemsEqual({sub_key:1, sub_key2:0}, voterecord.count_votes_for_submissions([sub_key, sub_key2],2))
