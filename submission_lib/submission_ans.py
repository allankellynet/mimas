#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb


class AnswerClass(ndb.Model):
    question_key = ndb.KeyProperty()
    answer_text = ndb.StringProperty()

    def answer(self):
        return self.answer_text

class AnswerClassDummy(AnswerClass):
    def __init__(self, *args, **kwargs):
        super(AnswerClassDummy, self).__init__(*args, **kwargs)
        self.question_key = None
        self.answer_text = ""


def mk_answer(subs_key, question_key, answer):
    ans = AnswerClass(parent=subs_key)
    ans.question_key = question_key
    ans.question_key = question_key
    ans.answer_text = answer
    ans.put()
    return ans

def make_or_update(subs_key, question_key, answer_text):
    answers = AnswerClass.query(ancestor=subs_key).filter(AnswerClass.question_key == question_key).fetch(1)
    if len(answers) < 1:
        return mk_answer(subs_key, question_key, answer_text)
    else:
        answer = answers[0]
        answer.question_key = question_key
        answer.answer_text = answer_text
        answer.put()
        return answer

def retrieve_answer(subs_key, question_key):
    answers = AnswerClass.query(ancestor=subs_key).filter(AnswerClass.question_key == question_key).fetch(1)
    if len(answers) < 1:
        return None
    else:
        return answers[0]

def mk_dummy_answer(question_key):
    ans = AnswerClassDummy()
    ans.question_key = question_key
    return ans

def retrieve_answer_or_dummy(subs_key, question_key):
    answers = AnswerClass.query(ancestor=subs_key).filter(AnswerClass.question_key == question_key).fetch(1)
    if len(answers) < 1:
        return mk_dummy_answer(question_key)
    else:
        return answers[0]

def retrieve_answer_map(subs_key, question_key_list):
    r = {}
    for q in question_key_list:
        r[q] = mk_dummy_answer(q)

    if subs_key is None:
        return r

    answers = AnswerClass.query(ancestor=subs_key).fetch()
    for answer in answers:
        if answer.question_key in question_key_list:
            r[answer.question_key] = answer

    return r

