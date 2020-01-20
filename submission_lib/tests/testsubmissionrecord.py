#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

import submission_lib.submissions_aux
from conference_lib import conference
from conference_lib import confstate
from speaker_lib import speaker
from submission_lib import submissionrecord, submissionnotifynames, voterecord
from talk_lib import talk


class TestSubmissionRecord(unittest.TestCase):
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
        self.s.set_names("Arnold", "Rimmer")
        self.s.put()

        self.t = talk.Talk(parent=self.s.key)
        self.t.title = "A testing talk"
        self.t.put()

    def test_record(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 1)

        c2 = conference.Conference()
        c2.name = "AnotherConf"
        c2.put()
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(c2.key)), 0)

        sub_key.get().withdraw()
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 0)

    def test_pass_through_funcs(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 1)

        self.assertEquals(sub_key.get().title(), "A testing talk")
        self.assertEquals(sub_key.get().submitter(), "Arnold Rimmer")
        self.assertEquals(sub_key.get().first_name(), "Arnold")
        self.assertEquals(sub_key.get().last_name(), "Rimmer")

    def test_expenses(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 1)

        sub = sub_key.get()
        sub.set_expenses_expectation("Long haul")
        sub.put()

        self.assertEquals(sub.expenses, "Long haul")

    def test_delete_talk_submissions(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")

        t2 = talk.Talk()
        t2.title = "Another testing talk"
        t2.put()
        sub_key = submissionrecord.make_submission(t2.key, self.c.key, "track", "format")

        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 2)

        submissionrecord.delete_submission_by_talk(self.t.key)
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 1)

    def test_reviewer_voting_score(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")

        self.assertEquals(sub_key.get().reviewer_voting_score("Fred", 1), 0)
        self.assertEquals(sub_key.get().reviewer_voting_msg("Fred", 1), "No vote")
        self.assertEquals(sub_key.get().reviewer_voting_comment("Fred", 1), "")


        voterecord.cast_new_vote(sub_key, "Fred", -2, "I hate this talk", 1)
        voterecord.cast_new_vote(sub_key, "Jim", 1, "I sort of like this talk", 1)

        self.assertEquals(sub_key.get().reviewer_voting_score("Fred", 1), -2)
        self.assertEquals(sub_key.get().reviewer_voting_msg("Fred", 1), -2)
        self.assertEquals(sub_key.get().reviewer_voting_comment("Fred", 1), "I hate this talk")
        self.assertEquals(sub_key.get().reviewer_voting_score("Jim", 1), 1)
        self.assertEquals(sub_key.get().reviewer_voting_comment("Jim", 1), "I sort of like this talk")

    def test_submission_scores(self):
        self.create_conference()

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")

        voterecord.cast_new_vote(sub_key, "Fred", -2, "I hate this talk", 1)
        voterecord.cast_new_vote(sub_key, "Jim", 1, "I sort of like this talk", 1)
        voterecord.cast_new_vote(sub_key, "Sheila", 1, "I like this talk", 1)
        submissions = submissionrecord.retrieve_submissions_records(self.c.key)
        self.assertEquals(len(submissions), 1)
        scores = submissions[0].get_scores(1)
        self.assertEquals(scores.total_score, 0)
        self.assertEquals(scores.mean_score, 0)
        self.assertEquals(scores.median_score, 1.0)
        self.assertEquals(scores.votes, 3)

        t2 = talk.Talk()
        t2.title = "Unreviewed"
        t2.put()
        sub_key = submissionrecord.make_submission(t2.key, self.c.key, "track", "format")
        scores2 = sub_key.get().get_scores(1)
        self.assertEquals(scores2.total_score, 0)
        self.assertEquals(scores2.mean_score, 0)
        self.assertEquals(scores2.median_score, 0)
        self.assertEquals(scores2.votes, 0)


    def test_final_decision(self):
        self.create_conference()

        sub_key1 = submissionrecord.make_submission(self.t.key, self.c.key, "TrackB", "format")
        sub1 = sub_key1.get()

        sub1.set_review_decision(1, "Round2")
        self.assertEquals(sub1.final_decision(), "Round2")
        confstate.close_round1_and_open_round2(self.c)

        self.assertEquals(sub1.final_decision(), "No decision")
        sub1.set_review_decision(2, "Accept")
        self.assertEquals(sub1.final_decision(), "Accept")

    def test_track_and_format(self):
        self.create_conference()

        t = talk.Talk()
        t.title = "A testing talk"
        t.put()

        subs_key = submissionrecord.make_submission(t.key, self.c.key, "Track1", "WithComputers")
        self.assertEquals(subs_key.get().track, "Track1")
        self.assertEquals(subs_key.get().delivery_format, "WithComputers")

    def test_talk_submissions(self):
        self.create_conference()

        t = talk.Talk()
        t.title = "A testing talk"
        t.put()

        self.assertEquals(len(submissionrecord.get_subs_for_talk(t.key)), 0)
        self.assertEquals(len(submissionrecord.get_confences_talk_submitted_to(t.key)), 0)

        sub_key = submissionrecord.make_submission(t.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.get_subs_for_talk(t.key)), 1)

        self.assertEquals(len(submissionrecord.get_confences_talk_submitted_to(t.key)), 1)
        self.assertEquals(submissionrecord.get_confences_talk_submitted_to(t.key)[0], "TestConf")

    def test_submissions_conference_map(self):
        self.create_conference()

        c2 = conference.Conference()
        c2.name = "Another Conf"
        c2.put()

        self.assertEquals(len(submissionrecord.get_subs_for_talk(self.t.key)), 0)
        self.assertEquals(len(submissionrecord.get_confences_talk_submitted_to(self.t.key)), 0)

        sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.get_subs_for_talk(self.t.key)), 1)

        self.assertEquals(len(submissionrecord.submissions_conference_map(self.t.key)), 1)
        self.assertEquals(submissionrecord.submissions_conference_map(self.t.key)[sub_key.urlsafe()], "TestConf")

        sub_key = submissionrecord.make_submission(self.t.key, c2.key, "track", "format")
        self.assertEquals(len(submissionrecord.get_subs_for_talk(self.t.key)), 2)

        self.assertEquals(len(submissionrecord.submissions_conference_map(self.t.key)), 2)
        self.assertEquals(submissionrecord.submissions_conference_map(self.t.key)[sub_key.urlsafe()], "Another Conf")

    def test_decision_summary(self):
        self.create_conference()

        t = talk.Talk()
        t.title = "A testing talk"
        t.put()

        submission = submissionrecord.make_submission(t.key, self.c.key, "track", "format").get()
        decision_summary = submissionrecord.get_decision_summary(self.c.key, "track", 1)

        self.assertEquals(len(decision_summary), 1)
        self.assertEquals(decision_summary["No decision"], 1)

        submission.set_review_decision(1, "Accept")
        submission.put()

        decision_summary = submissionrecord.get_decision_summary(self.c.key, "track", 1)
        self.assertEquals(len(decision_summary), 2)

        self.assertEquals(decision_summary["Accept"], 1)
        self.assertEquals(decision_summary["No decision"], 0)

        t2 = talk.Talk()
        t2.title = "A bad test"
        t2.put()

        sub2 = submissionrecord.make_submission(t2.key, self.c.key, "track", "format").get()
        sub2.set_review_decision(1, "Reject")
        sub2.put()

        decision_summary = submissionrecord.get_decision_summary(self.c.key, "track", 1)
        self.assertEquals(len(decision_summary), 3)
        self.assertEquals(decision_summary["Reject"], 1)
        self.assertEquals(decision_summary["No decision"], 0)

        t3 = talk.Talk()
        t3.title = "A good test"
        t3.put()

        sub3 = submissionrecord.make_submission(t3.key, self.c.key, "track", "format").get()
        sub3.set_review_decision(1, "Accept")
        sub3.put()

        decision_summary = submissionrecord.get_decision_summary(self.c.key, "track", 1)
        self.assertEquals(len(decision_summary), 3)
        self.assertEquals(decision_summary["Accept"], 2)
        self.assertEquals(decision_summary["Reject"], 1)
        self.assertEquals(decision_summary["No decision"], 0)

        decision_summary = submissionrecord.get_decision_summary(self.c.key, "another track", 1)
        self.assertEquals(len(decision_summary), 1)

    def test_sort_submissions_low__to_high(self):
        self.create_conference()

        t3 = talk.Talk()
        t3.title = "A round talk"
        t3.put()
        sub_key3 = submissionrecord.make_submission(t3.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key3, "Fred", 1, "I like this talk", 1)

        t1 = talk.Talk()
        t1.title = "A testing talk"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key1, "Fred", -2, "I hate this talk", 1)

        t4 = talk.Talk()
        t4.title = "Another round talk"
        t4.put()
        sub_key4 = submissionrecord.make_submission(t4.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key4, "Fred", 2, "I really like this talk", 1)

        t2 = talk.Talk()
        t2.title = "Another testing talk"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key2, "Fred", -1, "I dislike this talk", 1)

        submissions = submissionrecord.retrieve_submissions_records(self.c.key)
        sorted_submissions = submissionrecord.sort_low_to_high(submissions, "Fred", 1)

        self.assertEquals(len(sorted_submissions), 4)
        self.assertEquals(sorted_submissions[0].title(), t1.title)
        self.assertEquals(sorted_submissions[1].title(), t2.title)
        self.assertEquals(sorted_submissions[2].title(), t3.title)
        self.assertEquals(sorted_submissions[3].title(), t4.title)

    def test_sort_submissions_by_total(self):
        self.create_conference()


        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key1, "Fred", -2, "I hate this talk", 1)
        voterecord.cast_new_vote(sub_key1, "Jill", -2, "I hate this talk too", 1)

        t2 = talk.Talk()
        t2.title = "Talk T2"
        t2.put()
        sub_key2 = submissionrecord.make_submission(t2.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key2, "Fred", -1, "I dislike this talk", 1)
        voterecord.cast_new_vote(sub_key2, "Jill", 2, "Like", 1)

        t3 = talk.Talk()
        t3.title = "Talk T3...."
        t3.put()
        sub_key3 = submissionrecord.make_submission(t3.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key3, "Fred", 1, "I like this talk", 1)
        voterecord.cast_new_vote(sub_key3, "Jill", 2, "Like too", 1)

        submissions = submissionrecord.retrieve_submissions_records(self.c.key)

        sorted_submissions = submissionrecord.sort_submissions_by_total_low_to_high(submissions, 1)

        self.assertEquals(len(sorted_submissions), 3)
        self.assertEquals(sorted_submissions[0].title(), t1.title)
        self.assertEquals(sorted_submissions[0].get_scores(1).total_score, -4)
        self.assertEquals(sorted_submissions[1].title(), t2.title)
        self.assertEquals(sorted_submissions[1].get_scores(1).total_score, 1)
        self.assertEquals(sorted_submissions[2].title(), t3.title)
        self.assertEquals(sorted_submissions[2].get_scores(1).total_score, 3)

        rev_sorted_submissions = submissionrecord.sort_submissions_by_total_high_to_low(submissions, 1)

        self.assertEquals(len(rev_sorted_submissions), 3)
        self.assertEquals(rev_sorted_submissions[0].title(), t3.title)
        self.assertEquals(rev_sorted_submissions[0].get_scores(1).total_score, 3)
        self.assertEquals(rev_sorted_submissions[1].title(), t2.title)
        self.assertEquals(rev_sorted_submissions[1].get_scores(1).total_score, 1)
        self.assertEquals(rev_sorted_submissions[2].title(), t1.title)
        self.assertEquals(rev_sorted_submissions[2].get_scores(1).total_score, -4)

        voterecord.cast_new_vote(sub_key2, "Jim", +3, "Brill", 1)
        voterecord.cast_new_vote(sub_key2, "Shiela", +3, "Super", 1)
        mean_sorted = submissionrecord.sort_submissions_by_mean_low_to_high(submissions, 1)

        self.assertEquals(len(mean_sorted), 3)
        self.assertEquals(mean_sorted[0].title(), t1.title)
        self.assertEquals(mean_sorted[0].get_scores(1).mean_score, -2)
        self.assertEquals(mean_sorted[1].title(), t3.title)
        self.assertEquals(mean_sorted[1].get_scores(1).mean_score, 1.5)
        self.assertEquals(mean_sorted[2].title(), t2.title)
        self.assertEquals(mean_sorted[2].get_scores(1).mean_score, 1.75)

        mean_sorted = submissionrecord.sort_submissions_by_mean_high_to_low(submissions, 1)

        self.assertEquals(len(mean_sorted), 3)
        self.assertEquals(mean_sorted[2].title(), t1.title)
        self.assertEquals(mean_sorted[2].get_scores(1).mean_score, -2)
        self.assertEquals(mean_sorted[1].title(), t3.title)
        self.assertEquals(mean_sorted[1].get_scores(1).mean_score, 1.5)
        self.assertEquals(mean_sorted[0].title(), t2.title)
        self.assertEquals(mean_sorted[0].get_scores(1).mean_score, 1.75)


        voterecord.cast_new_vote(sub_key3, "Jim", +3, "Brill", 1)
        voterecord.cast_new_vote(sub_key3, "Shiela", +2, "Super", 1)
        median_sorted = submissionrecord.sort_submissions_by_median_low_to_high(submissions, 1)

        self.assertEquals(len(median_sorted), 3)
        self.assertEquals(median_sorted[0].title(), t1.title)
        self.assertEquals(median_sorted[0].get_scores(1).median_score, -2)
        self.assertEquals(median_sorted[1].title(), t3.title)
        self.assertEquals(median_sorted[1].get_scores(1).median_score, 2)
        self.assertEquals(median_sorted[2].title(), t2.title)
        self.assertEquals(median_sorted[2].get_scores(1).median_score, 2.5)

    def test_get_scores(self):
        self.create_conference()

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")
        voterecord.cast_new_vote(sub_key1, "Fred", -2, "I hate this talk", 1)
        voterecord.cast_new_vote(sub_key1, "Jill", -2, "I hate this talk too", 1)

        scores1 = sub_key1.get().get_scores(1)
        self.assertEquals(scores1.mean_score, -2)
        self.assertEquals(scores1.median_score, -2)
        self.assertEquals(scores1.total_score, -4)
        self.assertEquals(scores1.votes, 2)

        scores2 = sub_key1.get().get_scores(2)
        self.assertEquals(scores2.mean_score, 0)
        self.assertEquals(scores2.median_score, 0)
        self.assertEquals(scores2.total_score, 0)
        self.assertEquals(scores2.votes, 0)

        voterecord.cast_new_vote(sub_key1, "Fred", 1, "One", 2)
        voterecord.cast_new_vote(sub_key1, "Jim", 2, "Two", 2)
        voterecord.cast_new_vote(sub_key1, "Shiela", 2, "Two two", 2)

        scores2 = sub_key1.get().get_scores(2)
        self.assertEquals(scores2.total_score, 5)
        self.assertEquals(scores2.mean_score, 1.67)
        self.assertEquals(scores2.median_score, 2)
        self.assertEquals(scores2.votes, 3)

    def test_get_submission_by_talk_and_conf(self):
        self.create_conference()

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")

        t2 = talk.Talk()
        t2.title = "Unsubmitted"
        t2.put()

        self.assertEquals(sub_key1, submissionrecord.get_submission_by_talk_and_conf(t1.key, "TestConf"))
        self.assertEquals(None, submissionrecord.get_submission_by_talk_and_conf(t2.key, "TestConf"))

        # does not get listed for other conferences
        c2 = conference.Conference()
        c2.name = "OtherConf"
        c2.put()

        self.assertEquals(None, submissionrecord.get_submission_by_talk_and_conf(t1.key, "OtherConf"))
        self.assertEquals(None, submissionrecord.get_submission_by_talk_and_conf(t2.key, "OtherConf"))


    def test_withdraw(self):
        self.create_conference()

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")

        self.assertFalse(sub_key1.get().is_withdrawn())
        sub_key1.get().withdraw()
        self.assertTrue(sub_key1.get().is_withdrawn())

    def test_submission_by_conf_and_talk(self):
        self.create_conference()

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")

        t2 = talk.Talk()
        t2.title = "Talk T2"
        t2.put()

        self.assertEquals(submissionrecord.get_submission_key(self.c.key, t1.key), sub_key1)
        self.assertEquals(submissionrecord.get_submission_key(self.c.key, t2.key), None)


    def test_speaker_comms_state(self):
        self.create_conference()

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")
        sub = sub_key.get()

        self.assertEquals(sub.communication, "None")
        sub.acknowledge_receipt()
        self.assertEquals(sub.communication, "Receipt acknowledged")
        sub.mark_decline_pending()
        self.assertEquals(sub.communication, "Decline pending")
        sub.mark_declined()
        self.assertEquals(sub.communication, "Decline sent")
        sub.mark_acccept_pending()
        self.assertEquals(sub.communication, "Accept pending")
        sub.mark_acccept()
        self.assertEquals(sub.communication, "Accept sent")
        sub.mark_accept_acknowledged()
        self.assertEquals(sub.communication, "Acceptance acknowledged")
        sub.mark_accept_declined()
        self.assertEquals(sub.communication, "Acceptance declined")
        sub.mark_accept_problem()
        self.assertEquals(sub.communication, "Acceptance problem")

        sub.mark_comms(submissionnotifynames.SUBMISSION_ACCEPTED)
        self.assertEquals(sub.communication, "Accept sent")

        sub.mark_comms(submissionnotifynames.SUBMISSION_FAILED_ACCEPT_NOTIFICATON)
        self.assertEquals(sub.communication, "Accept notification failed")


    def test_retrieve_conference_submissions_keys(self):
        self.create_conference()
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 0)

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub_key = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 1)

        subs_list = submissionrecord.retrieve_conference_submissions_keys(self.c.key)
        self.assertEquals(sub_key, subs_list[0])

        sub_key2 = submissionrecord.make_submission(t1.key, self.c.key, "track2", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions_keys(self.c.key)), 2)

        subs_list = submissionrecord.retrieve_conference_submissions_keys(self.c.key)
        self.assertListEqual([sub_key, sub_key2], subs_list)

    def test_gdpr(self):
        self.create_conference()

        t1 = talk.Talk()
        t1.title = "Talk T1"
        t1.put()
        sub = submissionrecord.make_submission(t1.key, self.c.key, "track", "format").get()

        self.assertFalse(sub.gdpr_agreed)
        sub.set_gdpr_agreement(True)
        self.assertTrue(sub.gdpr_agreed)
        sub.set_gdpr_agreement(False)
        self.assertFalse(sub.gdpr_agreed)
