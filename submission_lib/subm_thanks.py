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
from speaker_lib import cospeaker


class SubmissionThankYouPage(basehandler.BaseHandler):
    def get(self):
        # remove the session flag that tells us this was a single page submit login
        self.session.pop("singlesubmit", 0)

        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        sub_key = ndb.Key(urlsafe=self.request.get("sub"))
        template_values = {
            'conference': conf_key.get(),
            'sub': sub_key.get(),
            'cospeakers': cospeaker.get_cospeakers(sub_key),
        }

        self.write_page('submission_lib/subm_thanks.html', template_values)
