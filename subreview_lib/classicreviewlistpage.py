#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import logging

from google.appengine.ext import ndb

# Local imports
from scaffold import sorrypage
import basehandler
from submission_lib import submissionrecord


class ClassicReviewListPage(basehandler.BaseHandler):
    def get(self):
        if not (self.session.has_key("crrt_conference")):
            logging.debug("Conference key session variable missing")
            sorrypage.redirect_sorry(self, "MissingParams")
            return

        crrt_conf = ndb.Key(urlsafe=self.session["crrt_conference"]).get()

        if not (self.request.params.has_key("round")):
            logging.debug("Round parameter variable missing")
            sorrypage.redirect_sorry(self, "MissingParams")
            return

        review_round = int(self.request.get("round"))

        rights = crrt_conf.user_rights()
        review_tracks = rights.tracks_to_review(self.get_crrt_user().email())

        if self.request.params.has_key("track"):
            crrt_track = self.request.get("track")
        else:
            if len(review_tracks) > 0:
                # no key so default to first track in list
                crrt_track = review_tracks[0]
            else:
                # no tracks or no review rights
                crrt_track = "None"  # review_tracks[0]
                sorrypage.redirect_sorry(self, "NoTracksAssigned")
                return

        records = submissionrecord.retrieve_conference_submissions_by_track_and_round(crrt_conf.key, crrt_track, review_round)

        template_values = {
            "conference_submissions": records,
            "count_submissions": len(records),
            "selected_conf": crrt_conf.name,
            "useremail": self.get_crrt_user().email(),
            "review_tracks": review_tracks,
            "track_objects": crrt_conf.mapped_track_obects(),
            "selected_track": crrt_track,
            "track_slots": crrt_conf.mapped_track_obects()[crrt_track].slots,
            "durations": crrt_conf.duration_options(),
            "review_round": review_round,
        }

        self.write_page('subreview_lib/classicreviewlistpage.html', template_values)
