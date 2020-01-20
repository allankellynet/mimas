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

class AssignmentDetailPage(basehandler.BaseHandler):
    def get(self):
        conf = self.get_crrt_conference_key().get()
        review_email = self.request.get("reviewer")
        who = reviewer.get_reviewer(conf.key, review_email)

        review_round = int(self.request.get("review_round", 99))
        self.write_page('subreview_lib/assignmentdetailpage.html',
                        {"reviewer": review_email,
                        "review_round" : review_round,
                         "subs_assignments": who.retrieve_review_assignments_for_round(review_round),
                         "tracks": conf.track_options()
                         })

    def remove_assignment(self, who, safekey):
        sub = ndb.Key(urlsafe=safekey).get()
        who.remove_assignment(sub.track, review_round=int(self.request.get("review_round", "1")), target=sub.key)

    def remove_selected(self):
        who = reviewer.get_reviewer(self.get_crrt_conference_key(), self.request.get("reviewer"))

        for s in self.request.get_all("select_for_removal"):
            self.remove_assignment(who, s)

    def post(self):
        if self.request.get("Remove"):
            self.remove_selected()

        self.redirect("/assignementdetailspage?review_round=" + self.request.get("review_round") +
                      "&reviewer=" + self.request.get("reviewer"))


