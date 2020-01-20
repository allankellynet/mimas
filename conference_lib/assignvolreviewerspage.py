#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from scaffold import volunteerreviewer, userrightsnames, sorrypage, sysinfo
import basehandler


class AssignVolunteerReviewersPage(basehandler.BaseHandler):
    def get(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        if not(conference.user_rights().has_permission(
                self.get_crrt_user().email(),
                userrightsnames.APPOINT_REVIEWERS)):
            sorrypage.redirect_sorry(self, "AssignTracksReq")
            return

        volunteers = volunteerreviewer.retrieve_all_volunteers(conf_key)

        template_values = {
            "crrt_conf": conference,
            "conf_key": conf_key,
            "tracks": conference.track_options(),
            "volunteers": volunteers,
            "volunteer_count": len(volunteers),
            "home_url": sysinfo.home_url(),
        }

        self.write_page('conference_lib/assignvolreviewerspage.html', template_values)

    def assign_tracks(self, rights, volunteer):
        for track in volunteer.tracks():
            if self.request.get(volunteer.key.urlsafe()+"."+track) == "on":
                rights.add_track_reviewer(volunteer.email(), track)

    def assign_permissions(self, rights, volunteer, tag_name, permission):
        if self.request.get(volunteer.key.urlsafe() + tag_name):
            volunteer.accept()
            rights.add_permission(volunteer.email(), permission)

    def assign_reviewer(self, rights, volunteer):
        if self.request.get(volunteer.key.urlsafe()+".reject"):
            volunteer.reject()
            return

        self.assign_permissions(rights, volunteer, ".round1", userrightsnames.ROUND1_REVIEWER)
        self.assign_permissions(rights, volunteer, ".round2", userrightsnames.ROUND2_REVIEWER)
        self.assign_tracks(rights, volunteer)

    def assign_all(self, conf_key):
        conf = conf_key.get()
        for volunteer in volunteerreviewer.retrieve_all_volunteers(conf_key):
            self.assign_reviewer(conf_key.get().user_rights(), volunteer)

    def post(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_safe_key"))
        self.assign_all(conf_key)
        self.redirect("/assignvolunteers?conf=" + conf_key.urlsafe())
