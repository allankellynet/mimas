#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedulepage.py
#

# System imports

# Google imports

# Local imports
import basehandler

class ScheduleConfigPage(basehandler.BaseHandler):
    def get(self):
        conf = self.get_crrt_conference_key().get()

        self.write_page('schedule/scheduleconfigpage.html',
                        {
                        })

    def post(self):
        pass
