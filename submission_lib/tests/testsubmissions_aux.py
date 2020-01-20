#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference, confstate
from speaker_lib import speaker
from talk_lib import talk
from submission_lib import submissionrecord, submissions_aux

class TestSubmissionAux(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def create_conference(self):
        self.c = conference.Conference()
        self.c.name = "TestConf"
        self.c.put()

        self.s = speaker.make_new_speaker("mail@email")
        self.s.name = "Arnold Rimmer"
        self.s.put()

        self.t = talk.Talk(parent=self.s.key)
        self.t.title = "A testing talk"
        self.t.put()

    def test_change_expenses(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option1")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(self.c.key)), 1)

        sub = sub_key.get()
        self.assertEquals("Option1", sub.expenses)
        submissions_aux.change_expenses(sub_key, "NotTheOption", "NewOption")
        self.assertEquals("Option1", sub.expenses)

        submissions_aux.change_expenses(sub_key, "Option1", "NewOption")
        self.assertEquals("NewOption", sub.expenses)


    def test_change_all_expenses(self):
        self.create_conference()

        sub_key1 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option1")
        sub_key2 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option2")
        sub_key3 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option3")
        sub_key4 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option2")

        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(self.c.key)), 4)
        submissions_aux.change_all_expenses(self.c.key, "Option2", "NewOption")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(self.c.key)), 4)

        self.assertEquals("Option1", sub_key1.get().expenses)
        self.assertEquals("NewOption", sub_key2.get().expenses)
        self.assertEquals("Option3", sub_key3.get().expenses)
        self.assertEquals("NewOption", sub_key4.get().expenses)

    def test_retrieve_submission_by_expenses(self):
        self.create_conference()

        sub_key1 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option1")
        sub = sub_key1.get()
        sub.set_expenses_expectation("Long haul")
        sub.put()

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Long haul")
        self.assertEquals(1, len(expenses_list))

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Short haul")
        self.assertEquals(0, len(expenses_list))

        sub_key2 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option1")
        sub = sub_key2.get()
        sub.set_expenses_expectation("Long haul")
        sub.put()

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Long haul")
        self.assertEquals(2, len(expenses_list))

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Short haul")
        self.assertEquals(0, len(expenses_list))

        sub_key3 = submissionrecord.make_submission_plus(self.t.key, self.c.key, "track", "format", "duration", "Option1")
        sub = sub_key3.get()
        sub.set_expenses_expectation("Short haul")
        sub.put()

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Long haul")
        self.assertEquals(2, len(expenses_list))

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Short haul")
        self.assertEquals(1, len(expenses_list))

        # now test for decision too
        no_filter_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "")
        self.assertEquals(3, len(no_filter_list))

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Long haul")
        self.assertEquals(2, len(expenses_list))

        expenses_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "Short haul")
        self.assertEquals(1, len(expenses_list))

        no_filter_list = submissions_aux.retrieve_submissions_by_expenses(self.c.key, "")
        self.assertEquals(3, len(no_filter_list))

    def test_retrieve_by_final_decision_track_ordered(self):
        self.create_conference()

        t = talk.Talk()
        t.title = "Decline round 1"
        t.put()
        sub_key1 = submissionrecord.make_submission(t.key, self.c.key, "TrackB", "format")
        sub1 = sub_key1.get()
        sub1.set_review_decision(1, "Decline")

        t2 = talk.Talk()
        t2.title = "Decline round 2"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "TrackA", "format")
        sub2 = sub_key2.get()
        sub2.set_review_decision(1, "Round2")

        t3 = talk.Talk()
        t3.title = "Accept round 2"
        t3.put()
        sub_key3 = submissionrecord.make_submission(t3.key, self.c.key, "TrackB", "format")
        sub3 = sub_key3.get()
        sub3.set_review_decision(1, "Round2")

        t4 = talk.Talk()
        t4.title = "Another round 2 accept in another track"
        t4.put()
        sub_key4 = submissionrecord.make_submission(t3.key, self.c.key, "TrackA", "format")
        sub4 = sub_key4.get()
        sub4.set_review_decision(1, "Round2")

        confstate.close_round1_and_open_round2(self.c)
        sub2.set_review_decision(2, "Decline")
        sub3.set_review_decision(2, "Accept")
        sub4.set_review_decision(2, "Accept")

        # Currently cannot accept a submission in round 1
        accepts = submissions_aux.retrieve_by_final_decision_track_ordered(self.c.key, "Accept")
        self.assertEquals(len(accepts), 2)
        self.assertEquals(accepts[0].final_decision(), "Accept")
        self.assertEquals(accepts[0].track, "TrackA")
        self.assertEquals(accepts[1].final_decision(), "Accept")
        self.assertEquals(accepts[1].track, "TrackB")

        declines = submissions_aux.retrieve_by_final_decision_track_ordered(self.c.key, "Decline")
        self.assertEquals(len(declines), 2)
        self.assertEquals(declines[0].title(), "Decline round 2")
        self.assertEquals(declines[0].final_decision(), "Decline")
        self.assertEquals(declines[0].track, "TrackA")
        self.assertEquals(declines[1].title(), "Decline round 1")
        self.assertEquals(declines[1].final_decision(), "Decline")
        self.assertEquals(declines[1].track, "TrackB")

        # and test unordered versions
        accepts = submissions_aux.retrieve_by_final_decision(self.c.key, "Accept")
        self.assertEquals(len(accepts), 2)
        self.assertEquals(accepts[0].final_decision(), "Accept")
        self.assertEquals(accepts[1].final_decision(), "Accept")

        declines = submissions_aux.retrieve_by_final_decision(self.c.key, "Decline")
        self.assertEquals(len(declines), 2)
        self.assertEquals(declines[0].final_decision(), "Decline")
        self.assertEquals(declines[1].final_decision(), "Decline")

    def test_retrieve_conference_submissions_by_track(self):
        self.create_conference()

        submissionrecord.make_submission(self.t.key, self.c.key, "Track1", "format")
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track1")), 1)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track2")), 0)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submission_keys_by_track(self.c.key, "Track1")), 1)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submission_keys_by_track(self.c.key, "Track2")), 0)

        t2 = talk.Talk()
        t2.title = "Talk 2"
        t2.put()

        submissionrecord.make_submission(t2.key, self.c.key, "Track1", "format")
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track1")), 2)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track2")), 0)

        t3 = talk.Talk()
        t3.title = "Talk 3 Track 2"
        t3.put()

        sub_key3 = submissionrecord.make_submission(t3.key, self.c.key, "Track2", "format")
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track1")), 2)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track2")), 1)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submission_keys_by_track(self.c.key, "Track1")), 2)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submission_keys_by_track(self.c.key, "Track2")), 1)

        sub_key3.get().withdraw()
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track1")), 2)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track2")), 0)

    def test_retrieve_conference_submission_keys_by_track_and_round(self):
        self.create_conference()

        sub_key1 = submissionrecord.make_submission(self.t.key, self.c.key, "Track1", "format")
        sub = sub_key1.get()
        sub.last_review_round = 2
        sub.put()

        t2 = talk.Talk()
        t2.title = "Talk 2"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "Track1", "format")

        t3 = talk.Talk()
        t3.title = "Talk 3"
        t3.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "Track3", "format")

        subs_round2track1 = submissions_aux.retrieve_conference_submission_keys_by_track_and_round(
                self.c.key, "Track1", 2)
        self.assertEquals(len(subs_round2track1), 1)
        self.assertItemsEqual([sub_key1], subs_round2track1)

        self.assertEquals(len(
            submissions_aux.retrieve_conference_submission_keys_by_track(self.c.key, "Track2")), 0)

        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track1")), 2)
        self.assertEquals(len(
            submissions_aux.retrieve_conference_submissions_by_track(self.c.key, "Track2")), 0)
