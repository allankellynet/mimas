#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from scaffold import sysinfo


class TestTalk(unittest.TestCase):
    def test_is_running_local(self):
        # tests should always be running locally!
        self.assertTrue(sysinfo.is_running_local())

    def test_home_url(self):
        # can't really test this one without running
        self.assertEquals(sysinfo.home_url(), "")

    def test_sysadmins(self):
        # for local running
        self.assertTrue(sysinfo.is_system_admin("test@example.com"))

        # the creator
        self.assertTrue(sysinfo.is_system_admin("allankellynet@gmail.com"))

        # all other email addresses should fail
        self.assertFalse(sysinfo.is_system_admin("hilary@clinton.com"))
        self.assertFalse(sysinfo.is_system_admin("fred@gmail.com"))
