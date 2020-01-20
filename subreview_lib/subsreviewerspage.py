#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import basehandler
from subreview_lib import reviewer
from submission_lib import voterecord

def find_vote_sugar(subs_key, reviewer, rr):
    v = voterecord.find_existing_vote_by_reviewer(subs_key, reviewer, rr)
    if v is None:
        return "No vote"

    return v.score

class SubmissionReviewersPage(basehandler.BaseHandler):
    def get(self):
        rr = int(self.request.get("round"))
        sub_key = ndb.Key(urlsafe=self.request.get("sub"))
        reviewers = reviewer.get_reviewers(sub_key, review_round=rr)

        self.write_page('subreview_lib/subsreviewerspage.html',
                        {"submission": sub_key.get(),
                         "review_round": rr,
                         "reviewers": map(lambda r:r.get(),reviewers),
                         "find_vote_sugar": find_vote_sugar,
                         })

    def add_reviewer(self):
        sub = ndb.Key(urlsafe=self.request.get("sub_key")).get()
        who = reviewer.get_new_or_existing_reviewer(sub.key.parent(), self.request.get("new_reviewer_email"))
        who.assign_submission(sub.track, [sub.key], int(self.request.get("review_round")))

    def delete_reviewers(self):
        sub = ndb.Key(urlsafe=self.request.get("sub_key")).get()
        rr = int(self.request.get("review_round"))

        for rev in self.request.get_all("delete_checkbox"):
            who = ndb.Key(urlsafe=rev).get()
            who.remove_assignment(sub.track, rr, sub.key)

    def post(self):
        if self.request.get("submit_new_reviewer"):
            self.add_reviewer()

        if self.request.get("delete_reviewers"):
            self.delete_reviewers()

        self.redirect("/subreviewers?round="+self.request.get("review_round")+
                      "&sub="+self.request.get("sub_key"))
