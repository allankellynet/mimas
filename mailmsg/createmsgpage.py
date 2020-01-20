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


class CreateMsgPage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.request.get("conf_key")
        template_values = {
            "conf_key": conf_key,
            "messages": custommsg.retrieve_custom_message(ndb.Key(urlsafe=conf_key))
        }

        self.write_page('mailmsg/createmsgpage.html', template_values)

    def get_all_checked(self):
        checked = self.request.get_all("selectedmsg")
        keys = []
        for c in checked:
            keys.append(ndb.Key(urlsafe=c))

        return keys

    def delete_msgs(self):
        for k in self.get_all_checked():
            k.delete()

    def post(self):
        if self.request.get("deletemsgs"):
            self.delete_msgs()

        self.redirect("/custommsgpage?conf_key=" + self.request.get("conf_key"))
