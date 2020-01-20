#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
from conference_lib import confdb
from scaffold import sysinfo
import basehandler


class ChooseConfPage(basehandler.BaseHandler):
    def get(self):
        user = self.get_crrt_user()

        all_conf = confdb.retrieve_special_rights_conferences(user.email())

        template_values = {
            'name': user.email(),
            'conference_count': len(all_conf),
            "conferences": all_conf,
            'is_running_local': sysinfo.is_running_local,
            'admin': sysinfo.is_system_admin,
        }

        self.write_page('conference_lib/chooseconf.html', template_values)

    def post(self):
        conf_key = self.request.get("conference")
        self.session["crrt_conference"] = conf_key
        self.redirect("/chooseconf")
