#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system includes

# library includes

from submission_lib import submissionrecord
# local includes
from submission_lib.submissionrecord import SubmissionRecord


def can_close_conference(conf_key, review_round):
    subs = SubmissionRecord.query(ancestor=conf_key).filter(SubmissionRecord.last_review_round==review_round)
    for s in subs:
        if (s.review_decision(review_round) == "No decision" \
            or s.review_decision(review_round) == ""):
            return False

    return True

def close_round1_and_open_round2(conf):
    for sub in submissionrecord.retrieve_conference_submissions(conf.key):
        if sub.last_review_round < 2:
            if (sub.review_decision(1) == "Round2"):
                sub.last_review_round = 2
                sub.set_review_decision(2, "No decision")
                sub.put()

    conf.start_round2_reviews()
    conf.put()


