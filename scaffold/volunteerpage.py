#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
from conference_lib import confdb
from scaffold import sorrypage, firebase
import basehandler


class VolunteerPage(basehandler.BaseHandler):
    def show_page(self, conf):
        template_values = {
            "crrt_conf": conf,
            "firebase_config_variable" : firebase.config_js_params()
        }

        self.write_page('scaffold/welcomepage.html', template_values)

    def welcome_sorry(self):
        template_values = {
        }

        self.write_page('scaffold/welcomesorry.html', template_values)

    def get(self):
        if self.request.params.has_key("cf"):
            shortname = self.request.get("cf")
        else:
            self.welcome_sorry()
            return

        conf = confdb.get_conf_by_shortname(shortname)
        if (conf == None):
            self.welcome_sorry()
            return

        if not(conf.are_submissions_open()):
            sorrypage.redirect_sorry(self, "VolunteerReviewerClosed")
            return

        self.session["conference_volunteer"] = conf.key.urlsafe()

        if self.is_logged_in():
            self.redirect('/volunteerreviewer')
        else:
            self.show_page(conf)
