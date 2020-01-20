#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from speaker_lib import speaker
from talk_lib import talk


class TestTalk(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_field_access(self):
        t = talk.Talk()
        self.assertEquals(t.title, "")
        t.title = "Wonderful"
        self.assertEquals(t.title, "Wonderful")
        self.assertEquals(t.title, "Wonderful".encode('ascii', 'ignore'))

    def test_talk_fields(self):
        t = talk.Talk()
        self.assertEquals(t.title, "")
        t.title = "Great talk"
        self.assertEquals(t.title, "Great talk")

    def test_store_retrieve(self):
        spk1 = speaker.make_new_speaker("who@email")
        spk1.put()
        t1 = talk.Talk(parent=spk1.key)
        t1.title = "Wonderful"
        t1.put()

        t2 = talk.Talk(parent=spk1.key)
        t2.title = "Great"
        t2.put()

        user1_talks = talk.all_user_talks_by_email(spk1.email)
        self.assertEquals(len(user1_talks), 2)

        spk2 = speaker.make_new_speaker("nobody@email")
        spk2.put()
        t3 = talk.Talk(parent=spk2.key)
        t3.title = "Smashing"
        t3.put()

        user2_talks = talk.all_user_talks_by_email(spk2.email)
        self.assertEquals(len(user2_talks), 1)

        t2.key.delete()
        user1_talks = talk.all_user_talks_by_email(spk1.email)
        self.assertEquals(len(user1_talks), 1)

    def test_store_retrieve_by_key(self):
        spk1 = speaker.make_new_speaker("who@email")
        spk1.put()
        t1 = talk.Talk(parent=spk1.key)
        t1.title = "Wonderful"
        t1.put()

        t2 = talk.Talk(parent=spk1.key)
        t2.title = "Great"
        t2.put()

        user1_talks = talk.speaker_talks_by_key(spk1.key)
        self.assertEquals(len(user1_talks), 2)

        spk2 = speaker.make_new_speaker("nobody@email")
        spk2.put()
        t3 = talk.Talk(parent=spk2.key)
        t3.title = "Smashing"
        t3.put()

        user2_talks = talk.speaker_talks_by_key(spk2.key)
        self.assertEquals(len(user2_talks), 1)

        t2.key.delete()
        user1_talks = talk.all_user_talks_by_email(spk1.email)
        self.assertEquals(len(user1_talks), 1)

    def test_no_such_speaker(self):
        talks = talk.all_user_talks_by_email("nosuch@nowhere")
        self.assertEquals(len(talks), 0)

    def test_directory_listing(self):
        spk1 = speaker.make_new_speaker("who@email")
        spk1.put()
        t1_key = talk.mk_talk(spk1.key, "Wonderful")
        t1 = t1_key.get()

        self.assertTrue(t1.is_listed())
        t1.hide_listing()
        self.assertFalse(t1.is_listed())
        t1.show_listing()
        self.assertTrue(t1.is_listed())
