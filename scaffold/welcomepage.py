#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import logging

import requests

# Local imports
import sysinfo
from conference_lib import confdb
from scaffold import sorrypage, firebase
import basehandler


class WelcomePage(basehandler.BaseHandler):
    def show_page(self, conf):
        template_values = {
            "crrt_conf": conf,
            "firebase_config_variable": firebase.config_js_params(),
        }

        self.write_page('scaffold/welcomepage.html', template_values)

    def welcome_sorry(self):
        self.write_page('scaffold/welcomesorry.html', {})

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

        if self.request.params.has_key("overide"):
            self.session["submission_overide"] = 1

        self.session["singlesubmit"] = conf.key.urlsafe()

        if self.is_logged_in():
            self.redirect('/flowsubmit')
        else:
            self.show_page(conf)
