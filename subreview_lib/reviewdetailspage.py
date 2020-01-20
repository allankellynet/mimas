#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import basehandler
import roundreviews
from conference_lib import confquestion
from speaker_lib import cospeaker
from submission_lib import submission_ans, votecomment


class ReviewDetailsPage(basehandler.BaseHandler):
    def render_page(self, readonly, enable_controls, confidential):
        submission_key = ndb.Key(urlsafe=self.request.get("k"))
        submission = submission_key.get()
        conference = submission_key.parent().get()
        speakers = [submission.talk.parent().get()]
        cospeakers = cospeaker.get_cospeakers(submission_key)
        for cospeak in cospeakers:
            speakers = speakers + [cospeak.profile()]

        conf_questions = confquestion.retrieve_questions(conference.key)
        conf_answers = submission_ans.retrieve_answer_map(submission_key, map(lambda q: q.key, conf_questions))

        template_values = {
            "submission": submission,
            "talk_details": submission.talk.get(),
            "speakers": speakers,
            "readonly": readonly,
            "reviews": roundreviews.retrieve_all_reviews(submission),
            "submissionrecord_track": conference.track_options()[submission.track],
            "submissionrecord_duration": conference.duration_options()[submission.duration],
            "submissionrecord_format": conference.delivery_format_options()[submission.delivery_format],
            "submissionrecord_expenses": conference.expenses_options()[submission.expense_expectations],
            "cospeakers": cospeakers,
            "cospeakers_count": len(cospeakers),
            "enable_controls" : enable_controls,
            "emaillocked": "disabled",
            "show_confidential": confidential,
            "retrieve_vote_comment": votecomment.retrieve_vote_comment,
            "retrieve_comment_text": votecomment.retrieve_comment_text,
            "conf_questions": conf_questions,
            "conf_answers": conf_answers,
        }

        self.write_page('subreview_lib/reviewdetailspage.html', template_values)


class ReviewDetailsPagePublic(ReviewDetailsPage):
    def get(self):
        if self.request.params.has_key("readonly"):
            enable_controls = False
        else:
            enable_controls = True

        self.render_page("readonly", enable_controls, True)

class ReviewDetailsPageFeedback(ReviewDetailsPage):
    def get(self):
        self.render_page("read_only", False, False)