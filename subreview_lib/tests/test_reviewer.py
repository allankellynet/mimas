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
from talk_lib import talk

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

    def setup_test_data(self):
        s = speaker.make_new_speaker("rimmer@email")
        s.name = "Arnold Rimmer"
        s.put()

        t1 = talk.Talk(parent=s.key)
        t1.title = "A testing talk"
        t1.put()

        sub_key1 = submissionrecord.make_submission(t1.key, self.conference.key, "track", "format")
        t2 = talk.Talk(parent=s.key)
        t2.title = "Another testing talk"
        t2.put()

        sub_key2 = submissionrecord.make_submission(t2.key, self.conference.key, "track", "format")
        s2 = speaker.make_new_speaker("cat@email")
        s2.name = "Cat"
        s2.put()

        t3 = talk.Talk(parent=s2.key)
        t3.title = "Cool for cats"
        t3.put()
        sub_key3 = submissionrecord.make_submission(t3.key, self.conference.key, "track", "format")

        return sub_key1, sub_key2, sub_key3


    def test_own_submissions(self):
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "rimmer@email")
        self.assertItemsEqual([sub_key1, sub_key2], reviewer1.own_submissions())

        reviewer2 = reviewer.make_new_reviewer(self.conference.key, "cat@email")
        self.assertItemsEqual([sub_key3], reviewer2.own_submissions())


    def test_current_review_assisgments(self):
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "rimmer@email")
        self.assertItemsEqual([], reviewer1.retrieve_review_assignments("track", review_round=1))
        self.assertItemsEqual([], reviewer1.retrieve_review_assignments_for_round(review_round=1))

        reviewer2 = reviewer.make_new_reviewer(self.conference.key, "cat@email")
        self.assertItemsEqual([], reviewer1.retrieve_review_assignments("track", review_round=1))

        reviewer1.assign_submission("track", [sub_key3], review_round=1)
        self.assertItemsEqual([sub_key3], reviewer1.retrieve_review_assignments("track", review_round=1))
        self.assertItemsEqual([sub_key3], reviewer1.retrieve_review_assignments_for_round(review_round=1))

        reviewer1.assign_submission("track", [sub_key2], review_round=1)
        self.assertItemsEqual([sub_key2, sub_key3], reviewer1.retrieve_review_assignments("track", review_round=1))
        self.assertItemsEqual([sub_key2, sub_key3], reviewer1.retrieve_review_assignments_for_round(review_round=1))

        reviewer2.assign_submission("track", [sub_key1, sub_key2], review_round=1)
        self.assertItemsEqual([sub_key2, sub_key1], reviewer2.retrieve_review_assignments("track", review_round=1))

        t4 = talk.Talk(parent=None)
        t4.title = "Nobody on another track"
        t4.put()
        sub_key4 = submissionrecord.make_submission(t4.key, self.conference.key, "another_track", "format")
        reviewer1.assign_submission("another_track", [sub_key4], review_round=1)
        self.assertItemsEqual([sub_key2, sub_key3], reviewer1.retrieve_review_assignments("track", review_round=1))
        self.assertItemsEqual([sub_key4], reviewer1.retrieve_review_assignments("another_track", review_round=1))
        self.assertItemsEqual([sub_key2, sub_key3, sub_key4], reviewer1.retrieve_review_assignments_for_round(review_round=1))


    def test_remove_review_assisgments(self):
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "rimmer@email")
        reviewer1.assign_submission("track", [sub_key1, sub_key3, sub_key2], review_round=1)
        self.assertItemsEqual([sub_key3, sub_key2, sub_key1],
                              reviewer1.retrieve_review_assignments("track", review_round=1))

        reviewer1.remove_assignment("track", review_round=1, target=sub_key1)
        self.assertItemsEqual([sub_key2, sub_key3],
                              reviewer1.retrieve_review_assignments("track", review_round=1))

        # Need to requery db to ensure update was made
        # Original version of remove_assignment missed a put() after operation
        refresh_reviewer = reviewer.get_reviewer(self.conference.key, "rimmer@email")
        self.assertItemsEqual([sub_key2, sub_key3],
                              refresh_reviewer.retrieve_review_assignments("track", review_round=1))


    def test_count_submission_reviewers(self):
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "rimmer@email")
        reviewer1.assign_submission("track", [sub_key1, sub_key2], review_round=1)

        reviewer2 = reviewer.make_new_reviewer(self.conference.key, "cat@email")
        reviewer2.assign_submission("track", [sub_key1], review_round=1)

        subs_count = reviewer.count_submission_reviewers([sub_key1, sub_key2, sub_key3], review_round=1)
        self.assertEqual(sub_key1, subs_count[0][0])
        self.assertEqual(2, subs_count[0][1])
        self.assertEqual(sub_key2, subs_count[1][0])
        self.assertEqual(1, subs_count[1][1])
        self.assertEqual(sub_key3, subs_count[2][0])
        self.assertEqual(0, subs_count[2][1])


    def test_assign_more_reviews(self):
        # basic test
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "lister@email")
        reviewer1.assign_more_reviews("track", 2, 1)
        self.assertEqual(2, len(reviewer1.retrieve_review_assignments("track", review_round=1)))

        reviewer2 = reviewer.make_new_reviewer(self.conference.key, "cat@email")
        self.assertEqual(2, len(reviewer1.retrieve_review_assignments("track", review_round=1)))
        reviewer2.assign_more_reviews("track", 2, 1)
        self.assertEqual(2, len(reviewer2.retrieve_review_assignments("track", review_round=1)))

        # three possible success scenarios - don't care which was chosen
        # on suubmission should be assigned to both reviewers
        # other submissions should both be assigned to one reviewer
        # less assigned submissions shoul be assigned first
        # then semi-random assignment up to totoal
        if (reviewer.count_submission_assignments(self.conference.key, sub_key1, 1)==2):
            print "*** First assignment case"
            self.assertEqual(1, reviewer.count_submission_assignments(self.conference.key, sub_key3, 1))
            self.assertEqual(1, reviewer.count_submission_assignments(self.conference.key, sub_key2, 1))
        elif (reviewer.count_submission_assignments(self.conference.key, sub_key2, 1) == 2):
            print "*** Second assignment case"
            self.assertEqual(1, reviewer.count_submission_assignments(self.conference.key, sub_key1, 1))
            self.assertEqual(1, reviewer.count_submission_assignments(self.conference.key, sub_key3, 1))
        elif (reviewer.count_submission_assignments(self.conference.key, sub_key3, 1) == 2):
            print "*** Third assignment case"
            self.assertEqual(1, reviewer.count_submission_assignments(self.conference.key, sub_key1, 1))
            self.assertEqual(1, reviewer.count_submission_assignments(self.conference.key, sub_key2, 1))
        else:
            self.assertFalse(True, "Unexpected assignment pattern")

        reviewer3 = reviewer.make_new_reviewer(self.conference.key, "kyton@email")
        reviewer3.assign_more_reviews("track", 2, 1)
        self.assertEqual(2, reviewer.count_submission_assignments(self.conference.key, sub_key1, 1))
        self.assertEqual(2, reviewer.count_submission_assignments(self.conference.key, sub_key2, 1))
        self.assertEqual(2, reviewer.count_submission_assignments(self.conference.key, sub_key3, 1))

        # check no repeated assignment
        reviewer1.assign_more_reviews("track", 2, 1)
        self.assertEqual(3, len(reviewer1.retrieve_review_assignments("track", review_round=1)))

        reviewer1.assign_more_reviews("track", 2, 1)
        self.assertEqual(3, len(reviewer1.retrieve_review_assignments("track", review_round=1)))

        # check no self-assignment
        rogue = "holy@email"
        s = speaker.make_new_speaker(rogue)
        s.name = "Holy"
        s.put()
        t4 = talk.Talk(parent=s.key)
        t4.title = "Lets see if the new speaker can review themselves"
        t4.put()
        sub_key4 = submissionrecord.make_submission(t4.key, self.conference.key, "track", "format")

        reviewer4 = reviewer.make_new_reviewer(self.conference.key, rogue)
        reviewer4.assign_more_reviews("track", 99, 1)
        self.assertItemsEqual([sub_key1, sub_key2, sub_key3],
                              reviewer4.retrieve_review_assignments("track", review_round=1))
        self.assertEqual(0, reviewer.count_submission_assignments(self.conference.key, sub_key4, 1))

    def set_round2(self, k):
        sub = k.get()
        sub.last_review_round = 2
        sub.put()

    def test_assign_limited_to_round(self):
        round1_key1, round1_sub_key2, round1_key3 = self.setup_test_data()

        reviewer1 = reviewer.make_new_reviewer(self.conference.key, "lister@email")
        reviewer1.assign_more_reviews("track", 99, 1)
        self.assertItemsEqual([round1_key1, round1_sub_key2, round1_key3],
                              reviewer1.retrieve_review_assignments("track", 1))

        round2_key4, round2_key5, round1_key6 = self.setup_test_data()
        self.set_round2(round2_key4)
        self.set_round2(round2_key5)

        reviewer1.assign_more_reviews("track", 99, 2)
        self.assertItemsEqual([round2_key4, round2_key5],
                              reviewer1.retrieve_review_assignments("track", 2))
        self.assertItemsEqual([round1_key1, round1_sub_key2, round1_key3],
                              reviewer1.retrieve_review_assignments("track", 1))


    def test_get_reviewer(self):
        self.assertIsNone(reviewer.get_reviewer(self.conference.key,
                                                "lister@redwarf.com"))

        reviewer.make_new_reviewer(self.conference.key, "lister@redwarf.com")
        r = reviewer.get_reviewer(self.conference.key, "lister@redwarf.com")
        self.assertIsNotNone(r)
        self.assertEquals("lister@redwarf.com", r.email)

    def test_count_assignments(self):
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        r = reviewer.make_new_reviewer(self.conference.key, "lister@redwarf.com")
        self.assertEquals(0, r.count_assignments(1))
        self.assertEquals(0, r.count_assignments(2))

        r.assign_submission("track", [sub_key1, sub_key2], review_round=1)
        self.assertEquals(2, r.count_assignments(1))

        r.assign_submission("track", [sub_key3], review_round=2)
        self.assertEquals(2, r.count_assignments(review_round = 1))
        self.assertEquals(1, r.count_assignments(review_round = 2))

        sub_key4, sub_key5, sub_key6 = self.setup_test_data()
        r.assign_submission("trackX", [sub_key4, sub_key5, sub_key6], review_round=1)
        self.assertEquals(1, r.count_assignments(review_round = 2))
        self.assertEquals(5, r.count_assignments(review_round = 1))

    def test_get_new_or_existing_reviewer(self):
        r = reviewer.get_reviewer(self.conference.key, "lister@redwarf.com")
        self.assertIsNone(r)

        r = reviewer.get_new_or_existing_reviewer(self.conference.key, "lister@redwarf.com")
        self.assertIsNotNone(r)

        q = reviewer.get_new_or_existing_reviewer(self.conference.key, "lister@redwarf.com")
        self.assertIsNotNone(q)
        self.assertEquals(q,r)

    def test_complete_flag(self):
        r = reviewer.get_new_or_existing_reviewer(self.conference.key, "lister@redwarf.com")
        self.assertIsNotNone(r)

        self.assertFalse(r.is_complete(review_round=1))
        r.set_complete(True, review_round=1)
        self.assertTrue(r.is_complete(review_round=1))
        r.set_complete(False, review_round=1)
        self.assertFalse(r.is_complete(review_round=1))

        self.assertFalse(r.is_complete(review_round=2))
        self.assertFalse(r.is_complete(review_round=1))
        r.set_complete(True, review_round=2)
        self.assertTrue(r.is_complete(review_round=2))
        self.assertFalse(r.is_complete(review_round=1))
        r.set_complete(False, review_round=2)
        self.assertFalse(r.is_complete(review_round=2))
        self.assertFalse(r.is_complete(review_round=1))

    def test_retrieve_reviewers(self):
        sub_key1, sub_key2, sub_key3 = self.setup_test_data()

        self.assertEquals(0, len(reviewer.get_reviewers(sub_key1, review_round=1)))
        self.assertEquals(0, len(reviewer.get_reviewers(sub_key1, review_round=2)))

        # new reviewer with no reviews
        r = reviewer.make_new_reviewer(self.conference.key, "lister@redwarf.com")

        # assign a submission
        r.assign_submission("track", [sub_key1], review_round=1)
        reviewers = reviewer.get_reviewers(sub_key1, review_round=1)
        self.assertEquals(1, len(reviewers))
        self.assertEquals([r.key], reviewers)

        r2 = reviewer.make_new_reviewer(self.conference.key, "rimmer@redwarf.com")
        r2.assign_submission("track", [sub_key1], review_round=1)
        reviewers = reviewer.get_reviewers(sub_key1, review_round=1)
        self.assertEquals(2, len(reviewers))
        self.assertEquals([r.key, r2.key], reviewers)
        self.assertEquals(0, len(reviewer.get_reviewers(sub_key1, review_round=2)))

        r3 = reviewer.make_new_reviewer(self.conference.key, "rimmer@redwarf.com")
        r3.assign_submission("track", [sub_key1], review_round=1)
        reviewers = reviewer.get_reviewers(sub_key1, review_round=1)
        self.assertEquals(3, len(reviewers))
        self.assertEquals([r.key, r2.key, r3.key], reviewers)
        self.assertEquals(0, len(reviewer.get_reviewers(sub_key1, review_round=2)))

        self.assertEquals(0, len(reviewer.get_reviewers(sub_key2, review_round=1)))
        self.assertEquals(0, len(reviewer.get_reviewers(sub_key3, review_round=1)))
