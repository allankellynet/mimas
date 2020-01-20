#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import speaker
from scaffold import sorrypage, attentionpage
import basehandler
from speaker_lib import speaker_fragment


class CoSpeakerPage(basehandler.BaseHandler):
    def get(self):
        if not(self.request.params.has_key("cospeaker")):
            sorrypage.redirect_sorry(self, "UnrecognisedCospeakerID")
            return

        cospeak = ndb.Key(urlsafe=self.request.get("cospeaker")).get()
        speaker_details = speaker.make_new_speaker(cospeak.email)
        speaker_details.name = cospeak.name

        if self.request.params.has_key("sub_key"):
            sub_key = self.request.get("sub_key")
        else:
            sub_key="Nokey"

        template_values = {
            'new_speaker': True,
            'speaker': speaker_details,
            'speakerKey': None,
            'readonly': "",
            "emaillocked": "readonly",
            "sub_key": sub_key,
        }

        self.write_page('speaker_lib/cospeakerpage.html', template_values)

    def store_speaker(self):
        spk = speaker.make_new_speaker(self.request.get("email"))
        speaker_fragment.read_and_store_fields(self, spk)

    def post(self):
        self.store_speaker()
        attentionpage.redirect_attention(self, "ThankYouCoSpeaker")

class CoSpeakerPageReturnToList(CoSpeakerPage):
    def post(self):
        self.store_speaker()
        self.redirect("/cospeakerlist?sub=" + self.request.get("sub_key"))
