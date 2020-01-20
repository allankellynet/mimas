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
import roundreviews
import basehandler
from submission_lib import submissionrecord


class ClassicReviewDecisionPage(basehandler.BaseHandler):

    def make_page(self, crrt_conf):
        review_round = int(self.request.get("round"))
        tracks = crrt_conf.mapped_track_obects()
        crrt_track = self.request.get("track", default_value=tracks.keys()[0])

        submissions = self.sorted_submissions(crrt_conf, crrt_track, review_round)

        template_values = {
            'crrt_conf': crrt_conf,
            "track_objects": tracks,
            "crrt_track": crrt_track,
            "submissions": submissions,
            "submissions_len": len(submissions),
            "decisions": submissionrecord.get_decision_summary(crrt_conf.key, crrt_track, review_round),
            "decision_maker": crrt_conf.user_rights().has_decision_right_for_round(
                                                            self.get_crrt_user().email(), review_round),
            "review_round": review_round,
            "track_slots": crrt_conf.mapped_track_obects()[crrt_track].slots,
        }

        self.write_page('subreview_lib/classicreviewdecisionpage.html', template_values)

    def sorted_submissions(self, crrt_conf, crrt_track, review_round):
        submissions = submissionrecord.retrieve_conference_submissions_by_track_and_round(
                            crrt_conf.key, crrt_track, review_round)

        if self.request.params.has_key("mean"):
            sorted = submissionrecord.sort_submissions_by_mean_high_to_low(submissions, review_round)
        else:
            sorted = submissionrecord.sort_submissions_by_total_high_to_low(submissions, review_round)
        return sorted

    def get(self):
        if not (self.session.has_key("crrt_conference")):
            logging.debug("Conference key session variable missing")
            return

        crrt_conf = ndb.Key(urlsafe=self.session["crrt_conference"]).get()

        self.make_page(crrt_conf)

    def submit_decisions(self, review_round):
        if not (self.session.has_key("crrt_conference")):
            logging.debug("Conference key session variable missing")
            return

        roundreviews.submit_decisions(
            ndb.Key(urlsafe=self.session["crrt_conference"]),
            self.request.get("tracklist"),
            review_round,
            self.request)

    def decline_no_decisions(self, review_round):
        self.submit_decisions(review_round)
        roundreviews.mass_track_change(
                        ndb.Key(urlsafe=self.session["crrt_conference"]),
                        self.request.get("tracklist"),
                        review_round,
                        "No decision",
                        "Decline")

    def post(self):
        review_round = int(self.request.get("review_round"))
        if self.request.get("SubmitDecision"):
            self.submit_decisions(review_round)
        if self.request.get("DeclineNoDecisions"):
            self.decline_no_decisions(review_round)

        self.redirect("/classic_review_decisions?track=" +
                      self.request.get("tracklist") +
                      "&round=" + str(review_round))
