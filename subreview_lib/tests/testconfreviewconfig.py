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
from conference_lib import conference, confoptions
from subreview_lib import confreviewconfig


class TestConfReviewConfig(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.conference = conference.Conference()
        self.conference.name = "TestConf"
        self.conference.put()

    def tearDown(self):
        self.testbed.deactivate()

    def test_simple_config(self):
        review_config = confreviewconfig.get_conference_review_factory(self.conference.key)
        self.assertIsNotNone(review_config)

        round1_config = review_config.get_round_config(round=1)
        self.assertEqual(1, round1_config.review_round())
        self.assertEquals("New scoring", round1_config.name())
        self.assertEquals(round1_config.reviewpage(), "scoringreview")
        self.assertEquals(round1_config.decisionpage(), "classic_review_decisions")
        self.assertEquals(round1_config.config_page(), "newscoreconfigpage")

        round2_config = review_config.get_round_config(round=2)
        self.assertEquals("Ranking", round2_config.name())
        self.assertEquals(round2_config.reviewpage(), "rankingreview")
        self.assertEquals(round2_config.decisionpage(), "rankingdecision")

    def test_new_conference(self):
        review_config = confreviewconfig.get_conference_review_factory(None)
        self.assertEquals("New scoring", review_config.get_round_config(round=1).name())
        self.assertEquals("Ranking", review_config.get_round_config(round=2).name())

    def test_change_config(self):
        review_config = confreviewconfig.get_conference_review_factory(self.conference.key)
        self.assertEquals("New scoring", review_config.get_round_config(round=1).name())
        self.assertEquals("Ranking", review_config.get_round_config(round=2).name())

        review_config.set_round(1, confreviewconfig.RankReview)
        self.assertEquals("Ranking", review_config.get_round_config(round=1).name())

        review_config.set_round(2, confreviewconfig.ClassicReview)
        self.assertEquals("Classic scoring", review_config.get_round_config(round=2).name())

        review_config.set_round(1, confreviewconfig.NewScoringReview)
        self.assertEquals("New scoring", review_config.get_round_config(round=1).name())

        retrieved_review_config = confreviewconfig.get_conference_review_factory(self.conference.key)
        self.assertEquals("New scoring", retrieved_review_config.get_round_config(round=1).name())
        self.assertEquals("Classic scoring", retrieved_review_config.get_round_config(round=2).name())

    def test_available_review_models(self):
        self.assertItemsEqual( ["Ranking", "Classic scoring", "New scoring"],
                                confreviewconfig.available_review_models())

    def test_change_by_name(self):
        review_config = confreviewconfig.get_conference_review_factory(self.conference.key)
        self.assertEquals("New scoring", review_config.get_round_config(round=1).name())
        self.assertEquals("Ranking", review_config.get_round_config(round=2).name())

        review_config.set_round_by_name(1, "Ranking")
        self.assertEquals("Ranking", review_config.get_round_config(round=1).name())

        review_config.set_round_by_name(1, "Nonsuch")
        self.assertEquals("Ranking", review_config.get_round_config(round=1).name())

        review_config.set_round_by_name(2, "Classic scoring")
        self.assertEquals("Classic scoring", review_config.get_round_config(round=2).name())

    def test_has_config_options(self):
        review_config = confreviewconfig.get_conference_review_factory(self.conference.key)
        self.assertTrue(review_config.get_round_config(round=1).has_config_options())
        self.assertFalse(review_config.get_round_config(round=2).has_config_options())
        self.assertEquals("", review_config.get_round_config(round=2).config_page())

    def test_track_assignments(self):
        factory = confreviewconfig.get_conference_review_factory(self.conference.key)
        factory.set_round(1, confreviewconfig.NewScoringReview)
        self.assertEquals("New scoring", factory.get_round_config(round=1).name())
        newscore_config = factory.get_round_config(1)

        self.assertEquals({}, newscore_config.track_limits())

        track1 = confoptions.make_conference_track(self.conference.key, "Track1")
        self.assertEquals({track1.shortname(): 10}, newscore_config.track_limits())

        track2 = confoptions.make_conference_track(self.conference.key, "Track2")
        self.assertItemsEqual({track1.shortname(): 10,
                               track2.shortname(): 10}, newscore_config.track_limits())

        newscore_config.set_track_limit(track1.shortname(), 20)
        self.assertItemsEqual({track1.shortname(): 20,
                               track2.shortname(): 10}, newscore_config.track_limits())

    def test_anonymous_flag(self):
        review_config = confreviewconfig.get_conference_review_factory(self.conference.key).get_round_config(round=1)
        self.assertIsNotNone(review_config)

        self.assertTrue(review_config.is_speaker_named())
        review_config.set_speaker_named(False)
        self.assertFalse(review_config.is_speaker_named())
        review_config.set_speaker_named(True)
        self.assertTrue(review_config.is_speaker_named())

    def test_private_comments_flag(self):
        review_config = confreviewconfig.get_conference_review_factory(self.conference.key)
        review_config.set_round(1, confreviewconfig.NewScoringReview)
        self.assertEquals("New scoring", review_config.get_round_config(round=1).name())

        retrieved_review_config = review_config.get_round_config(round=1)
        self.assertTrue(retrieved_review_config.private_comments())
        retrieved_review_config.set_private_comments(False)
        self.assertFalse(retrieved_review_config.private_comments())
