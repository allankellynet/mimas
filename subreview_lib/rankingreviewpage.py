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
import basehandler
import votesummary
from submission_lib import submissionrecord, voterecord, votecomment


class RankingReviewPage(basehandler.BaseHandler):
    def get(self):
        if not (self.session.has_key("crrt_conference")):
            logging.debug("Conference key session variable missing")
            self.response.write('Error: Current conference cannot be determned')
            return
        else:
            crrt_conf = ndb.Key(urlsafe=self.session["crrt_conference"]).get()

        review_round = int(self.request.get("round"))
        user_email = self.get_crrt_user().email()
        review_tracks = crrt_conf.user_rights().tracks_to_review(user_email)

        crrt_track = self.get_track(review_tracks)

        records = submissionrecord.sort_low_to_high(
            submissionrecord.retrieve_conference_submissions_by_track_and_round(
                crrt_conf.key,
                crrt_track,
                review_round),
            user_email,
            review_round)

        template_values = {
            "crrt_conf": crrt_conf,
            "conference_submissions": records,
            "count_submissions": len(records),
            "selected_conf": crrt_conf.name,
            "useremail": self.get_crrt_user().email(),
            "review_tracks": review_tracks,
            "track_objects": crrt_conf.mapped_track_obects(),
            "track_slots": crrt_conf.mapped_track_obects()[crrt_track].slots,
            "selected_track": crrt_track,
            "vote_summary": votesummary.VoteSummaryList(user_email, review_round),
            "review_round": review_round,
        }

        self.write_page('subreview_lib/rankingreviewpage.html', template_values)

    def get_track(self, review_tracks):
        if self.request.params.has_key("track"):
            crrt_track = self.request.get("track")
        else:
            if len(review_tracks) > 0:
                # no key so default to first track in list
                crrt_track = review_tracks[0]
            else:
                # no tracks or no review rights
                crrt_track = "None"  # review_tracks[0]
        return crrt_track

    def new_vote(self, submission_key, ranking, comment, review_round):
        return voterecord.cast_new_vote(
            submission_key,
            self.get_crrt_user().email(),
            ranking,
            comment,
            round=review_round)

    def update_existing_vote(self, existing_vote, ranking, comment, review_round):
        existing_vote.cast_vote( self.get_crrt_user().email(),
                                 ranking,
                                 comment,
                                 round=review_round)

    def vote(self, submission_key, ranking, comment, review_round):
        existing_vote = voterecord.find_existing_vote_by_reviewer(
            submission_key,
            self.get_crrt_user().email(),
            round=review_round)

        if existing_vote is None:
            existing_vote = self.new_vote(submission_key, ranking, comment, review_round)
        else:
            self.update_existing_vote(existing_vote, ranking, comment, review_round)

        return existing_vote

    def store_private_comment(self, vote_key, field_name):
        if self.request.get(field_name) != "":
            votecomment.update_comment(vote_key, "Private", self.request.get(field_name))


    def submit_votes(self, review_round):
        crrt_conf_key = ndb.Key(urlsafe=self.session["crrt_conference"])
        crrt_track = self.request.get("track")
        records = submissionrecord.retrieve_conference_submissions_by_track_and_round(
            crrt_conf_key,
            crrt_track,
            review_round)

        for r in records:
            safe_key = r.key.urlsafe()
            ranking = int(self.request.get(safe_key))
            comment = self.request.get("comment_" + safe_key)
            v = self.vote(r.key, ranking, comment, review_round)
            self.store_private_comment(v.key, "private_comment_" + safe_key)


    def post(self):
        review_round = int(self.request.get("review_round"))
        if self.request.get("VoteExit"):
            self.submit_votes(review_round)
            self.redirect("/reviewers")
        if self.request.get("VoteCont"):
            self.submit_votes(review_round)
            self.redirect("/rankingreview?track=" + self.request.get("track") + "&round=" + str(review_round))
