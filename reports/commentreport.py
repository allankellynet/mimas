#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
from submission_lib import submissionrecord
from submission_lib.voterecord import VoteRecord


class CommentReport(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    comments = ndb.PickleProperty()

    def __init__(self, *args, **kwargs):
        super(CommentReport, self).__init__(*args, **kwargs)
        self.comments = {}

    @property
    def has_comments(self):
        return len(self.comments)>0

    def add(self, key, vote):
        if not self.comments.has_key(key):
            self.comments[key] = []

        self.comments[key].append(vote)


def delete_comment_reports(conf_key):
    for report in CommentReport.query(ancestor=conf_key).fetch():
        report.key.delete()


def make_comment_report(conf_key):
    delete_comment_reports(conf_key)
    report = get_commented_votes(conf_key)
    report.put()
    return report


def retrieve_commented_report(conf_key):
    report = CommentReport.query(ancestor=conf_key).fetch(1)
    if len(report)==0:
        return None
    else:
        return report[0]


def get_commented_votes(conf_key):
    report = CommentReport(parent=conf_key)
    for sub in submissionrecord.retrieve_conference_submissions(conf_key):
        for v in VoteRecord.query(ancestor=sub.key).fetch():
            if len(v.comment):
                report.add(sub.key, v.key)

    return report


def delete_vote_comments(vote_keys):
    for v in vote_keys:
        vote = v.get()
        vote.comment = ""
        vote.put()


def find_reviewer_votes_for_round(reviewer, round):
    # type: (object, object) -> object
    return VoteRecord.query(VoteRecord.reviewer == reviewer).filter(VoteRecord.round == round).fetch()