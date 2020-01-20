#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from conference_lib import confquestion
from conference_lib import conference

class TestConferenceQuestions(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def mk_conference(self):
        c = conference.Conference()
        c.name = "Allans conference_lib"
        c.shortname = "Allans"
        c.dates = "1-2 January 2017"
        c.creator_id = "Harry1"

        c.put()
        return c


    def test_conf_question_basics(self):
        c = self.mk_conference()
        q = confquestion.mk_question(c.key, "How are you?")
        self.assertEquals("How are you?", q.question_text())
        self.assertTrue(q.is_free_text())
        self.assertEquals(set(), q.answer_options())

        q.add_option("Good")
        self.assertFalse(q.is_free_text())
        self.assertSetEqual({"Good"}, q.answer_options())

        q.add_option("Bad")
        self.assertFalse(q.is_free_text())
        self.assertSetEqual({"Good", "Bad"}, q.answer_options())

    def test_retrieve_questions(self):
        c = self.mk_conference()
        questions = confquestion.retrieve_questions(c.key)
        self.assertEquals(0, len(questions))

        q = confquestion.mk_question(c.key, "How are you?")
        questions = confquestion.retrieve_questions(c.key)
        self.assertEquals(1, len(questions))
        self.assertEquals("How are you?", questions[0].question_text())

        q2 = confquestion.mk_question(c.key , "What day is it?")
        questions = confquestion.retrieve_questions(c.key)
        self.assertEquals(2, len(questions))

    def test_delete_question_answers(self):
        c = self.mk_conference()
        q = confquestion.mk_question(c.key, "How are you?")
        q.add_option("Good")
        q.add_option("Bad")

        self.assertEquals(2, len(q.answer_options()))
        q.delete_answers()
        self.assertEquals(0, len(q.answer_options()))


    def test_delete_question_and_answers(self):
        c = self.mk_conference()
        q = confquestion.mk_question(c.key, "How are you?")
        q.add_option("Good")
        q.add_option("Bad")

        self.assertEquals(1, len(confquestion.retrieve_questions(c.key)))
        confquestion.delete_question_and_answers(q)
        self.assertEquals(0, len(confquestion.retrieve_questions(c.key)))

    # see submission_lib/submission_ans.py for actual answers
