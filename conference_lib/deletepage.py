#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler
import confdelete

class DeletePage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.get_crrt_conference_key()

        template_values = {
            "conference": conf_key.get(),
        }

        self.write_page('conference_lib/deletepage.html', template_values)

    def post(self):
        if self.request.get("DeleteConf"):
            confdelete.cascade_delete_conference(self.get_crrt_conference_key())
            self.clear_crrt_conference()

        self.redirect("/")
