#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

from google.appengine.ext import ndb

# Local imports
from scaffold import sorrypage, volunteerreviewer, firebase
import basehandler


# Local imports

class VolunteerReviewerPage(basehandler.BaseHandler):
    def get(self):
        self.crrt_conf = None

        if self.session.has_key("conference_volunteer"):
            self.crrt_conf = ndb.Key(urlsafe=self.session["conference_volunteer"]).get()
        else:
            if self.request.params.has_key("conf"):
                self.crrt_conf = ndb.Key(urlsafe=self.request.get("conf")).get()

        if self.crrt_conf == None:
            sorrypage.redirect_sorry(self, "VolunteerFailure")
            return

        user = self.get_crrt_user()

        template_values = {
            "crrt_conf": self.crrt_conf,
            "email": user.email(),
            "name": user.name(),
            "firebase_config_variable": firebase.config_js_params(),
        }

        self.write_page('scaffold/volunteerreviewerpage.html', template_values)

    def post(self):
        conf = ndb.Key(urlsafe=self.request.get("crrt_conf_key")).get()

        tracks = []
        for track in conf.track_options():
            if self.request.get(track):
                tracks.append(track)

        volunteerreviewer.mk_volunteer_reviewer(conf.key,
                                                self.request.get("name"),
                                                self.request.get("emailaddress"),
                                                tracks)

        self.write_page('scaffold/volunteerthankyou.html', {"name": self.request.get("name")})
