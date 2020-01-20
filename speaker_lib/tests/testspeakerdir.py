#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

# Local imports
from speaker_lib import speaker, speakerdir


class TestSpeakerDir(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_retrieve_full_directory(self):
        d = speakerdir.SpeakerDir()
        self.assertEquals(0, len(d.get_speaker_list()))

        s = speaker.make_new_speaker("mail@email")
        s.put()
        self.assertFalse(d.is_speaker_listed(s.key))
        d.add_speaker(s.key)
        self.assertTrue(d.is_speaker_listed(s.key))

        speaker_list = d.get_speaker_list()
        self.assertEquals(1, len(speaker_list))
        self.assertEquals("mail@email", speaker_list[0].get().email)

        s2 = speaker.make_new_speaker("harry@email")
        s2.put()
        d.add_speaker(s2.key)

        s3 = speaker.make_new_speaker("ron@email")
        s3.put()
        d.add_speaker(s3.key)
        self.assertEquals(3, len(d.get_speaker_list()))

    def test_remove_speaker(self):
        d = speakerdir.SpeakerDir()
        self.assertEquals(0, len(d.get_speaker_list()))

        s = speaker.make_new_speaker("mail@email")
        s.put()
        d.add_speaker(s.key)

        s2 = speaker.make_new_speaker("harry@email")
        s2.put()
        d.add_speaker(s2.key)

        self.assertEquals(2, len(d.get_speaker_list()))

        self.assertTrue(d.is_speaker_listed(s.key))
        self.assertTrue(d.is_speaker_listed(s2.key))

        d.remove_speaker(s.key)
        self.assertEquals(1, len(d.get_speaker_list()))
        self.assertEquals("harry@email", d.get_speaker_list()[0].get().email)
        self.assertFalse(d.is_speaker_listed(s.key))
        self.assertTrue(d.is_speaker_listed(s2.key))

    def test_double_entry(self):
        s = speaker.make_new_speaker("mail@email")
        s.put()
        speakerdir.SpeakerDir().add_speaker(s.key)
        self.assertTrue(speakerdir.SpeakerDir().is_speaker_listed(s.key))

        self.assertEquals(1, len(speakerdir.SpeakerDir().get_speaker_list()))

        speakerdir.SpeakerDir().add_speaker(s.key)
        self.assertEquals(1, len(speakerdir.SpeakerDir().get_speaker_list()))

