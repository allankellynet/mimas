#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
import unittest

# framework imports
from google.appengine.ext import testbed
from google.appengine.ext import ndb

# local imports
from conference_lib import conference, confoptions, confdelete
from submission_lib import submissionrecord, voterecord
from speaker_lib import speaker
from talk_lib import talk
from subreview_lib import confreviewconfig, dedupvotes, reviewer
from scaffold import userrights


class TestConferenceDelete(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def count_db_entries(self, cls, conf_key):
        return cls.query(ancestor=conf_key).count()

    def test_delete_conference(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        ur = userrights.UserRights(c.key)
        ur.add_track_reviewer("harry", "technology track")
        self.assertEquals(1, self.count_db_entries(userrights.RightsRecord, c.key))

        track1 = confoptions.make_conference_track(c.key, "New Track")
        track2 = confoptions.make_conference_track(c.key, "Another track")
        self.assertEquals(2, self.count_db_entries(confoptions.TrackOption, c.key))
        duration1 = confoptions.make_conference_option(confoptions.DurationOption, c.key, "30 minutes")
        self.assertEquals(1, self.count_db_entries(confoptions.DurationOption, c.key))
        confoptions.make_conference_option(confoptions.TalkFormatOption, c.key, "Lecture")
        self.assertEquals(1, self.count_db_entries(confoptions.TalkFormatOption, c.key))
        confoptions.make_conference_option(confoptions.ExpenseOptions, c.key, "Local")
        self.assertEquals(1, self.count_db_entries(confoptions.ExpenseOptions, c.key))

        review_config = confreviewconfig.get_conference_review_factory(c.key)
        self.assertIsNotNone(review_config)
        self.assertEquals(1, self.count_db_entries(confreviewconfig.ConferenceReviewFactory, c.key))
        self.assertEquals(0, self.count_db_entries(confreviewconfig.ClassicReview, c.key))
        self.assertEquals(1, self.count_db_entries(confreviewconfig.NewScoringReview, c.key))
        self.assertEquals(1, self.count_db_entries(confreviewconfig.RankReview, c.key))


        s = speaker.make_new_speaker("mail@email")
        s.name = "Arnold Rimmer"
        s.put()

        t = talk.Talk(parent=s.key)
        t.title = "A testing talk"
        t.put()

        sub_key = submissionrecord.make_submission(t.key, c.key, "track", "format")
        self.assertEquals(1, self.count_db_entries(submissionrecord.SubmissionRecord, c.key))
        vote = voterecord.cast_new_vote(sub_key, "Reviewer1", 2, "No comment", 1)
        self.assertEquals(1, self.count_db_entries(voterecord.VoteRecord, c.key))

        rev = reviewer.make_new_reviewer(c.key, "rimmer@email")
        self.assertEquals(1, self.count_db_entries(reviewer.Reviewer, c.key))
        rev.assign_submission("track", [sub_key], review_round=1)
        self.assertEquals(1, self.count_db_entries(reviewer.ReviewAssignment, c.key))


        confdelete.cascade_delete_conference(c.key)

        self.assertEquals(0, self.count_db_entries(userrights.RightsRecord, c.key))
        self.assertEquals(0, self.count_db_entries(submissionrecord.SubmissionRecord, c.key))
        self.assertEquals(0, self.count_db_entries(voterecord.VoteRecord, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.TrackOption, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.DurationOption, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.TalkFormatOption, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.ExpenseOptions, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.AcknowledgementEmailCCAddresses, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.AcknowledgementEmailBCCAddresses, c.key))
        self.assertEquals(0, self.count_db_entries(confoptions.AcceptEmailCCAddress, c.key))

        self.assertEquals(0, self.count_db_entries(confreviewconfig.ConferenceReviewFactory, c.key))
        self.assertEquals(0, self.count_db_entries(confreviewconfig.ClassicReview, c.key))
        self.assertEquals(0, self.count_db_entries(confreviewconfig.NewScoringReview, c.key))
        self.assertEquals(0, self.count_db_entries(confreviewconfig.RankReview, c.key))

        self.assertEquals(0, self.count_db_entries(dedupvotes.DuplicateVoteReport, c.key))
        self.assertEquals(0, self.count_db_entries(reviewer.ReviewAssignment, c.key))
        self.assertEquals(0, self.count_db_entries(reviewer.Reviewer, c.key))
