#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import logging
from google.appengine.api import users
from google.appengine.ext import ndb

# app imports
from conference import confoptions

# Does not import conference_lib
# Conference class imports this class

class ConferenceQuestionAnswer(confoptions.ConferenceOption):
    pass


class ConferenceQuestion(confoptions.ConferenceOption):
    def question_text(self):
        return self.full_text()

    def is_free_text(self):
        opt = ConferenceQuestionAnswer.query(ancestor=self.key).fetch(1)
        if len(opt) == 0:
            return True
        else:
            return False

    def add_option(self, option_text):
        # create a conference_lib option with this as the parent
        opt = confoptions.make_conference_option(ConferenceQuestionAnswer, self.key, option_text)
        return opt

    def answer_options(self):
        opts = set()
        for opt in ConferenceQuestionAnswer.query(ancestor=self.key).fetch():
            opts.add(opt.full_text())

        return opts

    def delete_answers(self):
        for answer in ConferenceQuestionAnswer.query(ancestor=self.key).fetch():
            answer.key.delete()

def mk_question(conf_key, question):
    q = confoptions.make_conference_option(ConferenceQuestion, conf_key, question)
    return q

def retrieve_questions(conf_key):
    return ConferenceQuestion.query(ancestor=conf_key).fetch()

def delete_question_and_answers(question):
    question.delete_answers()
    question.key.delete()
