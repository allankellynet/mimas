#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from scaffold import userrightsnames, userrights


class TestUserRights(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_is_reviewer(self):
        ur = userrights.UserRights(None)

        self.assertFalse(ur.is_track_reviewer("harry", "technology track"))
        self.assertFalse(ur.has_track_review_rights("harry"))

        ur.add_track_reviewer("harry", "technology track")
        self.assertTrue(ur.is_track_reviewer("harry", "technology track"))
        self.assertTrue(ur.has_track_review_rights("harry"))
        self.assertTrue(ur.tracks_to_review("harry"), ("technology track"))
        self.assertEquals(len(ur.tracks_to_review("harry")), 1)
        self.assertEquals(ur.tracks_to_review("harry"), ["technology track"])

        self.assertEquals(ur.track_assignments_string("harry"), "technology track")
        ur.add_track_reviewer("harry", "business")
        self.assertEquals(ur.track_assignments_string("harry"), "technology track, business")
        self.assertEquals(len(ur.tracks_to_review("harry")), 2)
        self.assertEquals(ur.tracks_to_review("harry"), ["technology track", "business"])

        ur.drop_track_reviewer("harry", "technology track")
        self.assertFalse(ur.is_track_reviewer("harry", "technology track"))
        self.assertTrue(ur.has_track_review_rights("harry"))
        self.assertEquals(len(ur.tracks_to_review("harry")), 1)
        self.assertEquals(ur.tracks_to_review("harry"), ["business"])

    def test_track_assignments(self):
        ur = userrights.UserRights(None)
        self.assertEquals(ur.track_assignments("harry"), [])

        ur.add_track_reviewer("harry", "track1")
        self.assertEquals(ur.track_assignments("harry"), ["track1"])

        ur.add_track_reviewer("harry", "track2")
        self.assertEquals(ur.track_assignments("harry"), ["track1", "track2"])

    def test_list_all_reviewers(self):
        ur = userrights.UserRights(None)

        self.assertEquals(len(ur.list_all_reviewers()), 0)

        ur.add_permission("admin", userrightsnames.CONF_ADMINISTRATOR)
        self.assertEquals(len(ur.list_all_reviewers()), 0)

        ur.add_permission("review1", userrightsnames.ROUND1_REVIEWER)
        self.assertEquals(len(ur.list_all_reviewers()), 1)
        self.assertEquals(ur.list_all_reviewers(), ["review1"])

        ur.add_permission("review2", userrightsnames.ROUND2_REVIEWER)
        self.assertEquals(len(ur.list_all_reviewers()), 2)
        self.assertEquals(ur.list_all_reviewers(), ["review1", "review2"])

        ur.add_permission("review3", userrightsnames.ROUND1_DECISION)
        self.assertEquals(len(ur.list_all_reviewers()), 3)
        self.assertEquals(ur.list_all_reviewers(), ["review1", "review2", "review3"])

        ur.add_permission("review4", userrightsnames.ROUND2_DECISION)
        self.assertEquals(len(ur.list_all_reviewers()), 4)
        self.assertEquals(ur.list_all_reviewers(), ["review1", "review2", "review3", "review4"])

        ur.add_permission("review1", userrightsnames.ROUND1_FULL_VIEW)
        self.assertEquals(len(ur.list_all_reviewers()), 4)
        self.assertEquals(ur.list_all_reviewers(), ["review1", "review2", "review3", "review4"])

        ur.add_permission("review2", userrightsnames.ROUND2_FULL_VIEW)
        self.assertEquals(len(ur.list_all_reviewers()), 4)
        self.assertEquals(ur.list_all_reviewers(), ["review1", "review2", "review3", "review4"])

    def test_add_drop_track_reviewers(self):
        ur = userrights.UserRights(None)

        self.assertFalse(ur.is_track_reviewer("harry", "technology track"))
        self.assertFalse(ur.is_track_reviewer("barry", "technology track"))

        ur.add_track_reviewer("harry", "technology track")
        self.assertTrue(ur.is_track_reviewer("harry", "technology track"))
        self.assertFalse(ur.is_track_reviewer("barry", "technology track"))

        ur.add_track_reviewer("barry", "technology track")
        self.assertTrue(ur.is_track_reviewer("harry", "technology track"))
        self.assertTrue(ur.is_track_reviewer("barry", "technology track"))

        ur.drop_track_reviewer("harry", "technology track")
        self.assertFalse(ur.is_track_reviewer("harry", "technology track"))
        self.assertTrue(ur.is_track_reviewer("barry", "technology track"))

    def test_drop_track(self):
        ur = userrights.UserRights(None)

        ur.add_track_reviewer("harry", "technology track")
        ur.add_track_reviewer("ron", "technology track")
        ur.add_track_reviewer("harry", "business")
        ur.add_track_reviewer("ron", "business")
        self.assertTrue(ur.is_track_reviewer("harry", "technology track"))
        self.assertTrue(ur.is_track_reviewer("ron", "technology track"))
        self.assertTrue(ur.is_track_reviewer("harry", "business"))
        self.assertTrue(ur.is_track_reviewer("ron", "business"))

        ur.drop_track("business")

        self.assertTrue(ur.is_track_reviewer("harry", "technology track"))
        self.assertTrue(ur.is_track_reviewer("ron", "technology track"))
        self.assertFalse(ur.is_track_reviewer("harry", "business"))
        self.assertFalse(ur.is_track_reviewer("ron", "business"))

    def test_remove_all_review_rights(self):
        ur = userrights.UserRights(None)

        self.assertFalse(ur.is_track_reviewer("harry", "technology track"))

        ur.add_track_reviewer("harry", "technology track")
        ur.add_track_reviewer("harry", "business")

        ur.remove_all_review_rights("harry")
        self.assertFalse(ur.is_track_reviewer("harry", "technology track"))
        self.assertFalse(ur.is_track_reviewer("harry", "business"))

    def test_permissions(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        user = "allan"

        self.assertTrue(c.user_rights() is not None)
        self.assertFalse(c.user_rights().has_permission(user, "ChangeConferenceState"))
        c.user_rights().add_permission(user, "ChangeConferenceState")
        self.assertTrue(c.user_rights().has_permission(user, "ChangeConferenceState"))
        c.user_rights().drop_permission(user, "ChangeConferenceState")
        self.assertFalse(c.user_rights().has_permission(user, "ChangeConferenceState"))

        self.assertFalse(c.user_rights().has_permission(user, "NoneSuch"))
        c.user_rights().drop_permission(user, "NoneSuch")
        self.assertFalse(c.user_rights().has_permission(user, "NoneSuch"))

        self.assertFalse(c.user_rights().has_permission(user, "AppointReviewers"))
        c.user_rights().add_permission(user, "AppointReviewers")
        self.assertTrue(c.user_rights().has_permission(user, "AppointReviewers"))

        c.user_rights().add_permission(user, "ChangeConferenceState")
        c.user_rights().add_permission(user, "AppointReviewers")
        c.user_rights().drop_all_permissions(user)
        self.assertFalse(c.user_rights().has_permission(user, "ChangeConferenceState"))
        self.assertFalse(c.user_rights().has_permission(user, "AppointReviewers"))

        user2 = "Jim"
        self.assertEquals(c.user_rights().readable_permissions(user2), "")
        c.user_rights().add_permission(user2, "One")
        self.assertEquals(c.user_rights().readable_permissions(user2), "One")
        c.user_rights().add_permission(user2, "Two")
        self.assertEquals(c.user_rights().readable_permissions(user2), "Two, One")
        c.user_rights().add_permission(user2, "Three")
        self.assertEquals(c.user_rights().readable_permissions(user2), "One, Three, Two")

    def test_list_permission_holders(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        c.user_rights().add_permission("One", "Permission")
        self.assertEquals(c.user_rights().list_permission_holders(), ["One"])
        c.user_rights().add_permission("Two", "More Permission")
        self.assertEquals(c.user_rights().list_permission_holders(), ["One", "Two"])

    def test_can_view_all(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        c.user_rights().add_permission("User1", "Permission")
        self.assertFalse(c.user_rights().can_view_all("User1"))

        c.user_rights().add_permission("User1", userrightsnames.ROUND1_DECISION)
        self.assertTrue(c.user_rights().can_view_all("User1"))
        c.user_rights().drop_all_permissions("User1")

        c.user_rights().add_permission("User1", userrightsnames.ROUND2_DECISION)
        self.assertTrue(c.user_rights().can_view_all("User1"))
        c.user_rights().drop_all_permissions("User1")

        c.user_rights().add_permission("User1", userrightsnames.ROUND1_FULL_VIEW)
        self.assertTrue(c.user_rights().can_view_all("User1"))
        c.user_rights().drop_all_permissions("User1")

        c.user_rights().add_permission("User1", userrightsnames.ROUND2_FULL_VIEW)
        self.assertTrue(c.user_rights().can_view_all("User1"))
        c.user_rights().drop_all_permissions("User1")

    def test_has_special_rights(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertFalse(c.user_rights().has_special_rights("User1"))
        c.user_rights().add_permission("User1", "Permission")
        self.assertTrue(c.user_rights().has_special_rights("User1"))

        self.assertFalse(c.user_rights().has_special_rights("User2"))
        c.user_rights().add_track_reviewer("User2", "technology track")
        self.assertTrue(c.user_rights().has_special_rights("User2"))

        self.assertFalse(c.user_rights().has_special_rights("User3"))
        c.user_rights().add_permission("User3", "Permission")
        c.user_rights().add_track_reviewer("User3", "technology track")
        self.assertTrue(c.user_rights().has_special_rights("User3"))

    def test_has_review_rights(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertFalse(c.user_rights().has_review_rights("User1"))
        c.user_rights().add_permission("User1", userrightsnames.ROUND1_REVIEWER)
        self.assertTrue(c.user_rights().has_review_rights("User1"))

        self.assertFalse(c.user_rights().has_review_rights("User2"))
        c.user_rights().add_permission("User2", userrightsnames.ROUND2_REVIEWER)
        self.assertTrue(c.user_rights().has_review_rights("User2"))

        self.assertFalse(c.user_rights().has_review_rights("User3"))
        c.user_rights().add_permission("User3", userrightsnames.ROUND1_DECISION)
        self.assertTrue(c.user_rights().has_review_rights("User3"))

        c.user_rights().drop_all_permissions("User3")
        self.assertFalse(c.user_rights().has_review_rights("User3"))
        c.user_rights().add_permission("User3", userrightsnames.ROUND2_DECISION)
        self.assertTrue(c.user_rights().has_review_rights("User3"))

        c.user_rights().drop_all_permissions("User3")
        self.assertFalse(c.user_rights().has_review_rights("User3"))
        c.user_rights().add_permission("User3", userrightsnames.ROUND1_FULL_VIEW)
        self.assertTrue(c.user_rights().has_review_rights("User3"))

        c.user_rights().drop_all_permissions("User3")
        self.assertFalse(c.user_rights().has_review_rights("User3"))
        c.user_rights().add_permission("User3", userrightsnames.ROUND2_FULL_VIEW)
        self.assertTrue(c.user_rights().has_review_rights("User3"))

    def test_has_decision(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertFalse(c.user_rights().has_decision_rights("User1"))
        c.user_rights().add_permission("User1", userrightsnames.ROUND1_DECISION)
        self.assertTrue(c.user_rights().has_decision_rights("User1"))

        self.assertFalse(c.user_rights().has_decision_rights("User2"))
        c.user_rights().add_permission("User2", userrightsnames.ROUND2_DECISION)
        self.assertTrue(c.user_rights().has_decision_rights("User2"))

    def test_has_decision_right_for_round(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertFalse(c.user_rights().has_decision_right_for_round("email@address.com", 1))
        self.assertFalse(c.user_rights().has_decision_right_for_round("email@address.com", 2))

        c.user_rights().add_permission("email@address.com", userrightsnames.ROUND1_DECISION)
        self.assertTrue(c.user_rights().has_decision_right_for_round("email@address.com", 1))
        self.assertFalse(c.user_rights().has_decision_right_for_round("email@address.com", 2))

        c.user_rights().add_permission("email@address.com", userrightsnames.ROUND2_DECISION)
        self.assertTrue(c.user_rights().has_decision_right_for_round("email@address.com", 1))
        self.assertTrue(c.user_rights().has_decision_right_for_round("email@address.com", 2))

        c.user_rights().drop_permission("email@address.com", userrightsnames.ROUND2_DECISION)
        self.assertTrue(c.user_rights().has_decision_right_for_round("email@address.com", 1))
        self.assertFalse(c.user_rights().has_decision_right_for_round("email@address.com", 2))

        c.user_rights().drop_permission("email@address.com", userrightsnames.ROUND1_DECISION)
        self.assertFalse(c.user_rights().has_decision_right_for_round("email@address.com", 1))
        self.assertFalse(c.user_rights().has_decision_right_for_round("email@address.com", 2))

    def test_list_reviewers(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals([], c.user_rights().list_reviewers(1))
        self.assertEquals([], c.user_rights().list_reviewers(2))

        c.user_rights().add_permission("User1", userrightsnames.ROUND1_REVIEWER)
        self.assertEquals(["User1"], c.user_rights().list_reviewers(1))
        self.assertEquals([], c.user_rights().list_reviewers(2))

        c.user_rights().add_permission("User2", userrightsnames.ROUND1_REVIEWER)
        c.user_rights().add_permission("User3", userrightsnames.ROUND1_REVIEWER)
        self.assertItemsEqual(["User2", "User3", "User1"], c.user_rights().list_reviewers(1))
        self.assertEquals([], c.user_rights().list_reviewers(2))

        c.user_rights().add_permission("User20", userrightsnames.ROUND2_REVIEWER)
        self.assertItemsEqual(["User1", "User3", "User2"], c.user_rights().list_reviewers(1))
        self.assertEquals(["User20"], c.user_rights().list_reviewers(2))

