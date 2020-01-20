#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

import unittest

# Library imports
from google.appengine.ext import testbed

# Local imports
from conference_lib import conference
from conference_lib import confmsgs
from speaker_lib import protospeaker


class TestConferenceMsg(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def common_data_setup(self):
        self.c = conference.Conference()
        self.c.name = "TestConf"
        self.c.creator_id = "creator@hogwarts.org"
        self.c.set_contact_email("contact@hogwarts.org")
        self.c.put()

    def test_conf_created_msg(self):
        self.common_data_setup()
        message = confmsgs.make_conference_created_msg(self.c)

        self.assertEquals("creator@hogwarts.org", message.to_address())
        self.assertEquals("Mimas conference_lib system", message.from_name())
        self.assertEquals("contact@confreview.com", message.from_address())
        self.assertEquals(["allankellynet@gmail.com"], message.cc_addresses(None))
        self.assertEquals(None, message.bcc_addresses(None))

    def test_speaker_request_msg(self):
        self.common_data_setup()

        proto = protospeaker.mk_proto_speaker(None, "harry potter", "harry@hogwarts.org")
        message = confmsgs.make_speaker_request_msg(self.c, proto)

        self.assertEquals("harry@hogwarts.org", message.to_address())
        self.assertEquals("TestConf", message.from_name())
        self.assertEquals("contact@hogwarts.org", message.from_address())
        self.assertEquals(None, message.cc_addresses(None))
        self.assertEquals(None, message.bcc_addresses(None))

        substitution = message.make_substitutions_map(None)
        self.assertTrue(substitution.has_key("%CONFERENCE_SPEAKER_REQUEST_URL%"))
