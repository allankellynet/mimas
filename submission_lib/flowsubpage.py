#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb
from google.appengine.runtime import apiproxy_errors

# Local imports
from scaffold import sorrypage
import basehandler
from speaker_lib import speaker_fragment, speaker
from submission_lib import subm_entry_fragment, submission_queries, submission_ans
from talk_lib import talk, talk_fragment
from conference_lib import confdb, confquestion


def submission_overide(handler):
    return handler.session.has_key("submission_overide")


class FlowSubmitPage1(basehandler.BaseHandler):
    def welcome_sorry(self):
        self.write_page('scaffold/welcomesorry.html', {})

    def determine_conference(self):
        if self.session.has_key("singlesubmit"):
            return ndb.Key(urlsafe=self.session["singlesubmit"]).get()

        if self.request.params.has_key("cf"):
            conf = confdb.get_conf_by_shortname(self.request.get("cf"))
            if (conf == None):
                return None
        else:
            return None

        return conf

    def get(self):
        crrt_conf = self.determine_conference()
        if crrt_conf == None:
            self.welcome_sorry()
            return

        if not(crrt_conf.are_submissions_open() or submission_overide(self)):
            sorrypage.redirect_sorry(self, "ConfNotOpen")
            return

        self.set_crrt_conference_key(crrt_conf.key)

        user = self.get_crrt_user()
        spkr = speaker.retrieve_or_make(user.email())
        spkr.name = user.name()
        spkr.put()

        template_values = {
            "crrt_conf": crrt_conf,
            'new_speaker': True,
            'speaker': spkr,
            "emaillocked": "readonly",
            'speakerKey': spkr.key.urlsafe(),
            'readonly': "",
        }

        self.write_page('submission_lib/flowpage1.html', template_values)

    def store_speaker(self):
        spkr = ndb.Key(urlsafe=self.request.get("speaker_key")).get()
        speaker_fragment.read_speaker_dir(self, spkr)
        try:
            speaker_fragment.read_and_store_fields(self, spkr)
        except apiproxy_errors.RequestTooLargeError:
            sorrypage.redirect_sorry(self, "ImageTooBig")
            return None

        return spkr

    def post(self):
        spkr = self.store_speaker()
        if not(spkr is None):
            self.redirect("/flowsubmit2?speaker_key=" + spkr.key.urlsafe())

class FlowSubmitPage2(basehandler.BaseHandler):
    def get(self):
        crrt_conf = self.get_crrt_conference_key().get()
        spkr = ndb.Key(urlsafe=self.request.get("speaker_key")).get()

        if not(submission_overide(self)):
            if (submission_queries.count_submissions(crrt_conf.key, spkr.key) >= crrt_conf.max_submissions()):
                sorrypage.redirect_sorry(self, "SubsLimitReached")
                return

        template_values = { "crrt_conf" : crrt_conf,
                            "talk_details": talk.Talk(parent=None),
                            "speaker" : spkr,
                            }
        self.write_page('submission_lib/flowpage2.html', template_values)

    def process_talk(self, spk):
        new_talk = talk.Talk(parent=spk.key)
        talk_fragment.readAndSave(self, new_talk)
        return new_talk

    def post(self):
        spkr = ndb.Key(urlsafe=self.request.get("speaker_key")).get()
        tlk = self.process_talk(spkr)
        self.redirect("/flowsubmit3?speaker_key=" + spkr.key.urlsafe() +
                      "&talk_key=" + tlk.key.urlsafe())

class FlowSubmitPage3(basehandler.BaseHandler):
    def get(self):
        crrt_conf_key = self.get_crrt_conference_key()

        conf_questions = confquestion.retrieve_questions(crrt_conf_key)
        conf_answers = submission_ans.retrieve_answer_map(None, map(lambda q: q.key, conf_questions))

        template_values = { "crrt_conf" : crrt_conf_key.get(),
                            "speaker" : ndb.Key(urlsafe=self.request.get("speaker_key")).get(),
                            "talk": ndb.Key(urlsafe=self.request.get("talk_key")).get(),
                            "conf_questions": conf_questions,
                            "conf_answers": conf_answers,
                            }
        self.write_page('submission_lib/flowpage3.html', template_values)

    def post(self):
        crrt_conf = self.get_crrt_conference_key().get()
        spkr = ndb.Key(urlsafe=self.request.get("speaker_key")).get()
        tlk = ndb.Key(urlsafe=self.request.get("talk_key")).get()
        submission = subm_entry_fragment.make_submission(self, crrt_conf.key, tlk.key)
        self.redirect("/flowsubmit4?sub_key=" + submission.key.urlsafe() +
                      "&speaker_key=" + spkr.key.urlsafe() +
                      "&talk_key=" + tlk.key.urlsafe() )

class FlowSubmitPage4(basehandler.BaseHandler):
    def get(self):
        template_values = { "sub_key" : self.request.get("sub_key"),
                            "speaker_key" : self.request.get("speaker_key"),
                            "talk_key" : self.request.get("talk_key"),
                            }

        self.write_page('submission_lib/flowpage4.html', template_values)
