#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

__author__ = 'allan'

# System imports
import datetime

# Google imports
import logging
from google.appengine.ext import ndb

# Local imports
import basehandler
from conference_lib import confdb, confquestion
import submissionrecord
from subreview_lib import roundreviews
from speaker_lib import cospeaker
import subm_entry_fragment
import submission_ans
import submission_queries

class SubmitPage(basehandler.BaseHandler):
    def get_existing_values(self):
        sub_key = ndb.Key(urlsafe=self.request.get("sub"))
        sub = sub_key.get()
        reviews = roundreviews.retrieve_all_reviews(sub)
        cospeak = cospeaker.get_cospeakers(sub_key)

        readonly = ""
        disabled = ""
        change_authority = False
        is_submitter = True
        crrt_conf = sub_key.parent().get()
        logging.info(self.get_crrt_user().email() + "----" + sub.talk.parent().get().email)
        if self.get_crrt_user().email() != sub.talk.parent().get().email:
            # not crrent users submission
            is_submitter = False
            if not crrt_conf.user_rights().has_decision_rights(self.get_crrt_user().email()):
                # and currt user does not have decision rights
                readonly = "readonly"
                disabled = "disabled"
            else:
                change_authority = True

        conf_questions = confquestion.retrieve_questions(crrt_conf.key)
        conf_answers = submission_ans.retrieve_answer_map(sub_key, map(lambda q: q.key, conf_questions))

        return {
                "talk_key" : sub.talk,
                "talk" : sub.talk.get(),
                "submitter": sub.talk.parent().get().name + " (" + sub.talk.parent().get().email + ")",
                "sub_key" : sub_key,
                "sub_key_safe" : sub_key.urlsafe(),
       			"available_conferences" : None,
                "crrt_conf" : crrt_conf,
                "selected_track" : sub.track,
                "selected_duration" : sub.duration,
                "selected_format" : sub.delivery_format,
                "selected_expenses" : sub.expenses,
                "reviews": reviews,
                "review_count": len(reviews),
                "withdrawn": sub.is_withdrawn(),
                "agree_privacy": sub.gdpr_agreed,
                "privacy_agreement_lock": "disabled",
                "cospeakers": cospeak,
                "cospeakers_count": len(cospeak),
                "submissions_count": submission_queries.count_submissions(sub_key.parent(), sub.talk.parent()),
                "readonly": readonly,
                "disabled": disabled,
                "change_authority": change_authority,
                "is_submitter": is_submitter,
                "conf_questions": conf_questions,
                "conf_answers": conf_answers,
                "created": sub.created,
        }

    def get_values_from_talk(self, conferences):
        talk_key = ndb.Key(urlsafe=self.request.get("talk"))

        if self.request.params.has_key("conf"):
            crrt_conference = ndb.Key(urlsafe=self.request.get("conf")).get()
        else:
            crrt_conference = conferences[0]

        sub_key = None
        conf_questions = confquestion.retrieve_questions(crrt_conference.key)
        conf_answers = submission_ans.retrieve_answer_map(sub_key, map(lambda q: q.key, conf_questions))

        return {
            "talk_key": talk_key,
            "talk": talk_key.get(),
            "submitter": self.get_crrt_user().email(),
            "sub_key": sub_key,
            "sub_key_safe": "Nil",
            "available_conferences": conferences,
            "crrt_conf": crrt_conference,
            "selected_track": crrt_conference.track_options().keys()[0],
            "selected_duration": crrt_conference.duration_options().keys()[0],
            "selected_format": crrt_conference.delivery_format_options().keys()[0],
            "selected_expenses": crrt_conference.expenses_options().keys()[0],
            "withdrawn": False,
            "agree_privacy": False,
            "privacy_agreement_lock": "", # once agreed to it cannot be resinded
            "cospeakers": [],
            "cospeakers_count": 0,
            "submissions_count": submission_queries.count_submissions(crrt_conference.key, talk_key.parent()),
            "change_authority": False,
            "is_submitter": True,
            "conf_questions": conf_questions,
            "conf_answers": conf_answers,
            "created": datetime.datetime.now(),
        }

    def display_page(self, values, next_page):
        template_values = {
            "username": self.get_crrt_user().email(),
            "next_page": next_page,
        }

        template_values.update(values)

        self.write_page('submission_lib/submitpage.html', template_values)

    def get(self):
        if self.request.params.has_key("reviewer"):
            next_page = "showallpage"
        else:
            next_page = ""

        if self.request.params.has_key("sub"):
            self.display_page(self.get_existing_values(), next_page)
        else:
            conferences = confdb.retrieve_all_conferences_by_state("Open")
            if (len(conferences) < 1):
                self.redirect("/sorry_page?reason=NoneOpen")
            else:
                self.display_page(self.get_values_from_talk(conferences), next_page)

    def decide_next_page(self, sub_key):
        # For reviewers
        if self.request.get("next_page")=="showallpage":
            return "/showallpage?conf=" + sub_key.parent().urlsafe()

        # For speakers
        return "/subthanks?conf="+sub_key.parent().urlsafe()+"&sub="+sub_key.urlsafe()

    def new_submit_talk(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        talk_key = ndb.Key(urlsafe=self.request.get("talk_key"))
        existing = submissionrecord.get_submission_key(conf_key, talk_key)
        if (existing is not None):
            self.redirect("/sorry_page?reason=AlreadySubmitted")
        else:
            submission = subm_entry_fragment.make_submission(self, conf_key, talk_key)
            self.redirect(self.decide_next_page(submission.key))

    def withdraw_submission(self):
        existing_sub_key = ndb.Key(urlsafe=self.request.get("sub_key"))
        existing_sub_key.get().withdraw()
        self.redirect("/list_submission")

    def update_submission(self):
        existing_sub_key = ndb.Key(urlsafe=self.request.get("sub_key"))
        subm_entry_fragment.read_and_store(self, existing_sub_key.get())
        self.redirect(self.decide_next_page(existing_sub_key))

    def authorised_update(self):
        self.update_submission()
        self.redirect("/showallpage")

    def post(self):
        if self.request.get("submittalk"):
            self.new_submit_talk()
        if self.request.get("withdrawtalk"):
            self.withdraw_submission()
        if self.request.get("updatetalk"):
            self.update_submission()
        if self.request.get("authorisedChanges"):
            self.authorised_update()