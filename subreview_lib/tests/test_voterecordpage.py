#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import unittest

from google.appengine.ext import testbed

# local imports
from conference_lib import conference
from speaker_lib import speaker
from submission_lib import submissionrecord
from subreview_lib import reviewer

# Target of tests
from subreview_lib import votingrecordspage
# A lot of logic has made its way into votingrecordpage.py
# Logic should be tested

class TestReviewer(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.conference = conference.Conference()
        self.conference.name = "TestConf"
        self.conference.put()

    def tearDown(self):
        self.testbed.deactivate()

    def test_reviewer_complete_description(self):
        self.assertEquals("",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "nosuch@revewer", 1))

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "rimmer@email")
        self.assertEquals("",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 1))
        self.assertEquals("",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 2))

        reviewer1.set_complete(True, review_round=1)
        self.assertEquals("Complete",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 1))
        self.assertEquals("",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 2))

        reviewer1.set_complete(True, review_round=2)
        self.assertEquals("Complete",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 1))
        self.assertEquals("Complete",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 2))

        reviewer1.set_complete(False, 1)
        self.assertEquals("",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 1))
        self.assertEquals("Complete",
                          votingrecordspage.reviewer_complete_description(self.conference.key, "rimmer@email", 2))
