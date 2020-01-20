#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import webapp2
import logging
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

# Local imports
from subreview_lib import reviewer


class MoreReviewsTask(webapp2.RequestHandler):
    def post(self):
        reviewer = ndb.Key(urlsafe=self.request.get("reviewer_key")).get()
        reviewer.assign_more_reviews(self.request.get("track"),
                                     int(self.request.get("review_count")),
                                     int(self.request.get("review_round")))

# Assignments should not be run in parallel
# Therefore queue.yaml limits default queue to one at a time
# If multiple run together the reviewers will get the same assignments
def enqueue_review_assignments(conf_key,
                               reviewer_email,
                               review_round,
                               track,
                               quantity):
    named_reviewer = reviewer.get_new_or_existing_reviewer(conf_key, reviewer_email)
    taskqueue.add(
        url='/more_reviews',
        params={'reviewer_key': named_reviewer.key.urlsafe(),
                'track'       : track,
                'review_count': quantity,
                'review_round': review_round
            })
