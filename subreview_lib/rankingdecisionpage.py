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


class RankingDecisionPage(basehandler.BaseHandler):
    def sort_submissions(self, submissions, review_round):
        if self.request.params.has_key("median"):
            return submissionrecord.sort_submissions_by_median_low_to_high(submissions, review_round)
        else:
            return submissionrecord.sort_submissions_by_mean_low_to_high(submissions, review_round)

    def get(self):
        if not (self.session.has_key("crrt_conference")):
            logging.debug("Conference key session variable missing")
            return

        crrt_conf = ndb.Key(urlsafe=self.session["crrt_conference"]).get()

        review_round = int(self.request.get("round"))
        crrt_track = self.select_track(crrt_conf.track_options())
        submissions = self.sort_submissions(
            submissionrecord.retrieve_conference_submissions_by_track_and_round(
                                    crrt_conf.key,
                                    crrt_track,
                                    review_round),
                        review_round)

        template_values = {
            'crrt_conf': crrt_conf,
            "track_objects": crrt_conf.mapped_track_obects(),
            "track_slots": crrt_conf.mapped_track_obects()[crrt_track].slots,
            "crrt_track": crrt_track,
            "submissions": submissions,
            "submissions_len": len(submissions),
            "decisions": submissionrecord.get_decision_summary(crrt_conf.key, crrt_track, review_round),
            "decision_maker": crrt_conf.user_rights().has_decision_right_for_round(
                                                            self.get_crrt_user().email(), review_round),
            "review_round": review_round,
        }

        self.write_page("subreview_lib/rankingdecisionpage.html", template_values)

    def select_track(self, tracks):
        if self.request.params.has_key("track"):
            crrt_track = self.request.get("track")
        else:
            crrt_track = tracks.keys()[0]
        return crrt_track

    def submit_decisions(self, review_round):
        if not (self.session.has_key("crrt_conference")):
            logging.debug("Conference key session variable missing")
            return

        roundreviews.submit_decisions(
            ndb.Key(urlsafe=self.session["crrt_conference"]),
            self.request.get("tracklist"),
            review_round,
            self.request)

    def post(self):
        review_round = int(self.request.get("review_round"))
        if self.request.get("SubmitDecision"):
            self.submit_decisions(review_round)

        self.redirect("/rankingdecision?track=" + self.request.get("tracklist") +"&round=" + str(review_round))
