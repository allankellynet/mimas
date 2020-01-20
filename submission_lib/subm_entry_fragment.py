#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# Functions to support multiple uses of the speaker_fragment.html

# system imports

# library imports

# local imports
import submission_ans
from conference_lib import confquestion
from submission_lib import submissionrecord
from mailmsg import postmail

agreement_map = { "Agree": True,
                  "Disagree": False }

def read_and_store_conference_questions(handler, subs_key):
    crrt_conference = subs_key.parent()
    conf_questions = confquestion.retrieve_questions(crrt_conference)
    for q in conf_questions:
        text_answer = handler.request.get(q.shortname())
        submission_ans.make_or_update(subs_key, q.key, text_answer)

def read_and_store(handler, submission):
    submission.track_name = handler.request.get("track")
    submission.duration = handler.request.get("duration")
    submission.delivery_format_text = handler.request.get("delivery_format")
    submission.set_expenses_expectation(handler.request.get("expenses"))
    submission.set_gdpr_agreement(agreement_map[handler.request.get("gdpr_policy", default_value="Disagree")])
    subs_key = submission.put()
    read_and_store_conference_questions(handler, subs_key)

def make_submission(handler, conf_key, talk_key):
    submission = submissionrecord.SubmissionRecord(parent=conf_key)
    submission.talk = talk_key
    read_and_store(handler, submission)
    submission.acknowledge_receipt()
    postmail.ack_submission(submission, conf_key)
    return submission
