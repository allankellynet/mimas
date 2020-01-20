#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports

# app imports
import reports.commentreport
from submission_lib import voterecord, votecomment


class VoteSummary:
    def __init__(self, score, comment):
        self.score = score
        self.shared_comment = comment
        self.private_comment = ""

def retrieve_vote_summary(reviewer, round):
    r = {}
    votes = reports.commentreport.find_reviewer_votes_for_round(reviewer, round)
    for v in votes:
        summary = VoteSummary(v.score, v.comment)
        summary.private_comment = votecomment.retrieve_comment_text(v.key)
        r[v.key.parent().urlsafe()] = summary

    return r

class VoteSummaryList():
    def __init__(self, reviewer, round):
        self.summary_map = retrieve_vote_summary(reviewer, round)

    def get_vote_score(self, key):
        if self.summary_map.has_key(key):
            return self.summary_map[key].score

        return 0

    def get_shared_comment(self, key):
        if self.summary_map.has_key(key):
            return self.summary_map[key].shared_comment

        return ""

    def get_private_comment(self, key):
        if self.summary_map.has_key(key):
            return self.summary_map[key].private_comment


        return ""
