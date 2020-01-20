#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports

# Local imports
from scaffold import sorrypage, userrightsnames
import basehandler


class ReviewAdminPage(basehandler.BaseHandler):
    def get(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()
        rights = conference.user_rights()

        if not(rights.has_permission(self.get_crrt_user().email(), userrightsnames.APPOINT_REVIEWERS)):
            sorrypage.redirect_sorry(self, "AssignTracksReq")
            return

        if self.request.get("reviewer"):
            reviewer = self.request.get("reviewer")
            reviewer_tracks = conference.user_rights().track_assignments(reviewer)
        else:
            reviewer = ""
            reviewer_tracks = []

        template_values = {
            "crrt_conf": conf_key.get(),
            "conf_key": conf_key,
            "tracks": conference.track_options(),
            "rights": rights,
            "reviewer": reviewer,
            "reviewer_tracks": reviewer_tracks,
        }

        self.write_page('conference_lib/assigntrackspage.html', template_values)

    def add_reviewer_by_track(self, ur, name, conference):
         for track in conference.track_options():
            if self.request.get(track):
                ur.add_track_reviewer(name, track)

    def add_reviewer(self, conf_key):
        # would be better to disable button unless these fields are populated
        # shold also check for duplicate names
        if len(self.request.get("new_reviewer_email")) == 0:
            return

        user_name = self.request.get("new_reviewer_email")

        conference = conf_key.get()
        ur = conference.user_rights()
        ur.remove_all_review_rights(user_name)
        self.add_reviewer_by_track(ur, user_name, conference)

    def remove_reviewer(self, conf_key):
        email = self.request.get("reviewerToDelete")
        ur = conf_key.get().user_rights()
        ur.remove_all_review_rights(email)

    def post(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_safe_key"))
        if self.request.get("SubmitReviewer"):
            self.add_reviewer(conf_key)
        if self.request.get("remove_reviewer"):
            self.remove_reviewer(conf_key)

        self.redirect("/assigntracks?conf=" + conf_key.urlsafe())
