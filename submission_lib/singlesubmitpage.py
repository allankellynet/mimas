#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from mailmsg import postmail
from scaffold import sorrypage
import basehandler
from speaker_lib import speaker_fragment, speaker
from submission_lib import subm_entry_fragment, submission_queries, submissionrecord, submission_ans
from talk_lib import talk, talk_fragment
from conference_lib import confquestion

class SingleSubmitPage(basehandler.BaseHandler):
    def overide(self):
        if self.request.params.has_key("overide"):
            if self.request.get("overide")=="Yes":
                return True

        return False

    def is_conference_closed(self, crrt_conf):
        if crrt_conf.state() != "Open" and not(self.overide()):
            sorrypage.redirect_sorry(self, "ConfNotOpen")
            return True
        else:
            return False

    def submissions_exceeded(self):
        return submission_queries.count_submissions(self.crrt_conf.key, self.submitter.key) >= self.crrt_conf.max_submissions()

    def show_single_submit_page(self):
        if self.submissions_exceeded():
            sorrypage.redirect_sorry(self, "SubsLimitReached")
            return

        conf_questions = confquestion.retrieve_questions(self.crrt_conf.key)
        conf_answers = submission_ans.retrieve_answer_map(None, map(lambda q: q.key, conf_questions))

        template_values = {
            "crrt_conf": self.crrt_conf,
            # Speaker fields
            'new_speaker': True,
            'speaker': self.submitter,
            "emaillocked": "readonly",
            'speakerKey': "",
            'readonly': "",
            # Talk fields
            "talk_details": talk.Talk(parent=None),
            "is_new": True,
            "talk_key": None,
            # Conference submission fields
            "selected_track": self.crrt_conf.track_options().keys()[0],
            "selected_duration": self.crrt_conf.duration_options().keys()[0],
            "selected_format": self.crrt_conf.delivery_format_options().keys()[0],
            "selected_expenses": self.crrt_conf.expenses_options().keys()[0],
            "conf_questions": conf_questions,
            "conf_answers": conf_answers,
        }

        self.write_page('submission_lib/singlesubmitpage.html', template_values)

    def submission_from_login(self):
        self.crrt_conf = ndb.Key(urlsafe=self.session["singlesubmit"]).get()
        if self.is_conference_closed(self.crrt_conf):
            return False

        user = self.get_crrt_user()
        self.submitter = speaker.retrieve_or_make(user.email())
        self.submitter.name = user.name()
        self.submitter.put()
        return True

    def get(self):
        if self.session.has_key("singlesubmit"):
            if (self.submission_from_login()):
                self.show_single_submit_page()
                return
        else:
            sorrypage.redirect_sorry(self, "RequiresEmail")


    def process_speaker(self, messages):
        # Now users must login user account will exist in the system
        # Therefore can remove checks about eixsting or new user
        # Existing details will be shown on get
        # So already read and store them here

        email = self.request.get("email")
        spk = speaker.retrieve_or_make(email)
        speaker_fragment.read_speaker_dir(self, spk)
        speaker_fragment.read_and_store_fields(self, spk)
        return spk

    def process_talk(self, messages, spk):
        new_talk = talk.Talk(parent=spk.key)
        talk_fragment.readAndSave(self, new_talk)
        return new_talk

    def process_submission(self, messages, conf_key, talk_key, email):
        # TODO 1 - Common code to share with submitpage.py
        # TODO 2 - Set acknowledge submission after send not before
        #           and check for exception to mark as failed acknowledge
        submission = submissionrecord.SubmissionRecord(parent=conf_key)
        submission.talk = talk_key
        subm_entry_fragment.read_and_store(self, submission)
        submission.acknowledge_receipt()
        postmail.ack_submission(submission, conf_key)
        messages.append("A confirmation email has been sent to " + email)
        return submission

    def post(self):
        conf = ndb.Key(urlsafe=self.request.get("conf_key")).get()
        messages = []
        spk = self.process_speaker(messages)

        sub_key="NoKey"
        if (submission_queries.count_submissions(conf.key, spk.key) >= conf.max_submissions()):
            messages.append("Conference submission limit has been reached for this speaker.")
            messages.append("This submission has NOT been accepted.")
        else:
            tlk = self.process_talk(messages, spk)
            if submission_queries.is_submitted(conf.key, spk.email, tlk.talk_title):
                messages.append("IMPORTANT: This submission will be discarded because you have already submitted a talk with this title.")
                messages.append("If you wish to modify the existing talk please log into the main system.")
            else:
                submission = self.process_submission(messages, conf.key, tlk.key, spk.email)
                sub_key=submission.key.urlsafe()
                messages.append("If you wish to modify any of the above please log into the main system.")
                messages.append("And thanks again!")

        template_values = {
            "crrt_conf": conf,
            "messages": messages,
            "sub_key": sub_key,
        }
        self.write_page('submission_lib/singlesubmitpage2.html', template_values)
