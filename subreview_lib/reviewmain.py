#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.api import users
from google.appengine.ext import ndb

# Local imports
from conference_lib import confdb
from scaffold import sorrypage
import basehandler
import confreviewconfig, reviewer

class ReviewMainPage(basehandler.BaseHandler):
    def get(self):
        username = self.get_crrt_user().email()
        all_conf = confdb.test_retrieve_conferences_not_finished()

        conference_key = self.get_crrt_conference_key()
        if conference_key is None:
            if len(all_conf) >= 1:
                conference_key = all_conf[0].key
                self.session["crrt_conference"] = conference_key.urlsafe()
            else:
                sorrypage.redirect_sorry(self, "NoConfToReview")
                return

        crrt_conference = conference_key.get()
        rev = reviewer.get_reviewer(crrt_conference.key, username)
        if rev is not None:
            rev_key = rev.key.urlsafe()
        else:
            rev_key = None

        template_values = {
            'name': username,
            'logoutlink': users.create_logout_url("/"),
            'conference_count': len(all_conf),
            "conferences": all_conf,
            "crrt_conference": crrt_conference,
            "review_config": confreviewconfig.get_conference_review_factory(crrt_conference.key),
            "compeleted_reviewing": (lambda r: rev.is_complete(r)),
            "reviewerKey": rev_key,
        }

        self.write_page('subreview_lib/reviewmain.html', template_values)

    def post(self):
        if "None" != self.request.get("reviewerKey"):
            rev = ndb.Key(urlsafe=self.request.get("reviewerKey")).get()
            rev.set_complete("on" == self.request.get("CompleteReviewing"),
                             int(self.request.get("reviewRound")))

        conf_key = self.request.get("conference")
        self.session["crrt_conference"] = conf_key
        self.redirect("/reviewers")