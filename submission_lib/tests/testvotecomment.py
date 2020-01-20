#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system includes

import unittest

# library imports
from google.appengine.ext import testbed

# local imports
from conference_lib import conference
from submission_lib import submissionrecord, voterecord, votecomment
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

    def test_add_comment(self):
        c, t = self.data_setup()

        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        vote =  voterecord.cast_new_vote(subs_key, "Reviewer", 2, "No comment", 1)

        comment = votecomment.mk_new_comment(vote.key, "Private", "I say old chap")
        self.assertTrue(comment.is_private())
        self.assertEquals(comment.comment_text(),"I say old chap")
        self.assertEquals(comment.key.parent(), vote.key)

    def test_retreive_comments(self):
        c, t = self.data_setup()

        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        vote =  voterecord.cast_new_vote(subs_key, "Reviewer", 2, "No comment", 1)

        private_comment = votecomment.retrieve_vote_comment(vote.key)
        self.assertIsNone(private_comment)
        self.assertEquals(votecomment.retrieve_comment_text(vote.key), "")

        comment = votecomment.mk_new_comment(vote.key, "Private", "I say old chap")

        retrieved_comment = votecomment.retrieve_vote_comment(vote.key)
        self.assertIsNotNone(retrieved_comment)
        self.assertEquals(comment, retrieved_comment)
        self.assertEquals(votecomment.retrieve_comment_text(vote.key), "I say old chap")

    def test_update_comment(self):
        c, t = self.data_setup()

        subs_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        vote =  voterecord.cast_new_vote(subs_key, "Reviewer", 2, "No comment", 1)

        private_comment = votecomment.retrieve_vote_comment(vote.key)

        comment = votecomment.update_comment(vote.key, "Private", "I say old chap")
        self.assertEquals(comment.comment_text(),"I say old chap")

        comment = votecomment.update_comment(vote.key, "Private", "Just like any picnic")
        self.assertEquals(comment.comment_text(),"Just like any picnic")
