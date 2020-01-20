#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import confquestion
from scaffold import sorrypage, userrightsnames
import basehandler


class ConferenceQuestionsPage(basehandler.BaseHandler):

    def get(self):
        if not(self.request.params.has_key("conf")):
            sorrypage.redirect_sorry(self, "ConfKeyMissing")
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        disabled = ""
        if conference.state() != "Closed":
            disabled = "disabled"

        if not(conference.user_rights().has_permission(self.get_crrt_user().email(),
                                                       userrightsnames.CONF_CREATOR)):
            sorrypage.redirect_sorry(self, "NoAccess")
            return

        template_values = {
            "crrt_conf": conference,
            "conf_key": conference.key,
            "questions": confquestion.retrieve_questions(conf_key),
            "read_only": disabled,
        }

        self.write_page('conference_lib/confquestionspage.html', template_values)

    def add_question(self, conf_key):
        confquestion.mk_question(conf_key, self.request.get("new_question"))

    def delete_selected(self, conf_key):
        for q in confquestion.retrieve_questions(conf_key):
            if self.request.get(q.key.urlsafe()):
                confquestion.delete_question_and_answers(q)

    def add_answer(self, conf_key):
        answer = self.request.get("new_answer")
        if answer == "":
            return

        for q in confquestion.retrieve_questions(conf_key):
            if self.request.get(q.key.urlsafe()):
                q.add_option(answer)

    def post(self):
        conf_key = ndb.Key(urlsafe=self.request.get("crrt_conf_key"))
        if self.request.get("addquestion"):
            self.add_question(conf_key)
        if self.request.get("delete_selected"):
            self.delete_selected(conf_key)
        if self.request.get("addanswer"):
            self.add_answer(conf_key)

        self.redirect("/confquestionspage?conf=" + self.request.get("crrt_conf_key"))