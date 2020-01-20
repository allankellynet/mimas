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
from scaffold import sorrypage
import basehandler
import confreviewconfig

class ReviewMainPage(basehandler.BaseHandler):
    def get(self):
        conference_key = None
        crrt_conference = None

        # Pick up current conference from session
        if self.session.has_key("crrt_conference"):
           conference_key = ndb.Key(urlsafe=self.session["crrt_conference"])
           crrt_conference = conference_key.get()
        else:
           sorrypage.redirect_sorry(self, "NoConfToReview")
           return

        template_values = {
            'logoutlink': users.create_logout_url("/"),
            "crrt_conference": crrt_conference,
            "conf_key": crrt_conference.key,
            "review_config": confreviewconfig.get_conference_review_factory(crrt_conference.key),
            "review_options": confreviewconfig.available_review_models(),
        }

        self.write_page('subreview_lib/reviewconfigpage.html', template_values)

    def set_review_choices(self):
        conf_key = self.get_crrt_conference_key()
        review_config = confreviewconfig.get_conference_review_factory(conf_key)
        review_config.set_round_by_name(1, self.request.get("round1reviews"))
        review_config.set_round_by_name(2, self.request.get("round2reviews"))
        review_config.put()

    def post(self):
        if self.request.get("reviewchoices"):
            self.set_review_choices()

        self.redirect("/reviewconfig")
