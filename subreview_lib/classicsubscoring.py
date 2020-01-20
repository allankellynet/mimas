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
from conference_lib import confquestion
from speaker_lib import cospeaker
from submission_lib import submission_ans, voterecord, votecomment


class ClassicSubScoringPage(basehandler.BaseHandler):
    def get(self):
        if not (self.request.params.has_key("sub")):
            self.response.write("Sorry, you shouldn't have been able to get here like that.")
            return

        submission_key = ndb.Key(urlsafe=self.request.get("sub"))
        submission = submission_key.get()

        conference = submission_key.parent().get()
        cospeakers = cospeaker.get_cospeakers(submission_key)

        speakers = [submission.talk.parent().get()]
        for cospeak in cospeakers:
            speakers = speakers + [cospeak.profile()]

        review_round = int(self.request.get("round"))
        user = self.get_crrt_user().email()
        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_key, user, round=review_round)

        if existing_vote is not None:
            vote_safe_key = existing_vote.key.urlsafe()
            existing_score = existing_vote.score
            existing_comment = existing_vote.comment
            private_comment = votecomment.retrieve_comment_text(existing_vote.key)
        else:
            vote_safe_key = ""
            existing_score = 0
            existing_comment = ""
            private_comment = ""

        conf_questions = confquestion.retrieve_questions(conference.key)
        conf_answers = self.conference_answers(conf_questions, submission_key)

        template_values = {
            "speakers": speakers,
            "readonly": "readonly",
            "talk_details": submission.talk.get(),
            "submissionrecord_track": conference.track_options()[submission.track],
            "submissionrecord_duration": conference.duration_options()[submission.duration],
            "submissionrecord_format": conference.delivery_format_options()[submission.delivery_format],
            "submissionrecord_expenses": conference.expenses_options()[submission.expense_expectations],
            "submissionrecord_key": submission_key.urlsafe(),
            "submission": submission,
            "cospeakers": cospeakers,
            "cospeakers_count": len(cospeakers),
            "voterecord": vote_safe_key,
            "existing_score": existing_score,
            "existing_comment": existing_comment,
            "private_comment": private_comment,
            "emaillocked": "disabled",
            "submission": submission,
            "conf_questions": conf_questions,
            "conf_answers": conf_answers,
            "review_round": review_round,
        }

        self.write_page('subreview_lib/classicsubscoring.html', template_values)

    def conference_answers(self, conf_questions, submission_key):
        return submission_ans.retrieve_answer_map(submission_key, map(lambda q: q.key, conf_questions))

    def store_private_comment(self, vote_key):
        if self.request.get("private_comment") != "":
            votecomment.update_comment(vote_key, "Private", self.request.get("private_comment"))

    def new_vote(self):
        vote = voterecord.cast_new_vote(
                            ndb.Key(urlsafe=self.request.get("submissionrecord_key")),
                            self.get_crrt_user().email(),
                            int(self.request.get("vote")),
                            self.request.get("review_comment"),
                            round=int(self.request.get("review_round")))

        self.store_private_comment(vote.key)
        return vote

    def update_existing_vote(self):
        votekey = ndb.Key(urlsafe=self.request.get("voterecord"))
        vote = votekey.get()
        vote.cast_vote(self.get_crrt_user().email(),
                       int(self.request.get("vote")),
                       self.request.get("review_comment"),
                       round=int(self.request.get("review_round")))
        self.store_private_comment(vote.key)
        return vote

    def post(self):
        if self.request.get("voterecord") == "":
            vote = self.new_vote()
        else:
            vote = self.update_existing_vote()

        track = vote.key.parent().get().track
        self.redirect("/classicreview?round=" +
                      self.request.get("review_round") +
                      "&track=" + track)
