#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
import reports.commentreport
from submission_lib import submissionrecord, voterecord
from talk_lib import talk

class TestCommentReport(unittest.TestCase):
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

    def test_CommentReport(self):
        rpt = reports.commentreport.CommentReport()
        self.assertEquals({}, rpt.comments)

        rpt.add("key1", "comment1")
        self.assertEquals({"key1": ["comment1"]}, rpt.comments)
        rpt.add("key1", "comment2")
        self.assertEquals({"key1": ["comment1", "comment2"]}, rpt.comments)
        rpt.add("key2", "comment3")
        self.assertEquals({"key1": ["comment1", "comment2"],
                           "key2": ["comment3"]}, rpt.comments)


    def test_retrieve_commented_votes(self):
        c, t = self.data_setup()

        rpt = reports.commentreport.retrieve_commented_report(c.key)
        self.assertEquals(None, rpt)

        report = reports.commentreport.make_comment_report(c.key)
        self.assertNotEquals(None, report)


    def test_get_commented_votes(self):
        c, t = self.data_setup()

        report = reports.commentreport.get_commented_votes(c.key)
        self.assertEquals(report.comments, {})
        self.assertFalse(report.has_comments)
        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        vote1 = voterecord.cast_new_vote(subs_key, "New reviewer", 1, "", 1)
        report = reports.commentreport.get_commented_votes(c.key)
        self.assertEquals(report.comments, {})
        self.assertFalse(report.has_comments)

        vote2 = voterecord.cast_new_vote(subs_key, "Another reviewer", 1, "Good", 1)
        report = reports.commentreport.get_commented_votes(c.key)
        self.assertTrue(report.has_comments)
        self.assertEquals(report.comments, {subs_key: [vote2.key]})

        vote3 = voterecord.cast_new_vote(subs_key, "3rd reviewer", 1, "Bad", -1)
        self.assertEquals(reports.commentreport.get_commented_votes(c.key).comments, {subs_key: [vote2.key, vote3.key]})

        t2 = talk.Talk()
        t2.title = "A testing talk"
        t2.put()
        subs_key2 = submissionrecord.make_submission(t2.key, c.key, "track", "format")
        self.assertEquals(reports.commentreport.get_commented_votes(c.key).comments, {subs_key: [vote2.key, vote3.key]})

        vote4 = voterecord.cast_new_vote(subs_key2, "New reviewer", 1, "", 2)
        self.assertEquals(reports.commentreport.get_commented_votes(c.key).comments, {subs_key: [vote2.key, vote3.key]})

        subs_key3 = submissionrecord.make_submission(t2.key, c.key, "track", "format")
        self.assertEquals(reports.commentreport.get_commented_votes(c.key).comments, {subs_key: [vote2.key, vote3.key]})

        vote5 = voterecord.cast_new_vote(subs_key3, "New reviewer", 1, "Yes!", 2)
        self.assertEquals(reports.commentreport.get_commented_votes(c.key).comments,
                          {subs_key: [vote2.key, vote3.key],
                           subs_key3: [vote5.key]})


    def test_delete_vote_comments(self):
        c, t = self.data_setup()

        report = reports.commentreport.get_commented_votes(c.key)
        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        vote1 = voterecord.cast_new_vote(subs_key, "New reviewer", 1, "Comment", 1)
        vote2 = voterecord.cast_new_vote(subs_key, "Another reviewer", 1, "Good", 1)
        vote3 = voterecord.cast_new_vote(subs_key, "3rd reviewer", 1, "Bad", -1)
        vote4 = voterecord.cast_new_vote(subs_key, "4th", 1, "", 3)

        self.assertEquals("Comment", vote1.comment)
        self.assertEquals("Good", vote2.comment)
        self.assertEquals("Bad", vote3.comment)
        self.assertEquals("", vote4.comment)

        reports.commentreport.delete_vote_comments([vote1.key, vote2.key, vote3.key, vote4.key])
        self.assertEquals("", vote1.comment)
        self.assertEquals("", vote2.comment)
        self.assertEquals("", vote3.comment)
        self.assertEquals("", vote4.comment)

        # check they are in the db correctly
        # Todo: this test always works... even when put removed... need to fix
        votes = voterecord.find_existing_votes(subs_key, 1)
        for v in votes:
            self.assertEquals("", v.comment)


    def test_find_reviewer_votes_for_round(self):
        c, t = self.data_setup()
        round = 1

        # no votes at the start
        self.assertEquals(0, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer1", round)))

        # first vote
        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        vote1 = voterecord.cast_new_vote(subs_key, "Reviewer1", 1, "Comment", round)
        self.assertEquals(1, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer1", round)))

        # another vote for another submission
        subs_key2 = submissionrecord.make_submission(t.key, c.key, "track", "format1")
        vote2 = voterecord.cast_new_vote(subs_key2, "Reviewer1", 1, "", round)
        self.assertEquals(2, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer1", round)))

        # vote for another track
        subs_key3 = submissionrecord.make_submission(t.key, c.key, "anotherTrack", "format")
        vote3 = voterecord.cast_new_vote(subs_key2, "Reviewer1", 1, "", round)
        self.assertEquals(3, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer1", round)))

        # vote for another round
        vote4 = voterecord.cast_new_vote(subs_key, "Reviewer1", 1, "Round2", round + 1)
        self.assertEquals(0, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer", round + 1)))
        self.assertEquals(3, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer1", round)))

        # somelse votes
        vote5 = voterecord.cast_new_vote(subs_key, "Reviewer2", 1, "some else", round)
        self.assertEquals(0, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer", round)))
        self.assertEquals(3, len(reports.commentreport.find_reviewer_votes_for_round("Reviewer1", round)))

