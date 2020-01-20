#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Library imports
from google.appengine.ext import ndb

# Application imports
from submission_lib import submissionrecord, voterecord


def reviewer_votes(reviewer, votes_cast):
    votes = []
    for v in votes_cast:
        if v.reviewer == reviewer:
            votes.append(v)

    return votes

def extract_reviewers(votes_cast):
    reviewers = {}
    if votes_cast != None:
        for v in votes_cast:
            reviewers[v.reviewer]="x"
    return reviewers.keys()

def find_duplicate_votes(conf_key, round):
    duplicates = {}
    for sub in submissionrecord.retrieve_conference_submissions(conf_key):
        votes = voterecord.find_existing_votes(sub.key, round)
        for reviewer in extract_reviewers(votes):
            votes_cast = reviewer_votes(reviewer, votes)
            if len(votes_cast) > 1:
                duplicates[reviewer] = votes_cast

    return duplicates

def remove_duplicates(dups_list):
    for voter in dups_list:
        while (len(dups_list[voter])>1):
            dups_list[voter][0].key.delete()
            del dups_list[voter][0]

class DuplicateVoteReport(ndb.Model):
    duplicates = ndb.PickleProperty()
    vote_round = ndb.IntegerProperty()

    def has_duplicates(self):
        return len(self.duplicates)>0

def retrieve_duplicate_report(conf_key):
    report = DuplicateVoteReport.query(ancestor=conf_key).fetch(1)
    if len(report)==0:
        return None

    return report[0]

def delete_vote_reports(conf_key):
    report = retrieve_duplicate_report(conf_key)
    while report != None:
        report.key.delete()
        report = retrieve_duplicate_report(conf_key)

def generate_duplicate_vote_report(conf_key, round):
    delete_vote_reports(conf_key)
    vote_report = DuplicateVoteReport(parent=conf_key)
    vote_report.duplicates = find_duplicate_votes(conf_key, round)
    vote_report.vote_round = round
    vote_report.put()
    return vote_report
