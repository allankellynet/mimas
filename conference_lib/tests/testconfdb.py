#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed
from google.appengine.ext import ndb

from conference_lib import conference, confoptions
from conference_lib import confdb
from submission_lib import submissionrecord, voterecord
from speaker_lib import cospeaker

# Testing db retrieva methods which are not part of conference_lib class
# And may be limited by other concerns
class TestConferenceRetrieval(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_RetreiveAllConference(self):
        self.assertEquals(len(confdb.retrieve_all_conferences()), 0)

        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertEquals(len(confdb.retrieve_all_conferences()), 1)

    def test_retreive_all_conferences_by_state(self):
        self.assertEquals(len(confdb.retrieve_all_conferences()), 0)

        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()

        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Closed")), 1)
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Open")), 0)

        another_conf = conference.Conference()
        another_conf.name = "WorldConf 2017"
        another_conf.put()

        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Closed")), 2)
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Open")), 0)

        new_conf.open_for_submissions()
        new_conf.put()
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Closed")), 1)
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Open")), 1)

        new_conf.close_submissions()
        new_conf.put()

        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Closed")), 2)
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Open")), 0)

        new_conf.start_round1_reviews()
        new_conf.put()
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Closed")), 1)
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Open")), 0)
        self.assertEquals(len(confdb.retrieve_all_conferences_by_state("Round1Reviews")), 1)

    def test_get_conf_by_name(self):
        self.assertTrue(confdb.get_conf_by_name("WorldConf 2016") is None)
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()
        self.assertTrue(confdb.get_conf_by_name("WorldConf 2016") is not None)

    def test_get_conf_by_shortname(self):
        self.assertTrue(confdb.get_conf_by_name("WC2016") is None)
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.shortname = "WC2016"
        new_conf.put()
        self.assertTrue(confdb.get_conf_by_shortname("WC2016") is not None)

    def test_get_any_conf(self):
        self.assertTrue(confdb.get_any_conf() is None)
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()
        self.assertTrue(confdb.get_any_conf() is not None)

    def test_count_conferences(self):
        self.assertEquals(confdb.count_conferences(), 0)
        new_conf = conference.Conference()
        new_conf.name = "WorldConf 2016"
        new_conf.put()
        self.assertEquals(confdb.count_conferences(), 1)
        new_conf2 = conference.Conference()
        new_conf2.name = "WorldConf 2017"
        new_conf2.put()
        self.assertEquals(confdb.count_conferences(), 2)

    def test_retrieve_special_rights_conference(self):
        new_conf1 = conference.Conference()
        new_conf1.name = "WorldConf 2016"
        new_conf1.put()

        new_conf2 = conference.Conference()
        new_conf2.name = "WorldConf 2017"
        new_conf2.put()

        user = "Harry@Hogwarts"
        self.assertEquals(confdb.retrieve_special_rights_conferences(user), [])

        new_conf1.user_rights().add_permission(user, "ChangeConferenceState")
        confs = confdb.retrieve_special_rights_conferences(user)
        self.assertEquals(len(confs), 1)
        self.assertEquals(confs[0].name, "WorldConf 2016")

        new_conf2.user_rights().add_permission(user, "ChangeConferenceState")
        confs = confdb.retrieve_special_rights_conferences(user)
        self.assertEquals(len(confs), 2)

        user2 = "Ron@hogwarts.com"
        conferences = confdb.retrieve_special_rights_conferences(user2)
        self.assertEquals(conferences, [])

    def mk_test_data(self, name):
        new_conf = conference.Conference()
        new_conf.name = name
        new_conf.put()

        subm_key = submissionrecord.make_submission(None, new_conf.key, "Track", "Format")
        confoptions.make_conference_track(new_conf.key, "Track")

        voterecord.cast_new_vote(subm_key, "Harry", 2, "No comment", 1)
        cospeaker.make_cospeaker(subm_key, "Ron", "ron2hogwarts.com")
        return new_conf.key, subm_key

    def test_delete_conference(self):
        conf1_key, sub1_key = self.mk_test_data("WorldConf 1000")
        conf2_key, sub2_key = self.mk_test_data("WorldConf 2000")

        self.assertEquals(1, len(submissionrecord.retrieve_conference_submissions(conf1_key)))
        self.assertEquals(1, len(submissionrecord.retrieve_conference_submissions(conf2_key)))
        self.assertEquals(1, len(voterecord.find_existing_votes(sub1_key, 1)))
        self.assertEquals(1, len(voterecord.find_existing_votes(sub2_key, 1)))
        self.assertEquals(1, len(cospeaker.get_cospeakers(sub1_key)))
        self.assertEquals(1, len(cospeaker.get_cospeakers(sub2_key)))
        self.assertEquals(2, confoptions.get_next_counter(conf1_key))
        self.assertEquals(2, confoptions.get_next_counter(conf2_key))
        self.assertEquals(6, len(ndb.Query(ancestor=conf1_key).fetch()))
        self.assertEquals(6, len(ndb.Query(ancestor=conf2_key).fetch()))

        confdb.delete_conference(conf2_key)
        self.assertEquals(None, conf2_key.get())

        self.assertEquals(1, len(submissionrecord.retrieve_conference_submissions(conf1_key)))
        self.assertEquals(0, len(submissionrecord.retrieve_conference_submissions(conf2_key)))
        self.assertEquals(1, len(voterecord.find_existing_votes(sub1_key, 1)))
        self.assertEquals(None, voterecord.find_existing_votes(sub2_key, 1))
        self.assertEquals(1, len(cospeaker.get_cospeakers(sub1_key)))
        self.assertEquals(0, len(cospeaker.get_cospeakers(sub2_key)))
        self.assertEquals(3, confoptions.get_next_counter(conf1_key))

        self.assertEquals(0, len(ndb.Query(ancestor=conf2_key).fetch()))
        self.assertEquals(None, conf2_key.get())
        self.assertEquals(None, confdb.get_conf_by_name("WorldConf 2000"))

    def test_retrieve_conferences_in_review(self):
        self.assertEquals([], confdb.test_retrieve_conferences_not_finished())

        conf_open = conference.Conference()
        conf_open.name = "WorldConf 2016"
        conf_open.open_for_submissions()
        conf_open.put()

        conf_closed = conference.Conference()
        conf_closed.name = "WorldConf 2017"
        conf_closed.close_submissions()
        conf_closed.put()

        conf_r1_review = conference.Conference()
        conf_r1_review.name = "WorldConf 2018"
        conf_r1_review.start_round1_reviews()
        conf_r1_review.put()

        conf_r2_review = conference.Conference()
        conf_r2_review.name = "WorldConf 2019"
        conf_r2_review.start_round2_reviews()
        conf_r2_review.put()

        conf_finished = conference.Conference()
        conf_finished.name = "WorldConf 2020"
        conf_finished.finish_reviews()
        conf_finished.put()

        expected_results = [conf_r1_review, conf_r2_review]
        expected_results.sort()
        actual_results = confdb.test_retrieve_conferences_not_finished()
        actual_results.sort()
        self.assertEquals(expected_results, actual_results)

