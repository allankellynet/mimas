#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports

class VoteRecord(ndb.Model):
    # database parent is a Submission record
    reviewer = ndb.StringProperty()
    score = ndb.IntegerProperty()
    comment = ndb.StringProperty()
    round = ndb.IntegerProperty()

    def cast_vote(self, reviewer, score, comment, round):
        self.reviewer = reviewer
        self.score = score
        self.comment = comment
        self.round = round
        self.put()


def find_existing_vote_by_reviewer(subs_key, reviewer, round):
    r = VoteRecord.query(ancestor=subs_key).filter(VoteRecord.reviewer == reviewer,
                                                   VoteRecord.round == round).fetch()
    if len(r) == 0:
        return None

    return r[0]


def cast_new_vote(submission_key, reviewer, score, comment, round):
    vote = VoteRecord(parent=submission_key)
    vote.cast_vote(reviewer, score, comment, round)
    return vote


def find_existing_votes(subs_key, round):
    r = VoteRecord.query(ancestor=subs_key).filter(VoteRecord.round == round).fetch()
    if len(r) == 0:
        return None

    return r

def count_reviewer_votes(conf_key, reviewer, review_round):
    return VoteRecord.query(ancestor=conf_key).filter(ndb.AND(
                        VoteRecord.reviewer == reviewer,
                        VoteRecord.round == review_round)).count()

def count_votes_for_submission(sub_key, review_round):
    return VoteRecord.query(ancestor=sub_key).filter(VoteRecord.round == review_round).count()

def count_votes_for_submissions(sub_key_list, review_round):
    return dict(map(lambda sk: (sk,count_votes_for_submission(sk, review_round)), sub_key_list))

