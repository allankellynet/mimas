#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from io import BytesIO

from google.appengine.ext import testbed

# Local imports
from speaker_lib import speaker, speaker_checks
from conference_lib import conference
from talk_lib import talk
from submission_lib import submissionrecord

class TestSpeakerChecks(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_is_bio_blank(self):
        spk = speaker.retrieve_or_make("harry@hogwarts.com")
        self.assertTrue(speaker_checks.is_bio_blank(spk))

        spk.bio = "Harry is a really nice guy"
        self.assertFalse(speaker_checks.is_bio_blank(spk))

    def test_find_blank_bios(self):
        harry = speaker.retrieve_or_make("harry@hogwarts.com")
        harry.bio = "Harry is a really nice guy"

        ron = speaker.retrieve_or_make("ron@hogwarts.com")

        hagrid = speaker.retrieve_or_make("hagrid@hogwarts.com")
        hagrid.bio = "Hagrid is big"

        hammy = speaker.retrieve_or_make("hammy@hogwarts.com")

        spk_list = speaker_checks.filter_for_blank_bios(speaker.Speaker.query().fetch())
        self.assertEquals(2, len(spk_list))

        self.assertListEqual([ron, hammy], spk_list)

    def test_speakers_who_have_submitted(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        blank_speaker = speaker.make_new_speaker("rimmer@email")
        blank_speaker.name = "Arnold Rimmer"
        blank_speaker.put()

        t1 = talk.mk_talk(blank_speaker.key, "Talk T1")
        sub_key1 = submissionrecord.make_submission(t1, c.key, "track", "format")

        bioed = speaker.make_new_speaker("cat@email")
        bioed.name = "Arnold Rimmer"
        bioed.bio ="The Cat"
        bioed.put()

        t2 = talk.mk_talk(bioed.key, "Cat Talks")
        sub_key2 = submissionrecord.make_submission(t2, c.key, "track", "format")

        spk_list = speaker_checks.find_blank_bio_submissions(c.key)
        self.assertEquals(1, len(spk_list))
        self.assertEquals("rimmer@email", spk_list[0].email)
