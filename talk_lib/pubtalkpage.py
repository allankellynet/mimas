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


class PublicTalkPage(basehandler.BaseHandler):
    def get(self):
        talk = ndb.Key(urlsafe=self.request.get('talk')).get()
        template_values = {
            "talk_details": talk,
            "speaker": talk.key.parent().get(),
            "disabled": "disabled",
        }

        self.write_page("talk_lib/pubtalkpage.html", template_values)
