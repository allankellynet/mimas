#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import datetime
import unittest

from google.appengine.ext import testbed

from conference_lib import confdb
from conference_lib import conference
from conference_lib import confoptions
from scaffold import userrights, openrights


class TestConference(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_conf_fields(self):
        c = conference.Conference()
        c.name = "Allans conference_lib"
        c.shortname = "Allans"
        c.dates = "1-2 January 2017"
        c.creator_id = "Harry1"

        c.put()

        self.assertEquals(c.name, "Allans conference_lib")
        self.assertEquals(c.shortname, "Allans")
        self.assertEquals(c.dates, "1-2 January 2017")
        self.assertEquals(c.creator_id, "Harry1")

    def test_tracks(self):
        conf = conference.Conference()
        self.assertEquals(len(conf.track_options()), 0)
        # related tests are part of confoptions and testconfoptions

    def test_duration_options(self):
        conf = conference.Conference()
        self.assertEquals(len(conf.duration_options()), 0)

    def test_states(self):
        conf = conference.Conference()
        self.assertEquals(conf.state(), "Closed")
        self.assertFalse(conf.are_submissions_open())
        conf.open_for_submissions()
        self.assertEquals(conf.state(), "Open")
        self.assertTrue(conf.are_submissions_open())
        conf.close_submissions()
        self.assertEquals(conf.state(), "Closed")
        self.assertFalse(conf.are_submissions_open())
        self.assertFalse(conf.is_round1)
        self.assertFalse(conf.is_round2)

        conf.start_round1_reviews()
        self.assertEquals(conf.state(), "Round1Reviews")
        self.assertTrue(conf.is_round1)
        self.assertFalse(conf.are_submissions_open())

        conf.start_round2_reviews()
        self.assertEquals(conf.state(), "Round2Reviews")
        self.assertTrue(conf.is_round2)
        self.assertFalse(conf.are_submissions_open())

    def test_close_and_finalise(self):
        self.assertEquals(confdb.count_conferences(), 0)
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        # No submissions so none outstanding
        new_conf.finish_reviews()
        self.assertTrue(new_conf.is_reviewing_compete)

    def test_review_toggle(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertFalse(new_conf.comments_visible)
        new_conf.show_comments()
        self.assertTrue(new_conf.comments_visible)
        new_conf.hide_comments()
        self.assertFalse(new_conf.comments_visible)

    def test_user_rights(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        self.assertTrue(new_conf.user_rights() is None)
        new_conf.put()
        self.assertFalse(new_conf.user_rights() is None)

    def test_dummy_conference(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertFalse(new_conf.is_dummy_conf())

        self.assertIsInstance(new_conf.user_rights(), userrights.UserRights)
        self.assertNotIsInstance(new_conf.user_rights(), openrights.OpenRights)

        dummy_conf = conference.Conference()
        dummy_conf.name = "World Dummy Conf 2016"
        dummy_conf.put()

        self.assertFalse(dummy_conf.is_dummy_conf())

    def test_contact_email(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertEquals(new_conf.contact_email(), "")
        new_conf.set_contact_email("info@contact.conference_lib.com")
        self.assertEquals(new_conf.contact_email(), "info@contact.conference_lib.com")

    def test_max_submissions(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertEquals(new_conf.max_submissions(), 3)
        new_conf.set_max_submissions(1)
        self.assertEquals(new_conf.max_submissions(), 1)

    def test_created(self):
        now = datetime.datetime.now()

        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        # Not a full date time test because we don't need that much
        # Besides, this will fail when midnigt occurs during test
        # Checking hour, minutes, etc. would make that more common
        self.assertEquals(new_conf.created.year, now.year)
        self.assertEquals(new_conf.created.month, now.month)
        self.assertEquals(new_conf.created.day, now.day)

    def test_tracks_list_and_string(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.track_names([]), [])
        self.assertEquals(c.tracks_string([]), "")

        opt1 = confoptions.make_conference_track(c.key, "Track 1")
        self.assertEquals(c.track_names([opt1.shortname()]), ["Track 1"])
        self.assertEquals(c.tracks_string([opt1.shortname()]), "Track 1")

        opt2 = confoptions.make_conference_track(c.key, "Track 2")
        self.assertEquals(c.track_names([opt1.shortname(), opt2.shortname()]), ["Track 1", "Track 2"])
        self.assertEquals(c.tracks_string(
                            [opt1.shortname(), opt2.shortname()]),
                            "Track 1, Track 2")

    def test_urls(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.website(), "")
        c.set_website("http://world.com")
        self.assertEquals(c.website(), "http://world.com")

        self.assertEquals(c.cfp_address(), "")
        c.set_cfp_address("http://cfp.com")
        self.assertEquals(c.cfp_address(), "http://cfp.com")

        self.assertEquals(c.gdpr_address(), "")
        c.set_gdpr_address("http://gdpr.com")
        self.assertEquals(c.gdpr_address(), "http://gdpr.com")


    def test_max_co_speakers(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(3, c.max_cospeakers())
        c.set_max_cospeakers(1)
        self.assertEquals(1, c.max_cospeakers())
