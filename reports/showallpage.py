#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.api import users

# Local imports
import submission_lib.submissions_aux
from submission_lib import submissionrecord
from scaffold import sorrypage
import basehandler


class ShowAllPage(basehandler.BaseHandler):
    def get(self):
        conference_key = self.get_crrt_conference_key()
        crrt_conference = conference_key.get()

        tracks = crrt_conference.track_options()
        if len(tracks)==0:
            sorrypage.redirect_sorry(self, "IncompleteSetup")
            return

        subs_count = {}
        subs_count["total"] = 0
        submissions = {}
        for t in tracks:
            if self.request.params.has_key("f"):
                submissions[t], filter_description = self.retrieve_submissions(conference_key, t, self.request.get("f"))
            else:
                submissions[t] = []
                filter_description = "No filter selected"
            subs_count[t] = len(submissions[t])
            subs_count["total"] += len(submissions[t])

        template_values = {
            "crrt_conference": crrt_conference,
            "tracks" : tracks,
            "submissions" : submissions,
            'logoutlink': users.create_logout_url(self.request.uri),
            "subs_count": subs_count,
            "filter_description": filter_description,
        }

        self.write_page('reports/showallpage.html', template_values)

    def retrieve_submissions(self, conference_key, track, filter):
        if (filter=="round1"):
            return submissionrecord.retrieve_conference_submissions_by_track_and_round(
                    conference_key, track, 1), "Round 1 results"
        if (filter=="round2"):
            return submissionrecord.retrieve_conference_submissions_by_track_and_round(
                    conference_key, track, 2), "Round 2 results"
        if (filter=="finalaccept"):
            return submissionrecord.retrieve_conference_submissions_by_track_round_and_decision(
                conference_key, track, 2, "Accept"), "Final accepts only"
        if (filter=="all"):
            return submission_lib.submissions_aux.retrieve_conference_submissions_by_track(conference_key, track), "All submissions"
