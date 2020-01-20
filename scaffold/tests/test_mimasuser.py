#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import datetime
import unittest

from google.appengine.ext import testbed

from scaffold import mimasuser
from speaker_lib import speaker


class TestMimasUser(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_basics(self):
        usr = mimasuser.mk_MimasUser("allan", "allan@earth.com", "unique")

        self.assertEquals("allan", usr.name())
        self.assertEquals("allan@earth.com", usr.email())
        self.assertEquals(None, usr.speaker_key())
        self.assertEquals("unique", usr.unique_id())
        self.assertEquals(datetime.datetime(2017,9,23), usr.last_login())

        now = datetime.datetime.now()
        usr.set_last_login(now)
        self.assertEquals(now, usr.last_login())

    def test_speaker_key(self):
        usr = mimasuser.mk_MimasUser("allan", "allan@earth.com", "unique")

        s = speaker.make_new_speaker("mail@email")
        usr.set_speaker_key(s.key)

        self.assertEquals(s.key, usr.speaker_key())

    def test_find_user_by_id(self):
        usr1 = mimasuser.mk_MimasUser("allan", "allan@earth.com", "allanId")

        self.assertEquals(mimasuser.find_user_by_id("allanId").name(), "allan")

        usr2 = mimasuser.mk_MimasUser("paul", "paul@earth.com", "paulId")
        usr3 = mimasuser.mk_MimasUser("grisha", "grisha@earth.com", "grishaId")

        self.assertEquals(mimasuser.find_user_by_id("allanId").name(), "allan")
        self.assertEquals(mimasuser.find_user_by_id("paulId").name(), "paul")

    def test_find_user_by_email(self):
        usr1 = mimasuser.mk_MimasUser("allan", "allan@earth.com", "allanId")

        self.assertEquals(mimasuser.find_user_by_email("allan@earth.com").name(), "allan")

        usr2 = mimasuser.mk_MimasUser("paul", "paul@earth.com", "paulId")
        usr3 = mimasuser.mk_MimasUser("grisha", "grisha@earth.com", "grishaId")

        self.assertEquals(mimasuser.find_user_by_email("allan@earth.com").name(), "allan")
        self.assertEquals(mimasuser.find_user_by_email("paul@earth.com").name(), "paul")

