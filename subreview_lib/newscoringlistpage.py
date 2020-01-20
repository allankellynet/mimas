#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
from scaffold import sorrypage, attentionpage
import basehandler
from subreview_lib import reviewer, newscoringtask, confreviewconfig


class NewScoringReviewListPage(basehandler.BaseHandler):
    def get(self):
        crrt_conf = self.get_crrt_conference_key().get()

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

        named_reviewer = reviewer.get_reviewer(crrt_conf.key, self.get_crrt_user().email())
        if named_reviewer is None:
            named_reviewer = reviewer.make_new_reviewer(crrt_conf.key, self.get_crrt_user().email())

        review_round = int(self.request.get("round"))
        records = named_reviewer.retrieve_review_assignments(crrt_track, review_round)

        newscoringconfig = confreviewconfig.get_conference_review_factory(crrt_conf.key). \
            get_round_config(int(self.request.get("round")))
        if newscoringconfig.is_speaker_named():
            show_name = True
        else:
            show_name = False

        template_values = {
            "conference_submissions": map(lambda s: s.get(), records),
            "count_submissions": len(records),
            "selected_conf": crrt_conf.name,
            "useremail": self.get_crrt_user().email(),
            "review_tracks": review_tracks,
            "track_dictionary": crrt_conf.track_options(),
            "selected_track": crrt_track,
            "durations": crrt_conf.duration_options(),
            "review_round": review_round,
            "show_name": show_name
        }

        self.write_page('subreview_lib/newscoringlistpage.html', template_values)

    def request_more_reviews(self, review_round, track):
        newscoringtask.enqueue_review_assignments(
            self.get_crrt_conference_key(),
            self.get_crrt_user().email(),
            review_round,
            track,
            10)

        attentionpage.redirect_extendedmessage(self, "RequestMoreReviewers", "/reviewers")


    def post(self):
        review_round = int(self.request.get("round"))
        crrt_track = self.request.get("crrt_track")

        if self.request.get("request_more_reviews"):
            self.request_more_reviews(review_round, crrt_track)

