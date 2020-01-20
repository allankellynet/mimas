#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from speaker_lib import protospeaker


class TestTalk(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_basics(self):
        p = protospeaker.ProtoSpeaker()
        self.assertEquals("", p.email())
        self.assertEquals("", p.name())

        p.set_email("harry@hogwarts.org")
        self.assertEquals("harry@hogwarts.org", p.email())

        p.set_email("HARRY@hogwarts.ORG")
        self.assertEquals("harry@hogwarts.org", p.email())

        p.set_name("harry potter")
        self.assertEquals("harry potter", p.name())

    def test_mk_proto_speaker(self):
        p = protospeaker.mk_proto_speaker(None, "harry potter", "harry@hogwarts.org")
        self.assertEquals("harry@hogwarts.org", p.email())
        self.assertEquals("harry potter", p.name())

        q = protospeaker.mk_proto_speaker(None, "RON weasly", "RON@hogwarts.org")
        self.assertEquals("ron@hogwarts.org", q.email())
        self.assertEquals("RON weasly", q.name())
