#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from io import BytesIO

from google.appengine.ext import testbed

from conference_lib import conference
from speaker_lib import speaker
from scaffold import image


class TestImage(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_basics(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertFalse(image.image_exists(new_conf.key))
        self.assertEquals(None, image.retrieve_image_key(new_conf.key))

        image.store_only_image(new_conf.key, u"")
        self.assertFalse(image.image_exists(new_conf.key))

        some_image = BytesIO(b"some binary data: \x00\x01\x02")

        image.store_only_image(new_conf.key, some_image.getvalue())
        self.assertTrue(image.image_exists(new_conf.key))

        self.assertEquals(some_image.getvalue(), image.retrieve_image_key(new_conf.key).get().picture)

        self.assertFalse(image.image_exists(None))

        image.delete_image(new_conf.key)
        self.assertFalse(image.image_exists(new_conf.key))

    def test_multiple_images(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        some_image = BytesIO(b"some binary data: \x00\x01\x02")
        image.store_only_image(new_conf.key, some_image.getvalue())
        self.assertTrue(image.image_exists(new_conf.key))

        another_image = BytesIO(b"some more binary data: \x00\x01\x02")
        image.store_only_image(new_conf.key, another_image.getvalue())
        self.assertTrue(image.image_exists(new_conf.key))
        self.assertEquals(1, len(image.MimasImage.query(ancestor=new_conf.key).fetch(10, keys_only=True)))


    def test_basics_via_conference(self):
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertFalse(new_conf.has_image())

        some_image = BytesIO(b"some binary data: \x00\x01\x02")
        key = new_conf.set_image(some_image.getvalue())
        self.assertTrue(new_conf.has_image())
        img_key = new_conf.get_image_key()
        self.assertEquals(img_key, img_key)
        self.assertEquals(some_image.getvalue(), img_key.get().picture)

        some_image2 = BytesIO(b"other binary data: \xF0\xF1\xF2")

        image_key2 = new_conf.set_image(some_image2.getvalue())
        self.assertTrue(new_conf.has_image())
        self.assertEquals(some_image2.getvalue(), new_conf.get_image())

        img_key2 = new_conf.get_image_key()
        self.assertEquals(img_key2, image_key2)
        self.assertEquals(some_image2.getvalue(), img_key2.get().picture)

    def mk_speaker_with_image(self, email, data):
        s_key = speaker.make_and_store_new_speaker(email)
        s = s_key.get()
        s.fullsize_picture = data
        s.put()
        return s

    def test_convert_speaker_full_image_to_mimas_image(self):
        data = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        s = self.mk_speaker_with_image("mail@email", data)

        image.convert_speaker_full_image_to_mimas_image(s)
        self.assertEquals(None, s.fullsize_picture)

        img_key = image.retrieve_image_key(s.key)
        self.assertEquals(data, img_key.get().picture)

    def test_convert_speaker_null_image(self):
        s = self.mk_speaker_with_image("mail@email", None)
        image.convert_speaker_full_image_to_mimas_image(s)
        self.assertEquals(None, s.fullsize_picture)
        self.assertEquals(None, image.retrieve_image_key(s.key))


    def test_convert_speaker_list_full_image_to_mimas_image(self):
        data = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        s1 = self.mk_speaker_with_image("mail@email", data)
        s2 = self.mk_speaker_with_image("mail2@email", data)
        s3 = self.mk_speaker_with_image("mail3@email", data)

        spk_list = speaker.Speaker.query().fetch(keys_only=True)
        image.convert_speaker_list_full_image_to_mimas_image(spk_list)
        self.assertEquals(None, s1.fullsize_picture)
        self.assertEquals(None, s2.fullsize_picture)
        self.assertEquals(None, s3.fullsize_picture)

        self.assertEquals(data, image.retrieve_image_key(s1.key).get().picture)
        self.assertEquals(data, image.retrieve_image_key(s2.key).get().picture)
        self.assertEquals(data, image.retrieve_image_key(s3.key).get().picture)
