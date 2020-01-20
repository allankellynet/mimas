#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler
from subreview_lib import reviewer
from submission_lib import voterecord

def count_assignments(conf_key, name, review_round):
    r = reviewer.get_reviewer(conf_key, name)
    if r is None:
        return 0
    else:
        return r.count_assignments(review_round)

def count_votes_and_assignments(conf_key, reviewers, review_round):
    r = {}
    for reviewer in reviewers:
        r.update( { reviewer: (count_assignments(conf_key, reviewer, review_round),
                               voterecord.count_reviewer_votes(conf_key, reviewer, review_round))
                    })

    return r

def reviewer_complete_description(conf_key, email, rev_round):
    person = reviewer.get_reviewer(conf_key, email)
    if person is None:
        return ""

    if person.is_complete(rev_round):
        return "Complete"

    return ""

class VotingRecordsPage(basehandler.BaseHandler):
    def get(self):
        conference = self.get_crrt_conference_key().get()
        review_round = int(self.request.get("round", 1))

        template_values = {
            "crrt_conf": conference,
            "review_round": int(self.request.get("round")),
            "reviewers": count_votes_and_assignments(conference.key,
                conference.user_rights().list_reviewers(review_round),
                                                     review_round),
            "reviewer_complete_description": reviewer_complete_description,
        }

        self.write_page('subreview_lib/votingrecordspage.html', template_values)

