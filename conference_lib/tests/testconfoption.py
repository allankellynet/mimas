#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from conference_lib import confoptions


class TestOptionCounter(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_counter(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(confoptions.get_next_counter(c.key), 1)
        self.assertEquals(confoptions.get_next_counter(c.key), 2)
        self.assertEquals(confoptions.get_next_counter(c.key), 3)

class TestConferenceOptions(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_shortname(self):
        opt = confoptions.ConferenceOption()
        opt.set_shortname("Harry")
        self.assertEquals(opt.shortname(), "Harry")

    def test_full_text(self):
        opt = confoptions.ConferenceOption()
        opt.set_full_text("Harry")
        self.assertEquals(opt.full_text(), "Harry")

    def test_new_track(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.track_options(), {})
        self.assertEquals(c.track_objects(), [])

        to = confoptions.make_conference_track(c.key, "New Track")
        self.assertEquals(to.shortname(), "Option1")
        self.assertEquals(to.full_text(), "New Track")
        self.assertEquals(3, to.slots)
        self.assertEquals(c.track_options(), {"Option1": "New Track"})
        tracks = c.track_objects()
        self.assertEquals(len(tracks), 1)

        self.assertIsInstance(tracks[0], confoptions.TrackOption)
        self.assertEquals(tracks[0].shortname(), "Option1")
        self.assertEquals(tracks[0].full_text(), "New Track")

        confoptions.make_conference_track(c.key, "Another track")
        self.assertEquals(c.track_options(), {"Option1": "New Track",
                                               "Option2": "Another track"})
        tracks = c.track_objects()
        self.assertEquals(len(tracks), 2)
        self.assertIsInstance(tracks[1], confoptions.TrackOption)
        self.assertEquals(tracks[0].shortname(), "Option1")
        self.assertEquals(tracks[0].full_text(), "New Track")
        self.assertEquals(tracks[1].shortname(), "Option2")
        self.assertEquals(tracks[1].full_text(), "Another track")

    def test_tracks_with_slots(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()
        confoptions.make_conference_track(c.key, "New Track")
        confoptions.make_conference_track(c.key, "Another track")

        tracks = c.track_objects()
        some_track = tracks[1]
        some_track.slots = 4
        some_track.put()

        tracks = c.mapped_track_obects()
        self.assertEquals(len(tracks), 2)
        self.assertEquals(tracks["Option1"].shortname(), "Option1")
        self.assertEquals(tracks["Option1"].full_text(), "New Track")
        self.assertEquals(tracks["Option1"].slots, 3)
        self.assertEquals(tracks["Option2"].shortname(), "Option2")
        self.assertEquals(tracks["Option2"].full_text(), "Another track")
        self.assertEquals(tracks["Option2"].slots, 4)

    def test_delete_track(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.track_options(), {})
        self.assertEquals(c.track_objects(), [])

        confoptions.make_conference_track(c.key, "New Track")
        self.assertEquals(len(c.track_objects()), 1)

        confoptions.make_conference_track(c.key, "Another Track")
        self.assertEquals(len(c.track_objects()), 2)

        tracks = c.track_options()
        self.assertEquals(len(tracks), 2)
        delete_track = tracks.keys()[0]
        keep_track = tracks.keys()[1]

        confoptions.delete_track(c.key, delete_track)
        self.assertEquals(len(c.track_objects()), 1)
        remaining_tracks = c.track_options()
        self.assertEquals(remaining_tracks.keys()[0], keep_track)

    def test_aotb_cutover(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        confoptions.make_conference_track(c.key, "Software delivery")
        opt = confoptions.make_conference_track(c.key, "Delete me")
        confoptions.make_conference_track(c.key, "Product Design")
        confoptions.make_conference_track(c.key, "Product Management")
        confoptions.make_conference_track(c.key, "Team working")
        confoptions.make_conference_track(c.key, "Agile Practices")
        confoptions.make_conference_track(c.key, "Agility in businesss")

        # this will cause option2 to be missing
        opt.key.delete()

        # Need to sort so equality can  be applied
        self.assertEquals(sorted(c.track_options().values()),
                          sorted(c.track_options().values()))
        self.assertEquals(
                sorted(c.track_options().keys()),
                sorted([ "Option1", "Option3", "Option4", "Option5", "Option6", "Option7" ]))

    def test_delete_option(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.track_options(), {})
        self.assertEquals(c.track_objects(), [])

        confoptions.make_conference_track(c.key, "New Track")
        self.assertEquals(len(c.track_objects()), 1)

        confoptions.make_conference_track(c.key, "Another Track")
        self.assertEquals(len(c.track_objects()), 2)

        tracks = c.track_options()
        self.assertEquals(len(tracks), 2)
        delete_track = tracks.keys()[0]
        keep_track = tracks.keys()[1]

        confoptions.delete_option(confoptions.TrackOption, c.key, delete_track)
        self.assertEquals(len(c.track_objects()), 1)
        remaining_tracks = c.track_options()
        self.assertEquals(remaining_tracks.keys()[0], keep_track)

    def test_new_duration(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(c.track_options(), {})
        self.assertEquals(c.track_objects(), [])

        to = confoptions.make_conference_option(confoptions.DurationOption, c.key, "30 minutes")
        self.assertEquals(to.shortname(), "Option1")
        self.assertEquals(to.full_text(), "30 minutes")
        self.assertEquals(c.duration_options(), { "Option1": "30 minutes" })

        confoptions.make_conference_option(confoptions.DurationOption, c.key, "60mins")
        self.assertEquals(c.duration_options(), { "Option1": "30 minutes",
                                               "Option2": "60mins"})

        confoptions.make_conference_option(confoptions.DurationOption, c.key, "90")
        self.assertEquals(c.duration_options(), { "Option1": "30 minutes",
                                               "Option2": "60mins",
                                               "Option3": "90"})
        confoptions.delete_option(confoptions.DurationOption, c.key, "Option2")
        self.assertEquals(c.duration_options(), { "Option1": "30 minutes",
                                               "Option3": "90"})
