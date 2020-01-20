#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler
from submission_lib import submissionrecord, voterecord
from subreview_lib import reviewer

class SubmissionAssignmentsPage(basehandler.BaseHandler):
    def get(self):
        conference = self.get_crrt_conference_key().get()
        review_round = int(self.request.get("round", "1"))

        submissions = submissionrecord.retrieve_conference_submissions(conference.key)
        submission_keys = map(lambda s: s.key, submissions)

        template_values = {
            "submissions": submissions,
            "assignment_count": dict(reviewer.count_submission_reviewers(submission_keys, review_round)),
            "tracks": conference.track_options(),
            "vote_count": voterecord.count_votes_for_submissions(submission_keys, review_round),
            "crrt_conf": conference,
            "review_round": review_round,
        }

        self.write_page('subreview_lib/subsassignmentpage.html', template_values)

