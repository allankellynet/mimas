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
from mailmsg import custommsg


class TestCustomMsg(unittest.TestCase):
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
        self.c.put()

    def test_custommsg(self):
        self.common_data_setup()
        msg = custommsg.CustomMsg(parent=self.c.key)

        self.assertEquals(msg.name(), "")
        self.assertEquals(msg.subject(), "")
        self.assertEquals(msg.message(), "")
        self.assertEquals(msg.cc_addresses(None), None)
        self.assertEquals(msg.bcc_addresses(None), None)

        msg.set_name("Surprise!")
        self.assertEquals(msg.name(), "Surprise!")

        msg.set_subject_line("This is the end")
        self.assertEquals(msg.subject(), "This is the end")

        msg.set_message("One Two Three Four")
        self.assertEquals(msg.message(), "One Two Three Four")

    def test_mk_custommsg(self):
        self.common_data_setup()

        msg_key = custommsg.make_custom_msg(self.c.key, "Name", "Subject line", "Some message")

        self.assertEquals(msg_key.get().name(), "Name")
        self.assertEquals(msg_key.get().subject(), "Subject line")
        self.assertEquals(msg_key.get().message(), "Some message")

    def test_retrieve_custom_messages(self):
        self.common_data_setup()

        msg_key1 = custommsg.make_custom_msg(self.c.key, "Name1", "Subject line A", "Some message")
        msg_key2 = custommsg.make_custom_msg(self.c.key, "Name2", "Subject line B", "Some message")
        msg_key3 = custommsg.make_custom_msg(self.c.key, "Name3", "Subject line C", "Some message")
        msg_key4 = custommsg.make_custom_msg(self.c.key, "Name4", "Subject line D", "Some message")

        messages = custommsg.retrieve_custom_message(self.c.key)
        self.assertEquals(4, len(messages))
