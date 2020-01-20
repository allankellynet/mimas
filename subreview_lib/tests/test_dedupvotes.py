#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

import unittest

# Library imports
from google.appengine.ext import testbed

from conference_lib import conference
from submission_lib import submissionrecord, voterecord
from subreview_lib import dedupvotes
# Local imports
from talk_lib import talk


class TestVoteDeDup(unittest.TestCase):
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

        # Set up the scenario
        t1 = talk.Talk()
        t1.title = "Talk1 - No duplicate votes"
        t1.put()

        subs_key1 = submissionrecord.make_submission(t1.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(self.c.key)), 1)

        t2 = talk.Talk()
        t2.title = "Talk2 - Allan duplicate votes"
        t2.put()

        subs_key2 = submissionrecord.make_submission(t2.key, self.c.key, "track", "format")
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(self.c.key)), 2)

        return [subs_key1, subs_key2]

    def test_extract_reviewers(self):
        votes = [voterecord.cast_new_vote(None, "Allan", 0, "None", 1),
                 voterecord.cast_new_vote(None, "Grisha", 0, "None", 1),
                 voterecord.cast_new_vote(None, "Anton", 0, "None", 1),
                 voterecord.cast_new_vote(None, "Allan", 0, "None", 1)]

        reviewers = dedupvotes.extract_reviewers(votes)
        self.assertEqual(len(reviewers), 3)
        reviewers.sort()
        self.assertEqual(reviewers[0], "Allan")
        self.assertEqual(reviewers[1], "Anton")
        self.assertEqual(reviewers[2], "Grisha")

    def test_reviewer_votes(self):
        submission_keys = self.common_data_setup()

        votes_cast = []
        self.assertEquals(len(dedupvotes.reviewer_votes("Anton", votes_cast)), 0)
        self.assertEquals(len(dedupvotes.reviewer_votes("Allan", votes_cast)), 0)
        self.assertEquals(len(dedupvotes.reviewer_votes("Grisha", votes_cast)), 0)

        votes_cast.append(voterecord.cast_new_vote(submission_keys[0], "Allan", 1, "One", 1))
        votes_cast.append(voterecord.cast_new_vote(submission_keys[0], "Grisha", 2, "Two", 1))

        self.assertEquals(len(dedupvotes.reviewer_votes("Anton", votes_cast)), 0)
        self.assertEquals(len(dedupvotes.reviewer_votes("Allan", votes_cast)), 1)
        self.assertEquals(len(dedupvotes.reviewer_votes("Grisha", votes_cast)), 1)

        votes_cast.append(voterecord.cast_new_vote(submission_keys[0], "Grisha", 2, "Again!", 1))
        self.assertEquals(len(dedupvotes.reviewer_votes("Anton", votes_cast)), 0)
        self.assertEquals(len(dedupvotes.reviewer_votes("Allan", votes_cast)), 1)
        self.assertEquals(len(dedupvotes.reviewer_votes("Grisha", votes_cast)), 2)

    def test_find_and_remove_duplicate_votes(self):
        VotingRound = 1
        submission_keys = self.common_data_setup()

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[0], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        voterecord.cast_new_vote(submission_keys[0], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound)), 3)

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[1], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        # Set up the bug
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 5)

        # This is the bug
        # Because of extra vote the total is wrong
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 4)

        duplicates_list = dedupvotes.find_duplicate_votes(self.c.key, VotingRound)
        self.assertEquals(len(duplicates_list), 1)
        self.assertEquals(len(duplicates_list[duplicates_list.keys()[0]]), 3)
        self.assertEquals(len(duplicates_list["Allan"]), 3)

        dedupvotes.remove_duplicates(duplicates_list)

        # Check it was all done
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 3)

        # And the total score is now correct
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 2)

    def test_mutiple_submissions_without_duplicate_votes(self):
        VotingRound = 1
        submission_keys = self.common_data_setup()

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[0], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        voterecord.cast_new_vote(submission_keys[0], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], 1)), 3)

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[1], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Anton", -1, "Minus 1", VotingRound)
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 2)

        duplicates_list = dedupvotes.find_duplicate_votes(self.c.key, VotingRound)
        self.assertEquals(len(duplicates_list), 0)

        dedupvotes.remove_duplicates(duplicates_list)

        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 3)
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 2)

    def test_multiple_submissions_with_duplicate_votes(self):
        VotingRound = 1
        submission_keys = self.common_data_setup()

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[0], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        voterecord.cast_new_vote(submission_keys[0], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], 1)), 3)

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[1], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        # Set up the bug
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 5)

        # This is the bug
        # Because of extra vote the total is wrong
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 4)

        # Another submission with duplicae votes
        t3 = talk.Talk()
        t3.title = "Talk3 - Another submission with duplicates"
        t3.put()

        subs_key3 = submissionrecord.make_submission(t3.key, self.c.key, "track", "format")
        submission_keys.append(subs_key3)
        self.assertEquals(len(submissionrecord.retrieve_conference_submissions(self.c.key)), 3)
        voterecord.cast_new_vote(submission_keys[2], "Harry", 2, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[2], "Ron", 2, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[2], "Draco", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[2], "Draco", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[2], "Draco", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[2], "Percy", 3, "Three", VotingRound)
        # check the bug is in place
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[2], VotingRound)), 6)
        self.assertEqual(submission_keys[2].get().get_scores(VotingRound).total_score, 10)

        duplicates_list = dedupvotes.find_duplicate_votes(self.c.key, VotingRound)
        self.assertEquals(len(duplicates_list), 2)

        dedupvotes.remove_duplicates(duplicates_list)

        # Check it was all done
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[2], VotingRound)), 4)

        # And the total score is now correct
        self.assertEqual(submission_keys[0].get().get_scores(VotingRound).total_score, 2)
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 2)
        self.assertEqual(submission_keys[2].get().get_scores(VotingRound).total_score, 8)

    def test_dedup_leave_other_rounds(self):
        VotingRound = 1
        submission_keys = self.common_data_setup()

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[0], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        voterecord.cast_new_vote(submission_keys[0], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[0], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound)), 3)

        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_keys[1], "Allan", VotingRound)
        self.assertTrue(existing_vote is None)

        # Set up the bug
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Anton", -1, "Minus 1", VotingRound)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 5)

        # This is the bug
        # Because of extra vote the total is wrong
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 4)

        # Add votes for another round, also with duplicates
        voterecord.cast_new_vote(submission_keys[0], "Harry", 1, "One", VotingRound + 1)
        voterecord.cast_new_vote(submission_keys[0], "Ron", 2, "Two", VotingRound + 1)
        voterecord.cast_new_vote(submission_keys[0], "Percy", -1, "Minus 1", VotingRound + 1)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound + 1)), 3)
        voterecord.cast_new_vote(submission_keys[1], "Harry", 1, "One", VotingRound + 1)
        voterecord.cast_new_vote(submission_keys[1], "Harry", 1, "One", VotingRound + 1)
        voterecord.cast_new_vote(submission_keys[1], "Harry", 1, "One", VotingRound + 1)
        voterecord.cast_new_vote(submission_keys[1], "Ron", 2, "Two", VotingRound + 1)
        voterecord.cast_new_vote(submission_keys[1], "Percy", -1, "Minus 1", VotingRound + 1)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound + 1)), 5)

        duplicates_list = dedupvotes.find_duplicate_votes(self.c.key, VotingRound)
        self.assertEquals(len(duplicates_list), 1)
        self.assertEquals(len(duplicates_list[duplicates_list.keys()[0]]), 3)
        self.assertEquals(len(duplicates_list["Allan"]), 3)

        dedupvotes.remove_duplicates(duplicates_list)

        # Check it was all done
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound)), 3)

        # And the total score is now correct
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound).total_score, 2)

        # Check second round wasn't touched
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound + 1)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound + 1)), 5)

        # Fix it
        second_duplicates_list = dedupvotes.find_duplicate_votes(self.c.key, VotingRound + 1)
        dedupvotes.remove_duplicates(second_duplicates_list)

        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[0], VotingRound + 1)), 3)
        self.assertEquals(len(voterecord.find_existing_votes(submission_keys[1], VotingRound + 1)), 3)
        self.assertEqual(submission_keys[0].get().get_scores(VotingRound+1).total_score, 2)
        self.assertEqual(submission_keys[1].get().get_scores(VotingRound+1).total_score, 2)

    def test_retrieve_duplicate_report(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(dedupvotes.retrieve_duplicate_report(c.key), None)

        dedupvotes.generate_duplicate_vote_report(c.key, 1)
        self.assertNotEquals(dedupvotes.retrieve_duplicate_report(c.key), None)

    def test_delete_existing_reports(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        self.assertEquals(dedupvotes.retrieve_duplicate_report(c.key), None)

        dedupvotes.generate_duplicate_vote_report(c.key, 1)
        self.assertNotEquals(dedupvotes.retrieve_duplicate_report(c.key), None)

        dedupvotes.delete_vote_reports(c.key)
        self.assertEquals(dedupvotes.retrieve_duplicate_report(c.key), None)

    def test_report_has_duplicates(self):
        VotingRound = 1
        submission_keys = self.common_data_setup()

        self.assertEquals(dedupvotes.retrieve_duplicate_report(self.c.key), None)

        report = dedupvotes.generate_duplicate_vote_report(self.c.key, 1)
        self.assertFalse(report.has_duplicates())

        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Grisha", 2, "Two", VotingRound)
        voterecord.cast_new_vote(submission_keys[1], "Anton", -1, "Minus 1", VotingRound)
        self.assertFalse(report.has_duplicates())

        voterecord.cast_new_vote(submission_keys[1], "Allan", 1, "One", VotingRound)
        report = dedupvotes.generate_duplicate_vote_report(self.c.key, 1)
        self.assertTrue(report.has_duplicates())
