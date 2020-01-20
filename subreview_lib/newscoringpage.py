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
from subreview_lib import confreviewconfig


class NewScoringReviewPage(basehandler.BaseHandler):
    def get(self):
        submission_key = ndb.Key(urlsafe=self.request.get("sub"))
        submission = submission_key.get()

        conference = submission_key.parent().get()

        user = self.get_crrt_user().email()
        existing_vote = voterecord.find_existing_vote_by_reviewer(submission_key, user, round=1)

        if existing_vote is not None:
            vote_safe_key = existing_vote.key.urlsafe()
            existing_score = existing_vote.score
            existing_comment = existing_vote.comment
            private_comment = votecomment.retrieve_comment_text(existing_vote.key)
        else:
            vote_safe_key = ""
            existing_score = 1
            existing_comment = ""
            private_comment = ""

        conf_questions = confquestion.retrieve_questions(conference.key)
        conf_answers = self.conference_answers(conf_questions, submission_key)

        newscoringconfig = confreviewconfig.get_conference_review_factory(conference.key). \
            get_round_config(int(self.request.get("round")))

        speakers = {}
        if newscoringconfig.is_speaker_named():
            show_name = True
            speakers = self.retrieve_speakers(submission)
        else:
            show_name = False

        template_values = {
            "speakers": speakers,
            "readonly": "readonly",
            "talk_details": submission.talk.get(),
            "submissionrecord_track": conference.track_options()[submission.track],
            "submissionrecord_duration": conference.duration_options()[submission.duration],
            "submissionrecord_format": conference.delivery_format_options()[submission.delivery_format],
            "submissionrecord_expenses": conference.expenses_options()[submission.expense_expectations],
            "submissionrecord_key": submission_key.urlsafe(),
            "voterecord": vote_safe_key,
            "existing_score": existing_score,
            "existing_comment": existing_comment,
            "private_comment": private_comment,
            "emaillocked": "disabled",
            "submission": submission,
            "conf_questions": conf_questions,
            "conf_answers": conf_answers,
            "newscoringconfig" : newscoringconfig,
            "show_name": show_name,
        }

        self.write_page('subreview_lib/newscoringpage.html', template_values)

    def retrieve_speakers(self, submission):
        speakers = [submission.talk.parent().get()]
        cospeakers = cospeaker.get_cospeakers(submission.key)

        for cospeak in cospeakers:
            speakers = speakers + [cospeak.profile()]
        return speakers

    def conference_answers(self, conf_questions, submission_key):
        return submission_ans.retrieve_answer_map(submission_key, map(lambda q: q.key, conf_questions))

    def store_private_comment(self, vote_key):
        if self.request.get("private_comment") != "":
            votecomment.update_comment(vote_key, "Private", self.request.get("private_comment"))

    def new_vote(self, review_round):
        vote = voterecord.cast_new_vote(
                            ndb.Key(urlsafe=self.request.get("submissionrecord_key")),
                            self.get_crrt_user().email(),
                            int(self.request.get("vote")),
                            self.request.get("review_comment"),
                            round=review_round)

        self.store_private_comment(vote.key)
        return vote

    def update_existing_vote(self, review_round):
        votekey = ndb.Key(urlsafe=self.request.get("voterecord"))
        vote = votekey.get()
        vote.cast_vote(self.get_crrt_user().email(),
                       int(self.request.get("vote")),
                       self.request.get("review_comment"),
                       round=review_round)
        self.store_private_comment(vote.key)
        return vote

    def post(self):
        review_round = int(self.request.get("round"))
        if self.request.get("voterecord") == "":
            vote = self.new_vote(review_round)
        else:
            vote = self.update_existing_vote(review_round)

        track = vote.key.parent().get().track
        self.redirect("/scoringreview?track=" + track + "&round="+str(review_round))
