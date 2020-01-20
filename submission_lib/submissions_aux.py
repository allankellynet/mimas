#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import logging
from google.appengine.ext import ndb


# app imports
import submissionrecord
from submission_lib.submissionrecord import SubmissionRecord


def expenses_summary(submissions):
    categories = {}
    for s in submissions:
        if categories.has_key(s.expense_expectations):
            categories[s.expense_expectations]+=1
        else:
            categories[s.expense_expectations] = 1

    return categories

def change_expenses(sub_key, criteria, new_value):
    submission = sub_key.get()
    if submission.expenses == criteria:
        submission.set_expenses_expectation(new_value)
        submission.put()

def change_all_expenses(conf_key, criteria, new_value):
    for sub_key in submissionrecord.retrieve_conference_submissions_keys(conf_key):
        change_expenses(sub_key, criteria, new_value)

def retrieve_submissions_by_expenses(conf_key, expenses_type_filter):
    query = submissionrecord.SubmissionRecord.query(ancestor=conf_key)
    if (expenses_type_filter != ""):
        query = query.filter(submissionrecord.SubmissionRecord.expense_expectations == expenses_type_filter)

    return query.fetch()

def filter_by_final_decision(decision, subs):
    r = []
    for s in subs:
        if s.final_decision() == decision:
            r.append(s)
    return r

def retrieve_by_final_decision(conf_key, decision):
    subs = submissionrecord.retrieve_conference_submissions(conf_key)
    return filter_by_final_decision(decision, subs)

def retrieve_by_final_decision_track_ordered(conf_key, decision):
    subs = submissionrecord.retrieve_conference_submissions_orderby_track(conf_key)
    return filter_by_final_decision(decision, subs)


def retrieve_conference_submissions_by_track(conf_key, track):
    return SubmissionRecord.query(ancestor=conf_key).filter(ndb.AND(
        SubmissionRecord.track_name == track,
        SubmissionRecord.withdrawn == False)).fetch()


def retrieve_conference_submission_keys_by_track(conf_key, track):
    return SubmissionRecord.query(ancestor=conf_key).filter(ndb.AND(
        SubmissionRecord.track_name == track,
        SubmissionRecord.withdrawn == False)).fetch(keys_only=True)

def retrieve_conference_submission_keys_by_track_and_round(conf_key, track, review_round):
    return SubmissionRecord.query(ancestor=conf_key).filter(ndb.AND(
        SubmissionRecord.track_name == track,
        SubmissionRecord.last_review_round == review_round,
        SubmissionRecord.withdrawn == False)).fetch(keys_only=True)
