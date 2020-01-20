#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from speaker_lib import speaker, cospeaker
from submission_lib import submissionrecord
from talk_lib import talk


class TestCoSpeaker(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.c = conference.Conference()
        self.c.name = "TestConf"
        self.c.put()

        self.spk1 = speaker.make_new_speaker("who@email")
        self.spk1.name = "Dr Who"
        self.spk1.put()


    def tearDown(self):
        self.testbed.deactivate()

    def test_ctor(self):
        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        cospeak = cospeaker.make_cospeaker(sub_key1, "Harry", "HPOTTER@hogwarts.org")
        self.assertFalse(speaker.speaker_exists("hpotter@hogwarts.org"))
        self.assertEquals(cospeak.name, "Harry")
        self.assertFalse(speaker.speaker_exists("hpotter@hogwarts.org"))
        self.assertEquals(cospeak.email, "hpotter@hogwarts.org")
        self.assertFalse(speaker.speaker_exists("hpotter@hogwarts.org"))
        self.assertEquals(cospeak.profile().bio, "No bio supplied")
        self.assertFalse(speaker.speaker_exists("hpotter@hogwarts.org"))
        self.assertFalse(cospeak.profile_exists())

        spk2 = speaker.make_new_speaker("hpotter@hogwarts.org")
        spk2.name="Harry"
        spk2.bio="The child who lived"
        spk2.put()

        # add a speaker profile on that email address
        self.assertTrue(cospeak.profile_exists())
        self.assertEquals(cospeak.profile().bio, "The child who lived")

    def test_get_co_speakers(self):
        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        self.assertEquals(len(cospeaker.get_cospeakers(sub_key1)), 0)

        cospeak = cospeaker.make_cospeaker(sub_key1, "Harry", "hpotter@hogwarts.org")
        r = cospeaker.get_cospeakers(sub_key1)
        self.assertEquals(len(r), 1)
        self.assertEquals(r[0], cospeak)

        cospeak2 = cospeaker.make_cospeaker(sub_key1, "Ron", "ron@hogwarts.org")
        q = cospeaker.get_cospeakers(sub_key1)
        self.assertEquals(len(q), 2)
        self.assertEquals(q[0], cospeak)
        self.assertEquals(q[1], cospeak2)

    def test_delete_cospeakers(self):
        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")
        cospeak = cospeaker.make_cospeaker(sub_key1, "Harry", "hpotter@hogwarts.org")
        cospeak2 = cospeaker.make_cospeaker(sub_key1, "Ron", "ron@hogwarts.org")
        self.assertEquals(len(cospeaker.get_cospeakers(sub_key1)), 2)

        cospeaker.delete_cospeakers(sub_key1)
        self.assertEquals(len(cospeaker.get_cospeakers(sub_key1)), 0)

    def test_profile_exists(self):
        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        self.assertEquals(len(cospeaker.get_cospeakers(sub_key1)), 0)

        cospeak = cospeaker.make_cospeaker(sub_key1, "Harry", "hpotter@hogwarts.org")
        r = cospeaker.get_cospeakers(sub_key1)
        self.assertEquals(len(r), 1)
        self.assertEquals(r[0], cospeak)

        self.assertFalse(r[0].profile_exists())
        self.assertFalse(speaker.speaker_exists("hpotter@hogwarts.org"))
        harry = speaker.make_new_speaker("hpotter@hogwarts.org")
        harry.put()
        self.assertTrue(speaker.speaker_exists("hpotter@hogwarts.org"))
        self.assertTrue(r[0].profile_exists())

    def test_filter_for_cospeakers(self):
        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        t2 = talk.Talk(parent=self.spk1.key)
        t2.title = "More talk"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "TrackB", "format")

        cospeak = cospeaker.make_cospeaker(sub_key2, "Harry", "hpotter@hogwarts.org")

        submissions = [ sub_key1, sub_key2 ]

        sub_speakers_map = cospeaker.filter_for_cospeakers(submissions)

        self.assertFalse(sub_speakers_map.has_key(sub_key1))
        self.assertTrue(sub_speakers_map.has_key(sub_key2))
        self.assertEqual(sub_speakers_map[sub_key2][0].name, "Harry")

        cospeak = cospeaker.make_cospeaker(sub_key2, "Ron", "ronw@hogwarts.org")
        sub_speakers_map = cospeaker.filter_for_cospeakers(submissions)

        self.assertFalse(sub_speakers_map.has_key(sub_key1))
        self.assertTrue(sub_speakers_map.has_key(sub_key2))
        cospeakers = sub_speakers_map[sub_key2]
        cospeakers.sort(key=lambda speaker: speaker.name)
        self.assertEqual(sub_speakers_map[sub_key2][0].name, "Harry")
        self.assertEqual(sub_speakers_map[sub_key2][1].name, "Ron")

    def test_add_speaker(self):
        running_total = cospeaker.SpeakerTotals()

        self.assertEqual(running_total.total_number_of_speakers(), 0)
        self.assertEqual(running_total.speaker("ron@hogwats.org"), 0)

        running_total.add_speaker("ron@hogwats.org", "ron")
        self.assertEqual(running_total.total_number_of_speakers(), 1)
        self.assertEqual(running_total.speaker("ron@hogwats.org"), 1)

        running_total.add_speaker("ron@hogwats.org", "ron")
        self.assertEqual(running_total.total_number_of_speakers(), 1)
        self.assertEqual(running_total.speaker("ron@hogwats.org"), 2)

        running_total.add_speaker("harry@hogwarts.org", "harry")
        self.assertEqual(running_total.total_number_of_speakers(), 2)
        self.assertEqual(running_total.speaker("ron@hogwats.org"), 2)
        self.assertEqual(running_total.speaker("harry@hogwarts.org"), 1)

    def test_count_all_speakers(self):
        self.assertEqual(cospeaker.count_all_speakers([]).total_number_of_speakers(), 0)

        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        submissions = [sub_key1]
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 1)

        t2 = talk.Talk(parent=self.spk1.key)
        t2.title = "More talk"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "TrackB", "format")

        submissions = [sub_key1, sub_key2]
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 1)

        cospeak = cospeaker.make_cospeaker(sub_key2, "Harry", "hpotter@hogwarts.org")
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 2)

        cospeak = cospeaker.make_cospeaker(sub_key2, "Ron", "ronw@hogwarts.org")
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 3)

        cospeak = cospeaker.make_cospeaker(sub_key1, "Ron", "ronw@hogwarts.org")
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 3)

    def test_get_co_speaker_text(self):

        speakers = cospeaker.count_all_speakers([])
        self.assertEqual(speakers.total_number_of_speakers(), 0)
        self.assertFalse(speakers.has_speaker("hpotter@hotwarts.org"))
        self.assertFalse(speakers.has_speaker("ron@hotwarts.org"))
        self.assertFalse(speakers.has_speaker("who@email"))

        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        self.assertEquals("", cospeaker.get_pretty_list(sub_key1))

        submissions = [sub_key1]
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 1)

        cospeak = cospeaker.make_cospeaker(sub_key1, "Harry", "hpotter@hogwarts.org")
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 2)

        self.assertEquals("Harry (hpotter@hogwarts.org)", cospeaker.get_pretty_list(sub_key1))

        cospeak = cospeaker.make_cospeaker(sub_key1, u"Ron\xc1", "ronw@hogwarts.org")
        self.assertEqual(cospeaker.count_all_speakers(submissions).total_number_of_speakers(), 3)

        self.assertEquals(u"Harry (hpotter@hogwarts.org), Ron\xc1 (ronw@hogwarts.org)", cospeaker.get_pretty_list(sub_key1))

        speakers = cospeaker.count_all_speakers(submissions)
        self.assertTrue(speakers.has_speaker("hpotter@hogwarts.org"))
        self.assertEquals("Harry", speakers.name("hpotter@hogwarts.org"))

        self.assertTrue(speakers.has_speaker("ronw@hogwarts.org"))
        self.assertEquals(u"Ron\xc1", speakers.name("ronw@hogwarts.org"))

        self.assertFalse(speakers.has_speaker("voldermort@hotwarts.org"))

        self.assertEquals(self.spk1.key, speakers.speaker_key("who@email"))
        self.assertEquals(None, speakers.speaker_key("hpotter@hogwarts.org"))
        self.assertEquals(None, speakers.speaker_key("ron@hogwarts.org"))

    def test_mass_lowercase_email(self):
        # Function will only be used once to fix a historic problem
        # force all co=speaker e-mail addresses to lower case

        # can't use make co cpeaker because it has been fixed already
        cospeaker1 = cospeaker.CoSpeaker(parent=None)
        cospeaker1.cospeaker_email = "lower@lowercase.com"
        cospeaker1.cospeaker_name = "lower"
        cospeaker1.put()

        cospeaker2 = cospeaker.CoSpeaker(parent=None)
        cospeaker2.cospeaker_email = "UPPER@UPPERCASE.COM"
        cospeaker2.cospeaker_name = "UPPER"
        cospeaker2.put()

        cospeaker3 = cospeaker.CoSpeaker(parent=None)
        cospeaker3.cospeaker_email = "MiXeD@mixed.COM"
        cospeaker3.cospeaker_name = "Mixed"
        cospeaker3.put()

        stored1 = cospeaker.CoSpeaker.query(cospeaker.CoSpeaker.cospeaker_email == "lower@lowercase.com").fetch()
        self.assertEquals(1, len(stored1))
        self.assertEquals("lower@lowercase.com", stored1[0].cospeaker_email)
        self.assertEquals("lower", stored1[0].cospeaker_name)

        stored2 = cospeaker.CoSpeaker.query(cospeaker.CoSpeaker.cospeaker_email == "UPPER@UPPERCASE.COM").fetch()
        self.assertEquals(1, len(stored2))
        self.assertEquals("UPPER@UPPERCASE.COM", stored2[0].cospeaker_email)
        self.assertEquals("UPPER", stored2[0].cospeaker_name)

        stored3 = cospeaker.CoSpeaker.query(cospeaker.CoSpeaker.cospeaker_email == "MiXeD@mixed.COM").fetch()
        self.assertEquals(1, len(stored3))
        self.assertEquals("MiXeD@mixed.COM", stored3[0].cospeaker_email)
        self.assertEquals("Mixed", stored3[0].cospeaker_name)

        # all set up....

        cospeaker.make_db_emails_lower_case()

        stored1 = cospeaker.CoSpeaker.query(cospeaker.CoSpeaker.cospeaker_email == "lower@lowercase.com").fetch()
        self.assertEquals(1, len(stored1))
        self.assertEquals("lower@lowercase.com", stored1[0].cospeaker_email)
        self.assertEquals("lower", stored1[0].cospeaker_name)

        stored2 = cospeaker.CoSpeaker.query(cospeaker.CoSpeaker.cospeaker_email == "upper@uppercase.com").fetch()
        self.assertEquals(1, len(stored2))
        self.assertEquals("upper@uppercase.com", stored2[0].cospeaker_email)
        self.assertEquals("UPPER", stored2[0].cospeaker_name)

        stored3 = cospeaker.CoSpeaker.query(cospeaker.CoSpeaker.cospeaker_email == "mixed@mixed.com").fetch()
        self.assertEquals(1, len(stored3))
        self.assertEquals("mixed@mixed.com", stored3[0].cospeaker_email)
        self.assertEquals("Mixed", stored3[0].cospeaker_name)

    def test_listed_cospeaker(self):
        self.assertFalse(cospeaker.is_listed_cospeaker("harry@hogwarts.org"))

        t = talk.Talk(parent=self.spk1.key)
        t.title = "Talk talk"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")

        cospeak = cospeaker.make_cospeaker(sub_key1, "Harry", "HPOTTER@hogwarts.org")
        self.assertFalse(speaker.speaker_exists("hpotter@hogwarts.org"))

        self.assertFalse(cospeaker.is_listed_cospeaker("harry@hogwarts.org"))
