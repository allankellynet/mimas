#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from io import BytesIO

from google.appengine.ext import testbed

# Local imports
from speaker_lib import speaker, protospeaker, speakerdir
from scaffold import image, tags

class TestSpeaker(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_speaker_exists(self):
        self.assertFalse(speaker.speaker_exists("shaggy"))

    def set_empty_profile(self):
        s = speaker.Speaker()
        s.set_empty_profile("foo@bar.com")
        self.assertEquals(s.name, "")
        self.assertEquals(s.telephone, "")
        self.assertEquals(s.email, "foo@bar.com")

    def test_make_new_speaker(self):
        self.assertFalse(speaker.speaker_exists("mail@email"))
        s = speaker.make_new_speaker("mail@email")
        self.assertFalse(s.is_zero_deleted())
        self.assertEquals(s.name, "")
        self.assertEquals(s.telephone, "")
        self.assertEquals(s.email, "mail@email")
        self.assertFalse(speaker.speaker_exists("mail@email"))

    def test_make_and_store_new_speaker(self):
        self.assertFalse(speaker.speaker_exists("mail@email"))
        s_key = speaker.make_and_store_new_speaker("mail@email")
        s = s_key.get()
        self.assertFalse(s.is_zero_deleted())
        self.assertEquals(s.name, "")
        self.assertEquals(s.telephone, "")
        self.assertEquals(s.email, "mail@email")
        self.assertTrue(speaker.speaker_exists("mail@email"))

    def test_getset(self):
        s = speaker.make_new_speaker("mail@email")
        self.assertEquals(s.telephone, "")
        s.telephone = "+44 123"
        self.assertEquals(s.telephone, "+44 123")

        s.address = "Yellow Brick Road"
        self.assertEquals(s.address, "Yellow Brick Road")

        self.assertEquals(s.bio, "")
        s.bio = "Once upon a time"
        self.assertEquals(s.bio, "Once upon a time")

        self.assertEquals(s.field("Twitter"), "")
        s.set_field("Twitter", "@Tweetypy")
        self.assertEquals(s.field("Twitter"), "@Tweetypy")

        self.assertEquals("", s.field(s.FIELD_JOBTITLE))
        s.set_field(s.FIELD_JOBTITLE, "Superman")
        self.assertEquals("Superman", s.field(s.FIELD_JOBTITLE))

    def test_speakers_retrievable(self):
        email = "allan@allan"
        self.assertFalse(speaker.speaker_exists(email))

        s = speaker.make_new_speaker("mail@email")
        s.email = email

        s.put()
        self.assertTrue(speaker.speaker_exists(email))

        retrieved = speaker.retreive_speaker(email)
        self.assertTrue(retrieved.email, email)

    def test_speaker_image_url(self):
        s = speaker.make_new_speaker("mail@email")
        s.put()

        self.assertFalse(s.has_full_size_image())
        img_key = image.store_only_image(s.key, "Some value")
        self.assertTrue(s.has_full_size_image())
        expected = "/speakerfullimg?spk_id=" + s.key.urlsafe()
        self.assertEquals(s.full_image_url(), expected)

    def test_make_from_proto(self):
        proto = protospeaker.mk_proto_speaker(None, "Harry S Potter", "harry@hogwarts.com")
        spk = speaker.make_speaker_from_proto(proto)

        self.assertEquals("Harry", spk.first_name())
        self.assertEquals("S Potter", spk.later_names())
        self.assertEquals(proto.email(), spk.email)
        self.assertEquals("", spk.telephone)
        self.assertEquals("", spk.address)
        self.assertEquals("", spk.bio)
        self.assertEquals("", spk.field(spk.FIELD_JOBTITLE))

    def test_retreive_or_make(self):
        s_key = speaker.make_and_store_new_speaker("ron@hoggarts.com")
        self.assertTrue(speaker.speaker_exists("ron@hoggarts.com"))

        s = s_key.get()
        s.name = "Ron Weasley"
        s.put()
        self.assertTrue(speaker.speaker_exists("ron@hoggarts.com"))
        ron = speaker.retrieve_or_make("ron@hoggarts.com")
        self.assertEquals("Ron Weasley", ron.name)

        self.assertFalse(speaker.speaker_exists("Hermione@hogwarts.com"))
        harry = speaker.retrieve_or_make("Hermione@hogwarts.com")
        self.assertTrue(speaker.speaker_exists("Hermione@hogwarts.com"))
        self.assertEquals("", harry.name)

    def test_zero_out_speaker(self):
        s = speaker.make_new_speaker("mail@email")
        s.telephone = "+44 123"
        s.address = "Yellow Brick Road"
        s.bio = "Once upon a time"
        s.set_field("Twitter", "@Tweetypy")
        s.set_field(s.FIELD_JOBTITLE, "Superman")
        s.put()
        speakerdir.SpeakerDir().add_speaker(s.key)
        image.store_only_image(s.key, "Just some binary data")
        tags.TagList(s.key).add_tag("Test", "Speaker")

        self.assertTrue(image.image_exists(s.key))
        self.assertFalse(s.is_zero_deleted())

        s.zero_out_speaker()

        self.assertTrue(s.is_zero_deleted())

        self.assertFalse(speaker.speaker_exists("mail@email"))
        self.assertEquals("none@deleted.mimascr.com", s.email)
        self.assertEquals("", s.telephone)
        self.assertEquals("", s.address)
        self.assertEquals("", s.bio)
        self.assertEquals("", s.field("Twitter"))
        self.assertFalse(speakerdir.SpeakerDir().is_speaker_listed(s.key))
        self.assertEquals([], tags.TagList(s.key).get_all_tags([]))
        self.assertFalse(image.image_exists(s.key))

    def test_new_name_parts(self):
        s = speaker.Speaker()
        s.set_empty_profile("foo@bar.com")
        self.assertEquals(s.first_name(), "")
        self.assertEquals(s.later_names(), "")

        s.set_first_name("Harry")
        self.assertEquals(s.first_name(), "Harry")
        self.assertEquals(s.later_names(), "")
        self.assertEquals(s.name, "Harry")

        s.set_later_names("Potter")
        self.assertEquals(s.first_name(), "Harry")
        self.assertEquals(s.later_names(), "Potter")
        self.assertEquals(s.name, "Harry Potter")

        s.set_later_names("S. Potter")
        self.assertEquals(s.first_name(), "Harry")
        self.assertEquals(s.later_names(), "S. Potter")
        self.assertEquals(s.name, "Harry S. Potter")

        s2 = speaker.Speaker()
        s2.set_empty_profile("ron@bar.com")
        self.assertEquals(s2.first_name(), "")
        self.assertEquals(s2.later_names(), "")

        s2.set_later_names("Weasley")
        self.assertEquals(s2.first_name(), "")
        self.assertEquals(s2.later_names(), "Weasley")
        self.assertEquals(s2.name, "Weasley")

        s3 = speaker.make_new_speaker("Hermione@hogwarts.com")
        s3.set_names("Hermione", "Granger")
        self.assertEquals(s3.first_name(), "Hermione")
        self.assertEquals(s3.later_names(), "Granger")
        self.assertEquals(s3.name, "Hermione Granger")

    def test_legacy_name_handling(self):
        legacy = speaker.Speaker()
        legacy.set_empty_profile("foo@bar.com")
        legacy.name = "Harry Potter"
        self.assertEquals(legacy.name, "Harry Potter")
        self.assertEquals(legacy.first_name(), "Harry")
        self.assertEquals(legacy.later_names(), "Potter")

    def test_split_name_into_two_parts(self):
        name_tuple = speaker.split_name_into_two_parts("allan kelly")
        self.assertEquals("allan", name_tuple[0])
        self.assertEquals("kelly", name_tuple[1])

        n1, n2 = speaker.split_name_into_two_parts("allan")
        self.assertEquals("allan", n1)
        self.assertEquals("", n2)

        n1, n2 = speaker.split_name_into_two_parts("")
        self.assertEquals("", n1)
        self.assertEquals("", n2)

    def test_find_duplicate_speakers(self):
        self.assertEquals([], speaker.find_duplicate_speakers())

        s1 = speaker.make_new_speaker("Harry@hogwarts.com")
        s1.put()
        self.assertEquals([], speaker.find_duplicate_speakers())

        s2 = speaker.make_new_speaker("Ron@hogwarts.com")
        s2.put()
        self.assertEquals([], speaker.find_duplicate_speakers())

        s3 = speaker.make_new_speaker("Hermione@hogwarts.com")
        s3.put()
        self.assertEquals([], speaker.find_duplicate_speakers())

        s4 = speaker.make_new_speaker("Harry@hogwarts.com")
        s4.put()
        duplicates = speaker.find_duplicate_speakers()
        self.assertEquals(1, len(duplicates))
        self.assertEquals("Harry@hogwarts.com", duplicates[0].speaker_email)

        s5 = speaker.make_new_speaker("Harry@hogwarts.com")
        s5.put()
        duplicates = speaker.find_duplicate_speakers()
        self.assertEquals(1, len(duplicates))
        self.assertEquals("Harry@hogwarts.com", duplicates[0].speaker_email)

        speaker.make_new_speaker("Hagrid@hogwarts.com").put()
        duplicates = speaker.find_duplicate_speakers()
        self.assertEquals(1, len(duplicates))
        self.assertEquals("Harry@hogwarts.com", duplicates[0].speaker_email)

        speaker.make_new_speaker("Hermione@hogwarts.com").put()
        duplicates = speaker.find_duplicate_speakers()
        self.assertEquals(2, len(duplicates))
        self.assertEquals("Harry@hogwarts.com", duplicates[0].speaker_email)
        self.assertEquals("Hermione@hogwarts.com", duplicates[1].speaker_email)
