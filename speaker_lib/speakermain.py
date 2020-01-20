#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler
import speaker
from talk_lib import talk


class SpeakerMainPage(basehandler.BaseHandler):
    def get(self):
        username = self.get_crrt_user().email()
        template_values = {
            'name': username,
            'speaker_exists': speaker.speaker_exists(username),
            'talk_count': len(talk.all_user_talks_by_email(username)),
        }

        self.write_page('speaker_lib/speakermain.html', template_values)
