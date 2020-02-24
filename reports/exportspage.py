#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler

class ExportsPage(basehandler.BaseHandler):
    def get(self):
        crrt_conference = self.get_crrt_conference_key().get()

        ## TODO Permissions check -> should have admin

        self.write_page('reports/exportspage.html', {"crrt_conference": crrt_conference,
                                                     "conf_key": crrt_conference.key})
