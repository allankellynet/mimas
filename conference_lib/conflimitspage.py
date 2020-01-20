#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from scaffold import sorrypage, userrightsnames
import basehandler


class ConferenceConfigPage(basehandler.BaseHandler):
    def edit_permission(self, conference):
        if conference.user_rights().has_permission(self.get_crrt_user().email(),
                                                userrightsnames.CONF_CREATOR):
            return ""
        else:
            return "disabled"

    def get(self):
        if not(self.request.params.has_key("conf")):
            sorrypage.redirect_sorry(self, "ConfKeyMissing")
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        template_values = {
            "crrt_conf": conference,
            "conf_key": conference.key,
            "read_only": self.edit_permission(conference),
        }

        self.write_page('conference_lib/conflimitspage.html', template_values)

    def update_conf(self):
        conf = ndb.Key(urlsafe=self.request.get("conf_key")).get()
        conf.set_max_submissions(int(self.request.get("max_submissions")))
        conf.set_max_cospeakers(int(self.request.get("max_cospeakers")))
        conf.put()

    def post(self):
        if self.request.get("updateconfig"):
            self.update_conf()

        self.redirect("/createconf?conf="+self.request.get("conf_key"))