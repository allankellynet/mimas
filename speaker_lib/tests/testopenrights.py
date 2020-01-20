#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from scaffold import userrightsnames, openrights


class TestOpenRights(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_has_permission(self):
        # most permission are live
        # except for creator which follows same rules as normal
        c = conference.Conference()
        c.name = "Test Dummy Conf"
        c.put()

        user = "allan"
        self.assertTrue(c.user_rights() is not None)
        self.assertFalse(c.user_rights().has_permission(user, "ChangeConferenceState"))
        self.assertFalse(c.user_rights().has_permission(user, "NoneSuch"))

        c.user_rights().add_permission(user, "ChangeConferenceState")
        c.user_rights().add_permission(user, "NoneSuch")

        self.assertTrue(c.user_rights() is not None)
        self.assertTrue(c.user_rights().has_permission(user, "ChangeConferenceState"))
        self.assertTrue(c.user_rights().has_permission(user, "NoneSuch"))

        self.assertFalse(c.user_rights().has_permission(user, userrightsnames.CONF_CREATOR))
        c.user_rights().add_permission(user, userrightsnames.CONF_CREATOR)
        self.assertTrue(c.user_rights().has_permission(user, userrightsnames.CONF_CREATOR))

    def test_has_special_rights(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        rights = openrights.OpenRights(c.key)
        self.assertTrue(rights.has_special_rights("Bert"))
        self.assertTrue(rights.has_special_rights("Jane"))
        self.assertTrue(rights.has_special_rights("Voldemort"))


