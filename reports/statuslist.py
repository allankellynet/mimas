#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler
from submission_lib import submissionrecord
from talk_lib import talk


class StatusListPage(basehandler.BaseHandler):
    def get(self):
        user = self.get_crrt_user().email()

        template_values = {
            "username": user,
            "talks": talk.all_user_talks_by_email(user),
            "conf_submits": submissionrecord.get_confences_talk_submitted_to,
            "submit_key": submissionrecord.get_submission_by_talk_and_conf,
        }

        self.write_page('reports/statuslist.html', template_values)
