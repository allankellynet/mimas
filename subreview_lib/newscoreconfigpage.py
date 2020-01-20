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
from scaffold import attentionpage
import basehandler
from subreview_lib import confreviewconfig, newscoringtask

class NewScoreConfigPage(basehandler.BaseHandler):
    def get(self):
        conference_key = self.get_crrt_conference_key()
        conference = conference_key.get()
        review_round = int(self.request.get("round", "1"))
        review_config = confreviewconfig.get_conference_review_factory(conference_key).get_round_config(review_round)

        reviewers = conference.user_rights().list_reviewers(review_round)

        template_values = {
            'logoutlink': users.create_logout_url("/"),
            "crrt_conference": conference,
            "review_round": review_round,
            "review_config": review_config,
            "conf_tracks": conference.track_options(),
            "tracks": review_config.track_limits(),
            "reviewers": reviewers,
        }

        self.write_page('subreview_lib/newscoreconfigpage.html', template_values)

    def post(self):
        newscoring_config = ndb.Key(urlsafe=self.request.get("round_key")).get()

        if self.request.get("updateparams"):
            self.update_config_params(newscoring_config)
        if self.request.get("assignreviewers"):
            self.review_assignments(newscoring_config)

    def update_config_params(self, newscoring_config):
        newscoring_config.set_speaker_named(self.request.get("name_speaker") == "on")
        newscoring_config.set_private_comments(self.request.get("private_comments") == "on")
        newscoring_config.set_min_vote(int(self.request.get("min_vote")))
        newscoring_config.set_max_vote(int(self.request.get("max_vote")))
        self.read_track_limits(newscoring_config)
        self.redirect("/newscoreconfigpage?round=" + self.request.get("round", "1"))

    def read_track_limits(self, newscoring_config):
        tracks = self.get_crrt_conference_key().get().track_options()
        for track in tracks.keys():
            limit = int(self.request.get(track, default_value="20"))
            newscoring_config.set_track_limit(track, limit)

    def review_assignments(self, newscoring_config):
        conference = self.get_crrt_conference_key().get()
        review_round = int(self.request.get("round", "99"))

        for track in conference.track_options():
            for reviewer_email in conference.user_rights().list_reviewers(review_round):
                synthetic_name = track + "&" + reviewer_email

                if self.request.get(synthetic_name):
                    newscoringtask.enqueue_review_assignments(
                        self.get_crrt_conference_key(),
                        reviewer_email,
                        review_round,
                        track,
                        newscoring_config.track_limits()[track])

        attentionpage.redirect_extendedmessage(self, "BulkReviewAssignments", "/createconf")
