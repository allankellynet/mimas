#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference, confquestion
from submission_lib import submissionrecord, submission_ans


class TestSubmissionAnswer(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def create_conference(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()

        return c

    def test_mk_answer(self):
        c = self.create_conference()
        question_key = confquestion.mk_question(c.key, "Yes or no?").key

        sub_key = submissionrecord.make_submission(None, c.key, "track", "format")

        ans = submission_ans.mk_answer(sub_key, question_key, "The answer is yes")

        self.assertEqual("The answer is yes", ans.answer())
        self.assertEqual(question_key, ans.question_key)

    def test_make_or_update(self):
        c = self.create_conference()
        question_key = confquestion.mk_question(c.key, "Yes or no?").key

        sub_key = submissionrecord.make_submission(None, c.key, "track", "format")

        ans = submission_ans.make_or_update(sub_key, question_key, "The answer is yes")
        self.assertEqual("The answer is yes", ans.answer())
        self.assertEqual(question_key, ans.question_key)

        ans = submission_ans.make_or_update(sub_key, question_key, "No")
        self.assertEqual("No", ans.answer())
        self.assertEqual(question_key, ans.question_key)

    def test_answer_retrieval(self):
        c = self.create_conference()
        question_key = confquestion.mk_question(c.key, "Yes or no?").key

        sub_key = submissionrecord.make_submission(None, c.key, "track", "format")

        ans = submission_ans.mk_answer(sub_key, question_key, "The answer is yes")

        found_ans = submission_ans.retrieve_answer(sub_key, question_key)
        self.assertEqual("The answer is yes", found_ans.answer())
        self.assertEqual(question_key, found_ans.question_key)

        question_key2 = confquestion.mk_question(c.key, "To be or not to be").key
        found_ans = submission_ans.retrieve_answer(sub_key, question_key2)
        self.assertEquals(None, found_ans)

        found_ans = submission_ans.retrieve_answer_or_dummy(sub_key, question_key)
        self.assertEqual("The answer is yes", found_ans.answer())
        self.assertEqual(question_key, found_ans.question_key)

        found_ans = submission_ans.retrieve_answer_or_dummy(sub_key, question_key2)
        self.assertNotEquals(None, found_ans)
        self.assertEquals("", found_ans.answer())
        self.assertEquals(question_key2, found_ans.question_key)

    def test_retrieve_answer_map(self):
        c = self.create_conference()
        question1 = confquestion.mk_question(c.key, "Yes or no?")
        question2 = confquestion.mk_question(c.key, "To be or not to be")
        question3 = confquestion.mk_question(c.key, "Black or white")
        questions = [question1.key, question2.key, question3.key]

        answers = submission_ans.retrieve_answer_map(None, questions)
        self.assertEquals(answers, {question1.key: submission_ans.mk_dummy_answer(question1.key),
                                    question2.key: submission_ans.mk_dummy_answer(question2.key),
                                    question3.key: submission_ans.mk_dummy_answer(question3.key)})

        sub_key = submissionrecord.make_submission(None, c.key, "track", "format")
        ans1 = submission_ans.mk_answer(sub_key, question1.key, "The answer is yes")
        ans2 = submission_ans.mk_answer(sub_key, question2.key, "Hamlet")
        ans3 = submission_ans.mk_dummy_answer(question3.key)

        answers = submission_ans.retrieve_answer_map(sub_key, questions)

        self.assertEquals(3, len(answers))
        self.assertEquals(answers[question1.key], ans1)
        self.assertEquals(answers[question2.key], ans2)
        self.assertEquals(answers[question3.key], ans3)

        # Answers without a submission should still be dummies
        # Conference has None parent, therefore all answers have a None ancestor
        # When some answers are in the system they ma show up for a new (None) submission
        answers = submission_ans.retrieve_answer_map(None, questions)
        self.assertEquals(answers, {question1.key: submission_ans.mk_dummy_answer(question1.key),
                                    question2.key: submission_ans.mk_dummy_answer(question2.key),
                                    question3.key: submission_ans.mk_dummy_answer(question3.key)})

