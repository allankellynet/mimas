#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net 
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from mailmsg import msgtemplate
from scaffold import sorrypage, userrightsnames
import basehandler


class MailTemplatesPage(basehandler.BaseHandler):
    def get(self):
        conf = ndb.Key(urlsafe=self.request.get("conf")).get()
        if not(conf.user_rights().has_permission(
                                        self.get_crrt_user().email(),
                                        userrightsnames.SPEAK_COMMS_COMMS)):
            sorrypage.redirect_sorry(self, "NoSpeakerCommsRights")
            return

        template_values = {
            "conf": conf,
            "decline": msgtemplate.retrieveTemplate(msgtemplate.DeclineMsg, conf.key),
            "accept": msgtemplate.retrieveTemplate(msgtemplate.AcceptMsg, conf.key),
            "acknowledge": msgtemplate.retrieveTemplate(msgtemplate.AcknowledgeMsg, conf.key),
        }

        self.write_page('mailmsg/mailtemplatespage.html', template_values)

    def update_fields(self, target, subject_name, msg_name):
        target.set_subject_line(self.request.get(subject_name))
        target.set_message(self.request.get(msg_name))
        target.put()

    def post(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        if self.request.get("SubmitDeclineMsg"):
            self.update_fields(msgtemplate.retrieveTemplate(msgtemplate.DeclineMsg, conf_key),
                               "DeclineSubject",
                               "DeclineMsg")
        elif self.request.get("SubmitAcceptMsg"):
            self.update_fields(msgtemplate.retrieveTemplate(msgtemplate.AcceptMsg, conf_key),
                               "AcceptSubject",
                               "AcceptMsg")
        elif self.request.get("SubmitAckMsg"):
            self.update_fields(msgtemplate.retrieveTemplate(msgtemplate.AcknowledgeMsg, conf_key),
                               "AckSubject",
                               "AckMsg")

        self.redirect("/mailmessages?conf=" + conf_key.urlsafe())
