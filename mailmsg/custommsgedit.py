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
import custommsg


class EditCustomMsgPage(basehandler.BaseHandler):
    def get(self):
        if self.request.params.has_key("msg_key"):
            msg = ndb.Key(urlsafe=self.request.get("msg_key")).get()
            conf_key = msg.key.parent().urlsafe()
            new_msg = False
            msg_key = msg.key.urlsafe()
        else:
            msg = custommsg.CustomMsg()
            conf_key = self.request.get("conf_key")
            new_msg = True
            msg_key = "None"

        template_values = {
            "conf_key": conf_key,
            "message": msg,
            "new_msg": new_msg,
            "msg_key": msg_key,
        }

        self.write_page('mailmsg/custommsgedit.html', template_values)

    def create_msg(self):
        custommsg.make_custom_msg(ndb.Key(urlsafe=self.request.get("conf_key")),
                                  self.request.get("MsgName"),
                                  self.request.get("SubjectLine"),
                                  self.request.get("Message"))

    def update_msg(self):
        msg = ndb.Key(urlsafe=self.request.get("msg_key")).get()
        msg.set_name(self.request.get("MsgName"))
        msg.set_subject_line(self.request.get("SubjectLine"))
        msg.set_message(self.request.get("Message"))
        msg.put()

    def post(self):
        if self.request.get("submitmsg"):
            self.create_msg()
        if self.request.get("updatemsg"):
            self.update_msg()

        self.redirect("/custommsgpage?conf_key="+self.request.get("conf_key"))
