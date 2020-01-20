#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from scaffold import tags
import basehandler
from talk_lib import talk

class PublicSpeakerPage(basehandler.BaseHandler):
    def get(self):
        speaker = ndb.Key(urlsafe=self.request.get("skey")).get()
        talks = talk.speaker_talks_by_key(speaker.key)
        template_values = {
            "speaker": speaker,
            "talks": talks,
            "talk_count": len(talks),
            "taglist_func": tags.taglist_func,
        }

        self.write_page('speaker_lib/publicspage.html', template_values)
