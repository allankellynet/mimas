#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
from submission_lib import submissionrecord, voterecord


def submit_decisions(conf_key, track, review_round, decisions_map):
    subs = submissionrecord.retrieve_conference_submissions_by_track_and_round(
        conf_key,
        track,
        review_round)
    for s in subs:
        safekey = s.key.urlsafe()
        value = decisions_map.get(safekey)
        s.set_review_decision(review_round, value)
        s.put()


def retrieve_all_reviews(submission):
    reviews = []
    for r in range(1, submission.last_review_round+1):
        round_reviews = voterecord.find_existing_votes(submission.key, r)
        if not (round_reviews is None):
            reviews = reviews + round_reviews

    return reviews


def mass_track_change(conf_key, track, review_round,
                      crrt_decision, new_decision):
    subs = submissionrecord.retrieve_conference_submissions_by_track_and_round(
            conf_key,
            track,
            review_round)
    for s in subs:
        if (s.review_decision(review_round) == crrt_decision):
            s.set_review_decision(review_round, new_decision)
            s.put()
