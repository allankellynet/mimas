#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports

# Local imports
from scaffold import firebase
import basehandler


class LogoutBasicGooglePage(basehandler.BaseHandler):
    def get(self):
        self.session.pop("uk")

        self.write_page('scaffold/logoutpageb.html', {})


class LogoutFirebasePage(basehandler.BaseHandler):
    def get(self):
        self.session.pop("uk")

        self.write_page('scaffold/logoutpage.html', {"firebase_config_variable" : firebase.config_js_params()})
