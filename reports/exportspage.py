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
from reports import reportrecord
from scaffold import userrights, userrightsnames, sorrypage

class ExportsPage(basehandler.BaseHandler):
    def get(self):
        crrt_conf = self.get_crrt_conference_key().get()

        if not(crrt_conf.user_rights().has_permission(self.get_crrt_user().email(),
                                                        userrightsnames.CONF_ADMINISTRATOR)):
            sorrypage.redirect_sorry(self, "NoAccess")
            return

        if self.request.params.has_key("newrpt"):
            newrpt = ndb.Key(urlsafe=self.request.get("newrpt")).get()
        else:
            newrpt = None

        self.write_page('reports/exportspage.html', {
            "crrt_conference": crrt_conf,
            "conf_key": crrt_conf.key,
            "reports": reportrecord.retrieve_reports_newest_to_oldset(crrt_conf.key),
            "newrpt": newrpt,
        })
