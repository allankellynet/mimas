#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports
import itertools

# Library imports
import logging
from google.appengine.ext import ndb

# Application imports
import submission_lib.submissions_aux
from submission_lib import submissionrecord

class ReviewAssignment(ndb.Model):
    track = ndb.StringProperty()
    round = ndb.IntegerProperty()
    assigned_subs = ndb.KeyProperty(repeated=True)

    def add_submisson_assignments(self, subs_list):
        self.assigned_subs.extend(subs_list)
        self.put()


def count_submission_assignments(conf_key, sub_key, review_round):
    entries = retrieve_review_assignments(conf_key, sub_key, review_round)
    return len(entries)


def retrieve_review_assignments(conf_key, sub_key, review_round):
    entries = ReviewAssignment.query(ancestor=conf_key) \
        .filter(ndb.AND(sub_key == ReviewAssignment.assigned_subs,
                        review_round == ReviewAssignment.round)) \
        .fetch(keys_only=True)
    return entries


def count_submission_reviewers(subs_list, review_round):
    r = []
    for s in subs_list:
        r.append([s, count_submission_assignments(s.parent(), s, review_round)])

    return r

def make_review_assignment(reviewer_key, track_name, review_round, assignments_list):
    assignment = ReviewAssignment(parent=reviewer_key)
    assignment.track = track_name
    assignment.round = review_round
    assignment.assigned_subs = assignments_list
    assignment.put()


class Reviewer(ndb.Model):
    email = ndb.StringProperty()
    reviews_complete = ndb.PickleProperty()

    def __init__(self, *args, **kwargs):
        super(Reviewer, self).__init__(*args, **kwargs)
        self.email = ""
        self.own_subs = None
        self.reviews_complete = {}

    def own_submissions(self):
        if self.own_subs is None:
            own_subs = self.find_own_subissions()

        # Conferences are closed to new submissions during review
        # So a new submission is unlikely to enter while we assign reviewers
        # Therefore cache own submissions

        return own_subs

    def find_own_subissions(self):
        sub_keys = submissionrecord.retrieve_conference_submissions_keys(self.key.parent())
        return list(filter(lambda sk: sk.get().talk.parent().get().email == self.email, sub_keys))

    def retrieve_review_assignments(self, track_name, review_round):
        assignments = ReviewAssignment.query(ancestor=self.key).filter(
            ndb.AND(ReviewAssignment.track == track_name,
                    ReviewAssignment.round == review_round)).fetch()
        if assignments == []:
            return []
        else:
            return assignments[0].assigned_subs

    def retrieve_review_assignments_for_round(self, review_round):
        assignments = ReviewAssignment.query(ancestor=self.key).filter(
                    ReviewAssignment.round == review_round).fetch()
        return list(itertools.chain(*(map(lambda i: i.assigned_subs, assignments))))

    def count_assignments(self, review_round):
        assignment_records = ReviewAssignment.query(ancestor=self.key) \
                            .filter(ReviewAssignment.round == review_round).fetch()
        if len(assignment_records) == 0:
            return 0

        assignment_counts = map(lambda a: len(a.assigned_subs), assignment_records)
        return reduce(lambda i, j: i+j, assignment_counts)

    # only one set of assignments at a time should be run
    # if multiple run together they will get the same results
    def assign_submission(self, track_name, submission_keys, review_round):
        assignments = ReviewAssignment.query(ancestor=self.key).filter(
            ndb.AND(ReviewAssignment.track == track_name,
                    ReviewAssignment.round == review_round)).fetch()  # type: object
        if assignments == []:
            make_review_assignment(self.key, track_name, review_round, submission_keys)
        else:
            assignments[0].add_submisson_assignments(submission_keys)


    def remove_assignment(self, track_name, review_round, target):
        assignments = ReviewAssignment.query(ancestor=self.key).filter(
            ndb.AND(ReviewAssignment.track == track_name,
                    ReviewAssignment.round == review_round)).fetch()
        if assignments == []:
            return

        while assignments[0].assigned_subs.count(target) > 0:
            assignments[0].assigned_subs.remove(target)

        assignments[0].put()

    def assign_more_reviews(self, track, how_many, review_round):
        subs = submission_lib.submissions_aux.retrieve_conference_submission_keys_by_track_and_round(
            self.key.parent(),
            track,
            review_round)

        review_candidates = list(set(subs) -
                                 set(self.retrieve_review_assignments(track, review_round)) -
                                 set(self.find_own_subissions())
                                 )

        subs_reviewers_count = count_submission_reviewers(review_candidates, review_round)
        sorted_by_number_of_reviewers = sorted(subs_reviewers_count, key=lambda k: k[1])
        new_assignments = sorted_by_number_of_reviewers[0:how_many]
        self.assign_submission(track, map(lambda s:s[0], new_assignments), review_round)

    def is_complete(self, review_round):
        if self.reviews_complete.has_key(review_round):
            return self.reviews_complete[review_round]
        else:
            return False

    def set_complete(self, flag, review_round):
        self.reviews_complete[review_round] = flag
        self.put()

def make_new_reviewer(conf_key, email):
    r = Reviewer(parent=conf_key)
    r.email = email
    r.put()
    return r

def get_reviewer(conf_key, email):
    reviewers = Reviewer.query(ancestor=conf_key).filter(Reviewer.email == email).fetch()
    if len(reviewers) == 0:
        return None

    return reviewers[0]

def get_new_or_existing_reviewer(conf_key, email):
    r = get_reviewer(conf_key, email)
    if r:
        return r
    else:
        return make_new_reviewer(conf_key, email)

def get_reviewers(sub_key, review_round):
    return map(lambda ass:ass.parent(), retrieve_review_assignments(sub_key.parent(), sub_key, review_round))
