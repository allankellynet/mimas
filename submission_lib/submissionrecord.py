#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import numpy
from google.appengine.ext import ndb

import submissionnotifynames
import voterecord
from conference_lib import confdb


class SubmissionRecord(ndb.Model):
    # conference object is parent so no need to record that her
    talk = ndb.KeyProperty()
    track_name = ndb.StringProperty()
    decision_by_round = ndb.PickleProperty()
    duration = ndb.StringProperty()
    delivery_format_text = ndb.StringProperty()
    last_review_round = ndb.IntegerProperty()
    withdrawn = ndb.BooleanProperty()
    speaker_communication = ndb.StringProperty()
    expense_expectations = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    gdpr_agreed_flag = ndb.BooleanProperty()

    def __init__(self, *args, **kwargs):
        super(SubmissionRecord, self).__init__(*args, **kwargs)
        self.track_name = ""
        self.decision_by_round = { 1: "No decision" }
        self.last_review_round = 1
        self.withdrawn = False
        self.speaker_communication = submissionnotifynames.SUBMISSION_NEW
        self.gdpr_agreed_flag = False

    def title(self):
        return self.talk.get().title

    # Deprecated: should move over to first, last name convention
    def submitter(self):
        return self.talk.parent().get().name

    def first_name(self):
        return self.talk.parent().get().first_name()

    def last_name(self):
        return self.talk.parent().get().later_names()

    def email(self):
        return self.talk.parent().get().email

    @property
    def track(self):
        return self.track_name

    @property
    def delivery_format(self):
        return self.delivery_format_text

    def review_decision(self, review_round):
        return self.decision_by_round[review_round]

    def set_review_decision(self, review_round, text):
        self.decision_by_round[review_round] = text

    def final_decision(self):
        return self.decision_by_round[self.last_review_round]

    def reviewer_voting_score(self, name, round):
        vote = voterecord.find_existing_vote_by_reviewer(self.key, name, round)
        if vote is None:
            return 0

        return vote.score

    def reviewer_voting_msg(self, name, round):
        vote = voterecord.find_existing_vote_by_reviewer(self.key, name, round)
        if vote is None:
            return "No vote"

        return vote.score

    def reviewer_voting_comment(self, name, round):
        vote = voterecord.find_existing_vote_by_reviewer(self.key, name, round)
        if vote is None:
            return ""

        return vote.comment

    def withdraw(self):
        self.withdrawn = True
        self.decision_by_round[self.last_review_round] = "Withdrawn"
        self.put()

    def is_withdrawn(self):
        return self.withdrawn

    class ScoresRecord():
        def __init__(self):
            self.total_score = 0
            self.mean_score = 0
            self.median_score = 0
            self.votes = 0
            self.scores = []

    # would be good to optimise this
    # or do some score caching

    def get_scores(self, review_round):
        voterecords = voterecord.VoteRecord.query(ancestor=self.key).filter(
            voterecord.VoteRecord.round == review_round).fetch()
        if (len(voterecords) == 0):
            return SubmissionRecord.ScoresRecord()

        rec = SubmissionRecord.ScoresRecord()
        rec.total_score = numpy.sum(list(v.score for v in voterecords))
        rec.mean_score = round(numpy.mean(list(v.score for v in voterecords)),2)
        rec.median_score = round(numpy.median(list(v.score for v in voterecords)),2)
        rec.votes = len(voterecords)
        rec.scores = map(lambda vr: vr.score, voterecords)
        return rec

    @property
    def communication(self):
        return self.speaker_communication

    def mark_comms(self, notify_state):
        self.speaker_communication = notify_state
        self.put()

    def acknowledge_receipt(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_ACKNOWLEDGED
        self.put()

    def mark_decline_pending(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_DECLINE_PENDING
        self.put()

    def mark_declined(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_DECLINED
        self.put()

    def mark_acccept_pending(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_ACCEPT_PENDING
        self.put()

    def mark_acccept(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_ACCEPTED
        self.put()

    def mark_accept_acknowledged(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_ACCEPT_ACKNOWLEDGED
        self.put()

    def mark_accept_declined(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_ACCEPT_DECLINDED
        self.put()

    def mark_accept_problem(self):
        self.speaker_communication = submissionnotifynames.SUBMISSION_ACCEPT_PROBLEM
        self.put()

    @property
    def expenses(self):
        return self.expense_expectations

    def set_expenses_expectation(self, exp):
        self.expense_expectations = exp

    @property
    def gdpr_agreed(self):
        return self.gdpr_agreed_flag

    def set_gdpr_agreement(self, agree):
        self.gdpr_agreed_flag = agree
        self.put()

def make_submission(talk_key, conf_key, track, format):
    sr = SubmissionRecord(parent=conf_key)
    sr.talk = talk_key
    sr.track_name = track
    sr.delivery_format_text = format
    return sr.put()

def make_submission_plus(talk_key, conf_key, track, format, duration, expenses):
    sr = SubmissionRecord(parent=conf_key)
    sr.talk = talk_key
    sr.track_name = track
    sr.delivery_format_text = format
    sr.duration = duration
    sr.expense_expectations = expenses
    return sr.put()

def retrieve_conference_submissions_keys(conf_key):
    return SubmissionRecord.query(ancestor=conf_key).filter(SubmissionRecord.withdrawn == False).fetch(keys_only=True)

def retrieve_conference_submissions(conf_key):
    return SubmissionRecord.query(ancestor=conf_key).filter(SubmissionRecord.withdrawn == False).fetch()

def retrieve_conference_submissions_orderby_track(conf_key):
    return SubmissionRecord.query(ancestor=conf_key).order(SubmissionRecord.track_name).fetch()


def retrieve_conference_submissions_by_track_and_round(conf_key, track, review_round):
    return SubmissionRecord.query(
        ancestor=conf_key).filter(ndb.AND(SubmissionRecord.track_name == track,
                                          SubmissionRecord.last_review_round >= review_round,
                                          SubmissionRecord.withdrawn == False)).fetch()

def retrieve_conference_submissions_by_track_round_and_decision(conf_key, track, review_round, decision):
    subs = retrieve_conference_submissions_by_track_and_round(conf_key, track, review_round)
    r = []
    for s in subs:
        if s.review_decision(review_round) == decision:
            r.append(s)

    return r

def delete_submission_by_talk(talk_key):
    records = SubmissionRecord.query().filter(SubmissionRecord.talk == talk_key)
    for r in records:
        r.key.delete()

def retrieve_submissions_records(conf_key):
    return SubmissionRecord.query(ancestor=conf_key).fetch()

def get_subs_for_talk(talk_key):
    return SubmissionRecord.query().filter(SubmissionRecord.talk == talk_key).fetch()

def get_submission_key(conf_key, talk_key):
    r = SubmissionRecord.query(ancestor=conf_key).\
        filter(SubmissionRecord.talk == talk_key).\
        fetch()
    if len(r)==0:
        return None
    else:
        return r[0].key

def get_confences_talk_submitted_to(talk_key):
    submissions = SubmissionRecord.query().filter(SubmissionRecord.talk == talk_key).fetch()
    fn = lambda submission: submission.key.parent().get().name
    return map(fn, submissions)

def submissions_conference_map(talk_key):
    r = {}
    submissions = SubmissionRecord.query().filter(SubmissionRecord.talk == talk_key).fetch()
    for s in submissions:
        r[s.key.urlsafe()]= s.key.parent().get().name
    return r

def get_decision_summary(conf_key, track, review_round):
    # projection query would be faster here but... obvious doesn't work
    summary = {"No decision": 0}
    for r in retrieve_conference_submissions_by_track_and_round(conf_key, track, review_round):
        round_decision = r.review_decision(review_round)
        if summary.has_key(round_decision):
            summary[r.review_decision(review_round)] = summary[r.review_decision(review_round)] + 1
        elif round_decision == "":
            summary["No decision"] = summary["No decision"] + 1
        else:
            summary[r.review_decision(review_round)] = 1

    return summary

def sort_low_to_high(submission_list, user, review_round):
    return sorted(submission_list, key=lambda sub: sub.reviewer_voting_score(user, review_round))

def sort_submissions_by_total_low_to_high(submission_list, review_round):
    return sorted(submission_list, key=lambda sub: sub.get_scores(review_round).total_score)

def sort_submissions_by_total_high_to_low(submission_list, review_round):
    return sorted(submission_list, key=lambda sub: sub.get_scores(review_round).total_score, reverse=True)

def sort_submissions_by_mean_low_to_high(submission_list, review_round):
    return sorted(submission_list, key=lambda sub: sub.get_scores(review_round).mean_score)

def sort_submissions_by_mean_high_to_low(submission_list, review_round):
    return sorted(submission_list, key=lambda sub: sub.get_scores(review_round).mean_score, reverse=True)


def sort_submissions_by_median_low_to_high(submission_list, review_round):
    return sorted(submission_list, key=lambda sub: sub.get_scores(review_round).median_score)

def get_submission_by_talk_and_conf(talk_key, conf_name):
    conf_key = confdb.get_conf_by_name(conf_name).key
    # duplicate eentries should be preventsed
    subs = SubmissionRecord.query(ancestor=conf_key).filter(SubmissionRecord.talk == talk_key).fetch()
    if (len(subs) == 0):
        return None
    else:
        return subs[0].key

