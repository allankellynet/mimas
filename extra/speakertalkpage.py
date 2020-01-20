#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# System imports
import sys

# Google imports

# Local imports
import basehandler
from speaker_lib import cospeaker, speaker
from talk_lib import talk

class SpeakerTalksPage(basehandler.BaseHandler):
    def get(self):
        speakers = self.duplicate_speakers()
        talks = self.speaker_talks(speakers)
        template_values = {
            "speakers": speakers,
            "talks": talks,
            "is_cospeaker_func": cospeaker.is_listed_cospeaker,
        }

        self.write_page('extra/speakertalkpage.html', template_values)

    def duplicate_speakers(self):
        sys.setrecursionlimit(9999)
        duplicates = speaker.find_duplicate_speakers()

        speakers = []
        for dup in duplicates:
            speakers = speakers + speaker.Speaker.query(speaker.Speaker.speaker_email == dup.email).fetch()

        return speakers

    def speaker_talks(self, speakers):
        talks = {}
        for spk in speakers:
           talks[spk.key] = talk.speaker_talks_by_key(spk.key)

        return talks