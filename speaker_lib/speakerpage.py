#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

from google.appengine.ext import ndb
from google.appengine.runtime import apiproxy_errors

# Local imports
import speaker
import speaker_fragment
import speakerdir
from scaffold import sorrypage, attentionpage, tags
import basehandler


class SpeakerPage(basehandler.BaseHandler):
    def get(self):
        user_email = self.get_crrt_user().email()

        if speaker.speaker_exists(user_email):
            new_speaker = False
        else:
            new_speaker = True

        speaker_details = speaker.retrieve_or_make(user_email)

        template_values = {
            'new_speaker': new_speaker,
            'speaker': speaker_details,
            'speakerKey': speaker_details.key.urlsafe(),
            'readonly': "",
            "emaillocked": "readonly",
            "updateable": True,
            "dir_selected": speakerdir.SpeakerDir().is_speaker_listed(speaker_details.key),
            "speaker_tags": tags.TagList(speaker_details.key).pretty_tag_list(["Speaker"])
        }

        self.write_page('speaker_lib/speakerpage.html', template_values)

    def post_update_redirect(self):
        self.redirect("/speakermain")

    def update_speaker(self):
        spk = ndb.Key(urlsafe=self.request.get("speakerKey")).get()

        speaker_fragment.read_speaker_dir(self, spk)
        speaker_fragment.read_and_store_fields(self, spk)

        return spk.key

    def delete_speaker(self):
        spk = ndb.Key(urlsafe=self.request.get("speakerKey")).get()
        spk.zero_out_speaker()

    def post(self):
        if self.request.get("deletespeaker"):
            self.delete_speaker()

        try:
            if self.request.get("updatespeaker"):
                self.update_speaker()
                self.post_update_redirect()

            if self.request.get("updatetags"):
                k = self.update_speaker()
                self.redirect("/edittags?spk=" + k.urlsafe())
        except apiproxy_errors.RequestTooLargeError:
            sorrypage.redirect_sorry(self, "ImageTooBig")


def write_readonly_speaker_page(handler, who):
    template_values = {
        'new_speaker': False,
        'speaker': who,
        'speakerKey': who.key,
        'readonly': "readonly",
        "emaillocked": "readonly",
        "updateable": False,
        "dir_selected": False, # not used
        "speaker_tags": tags.TagList(who.key).pretty_tag_list([])
    }

    handler.write_page('speaker_lib/speakerpage.html', template_values)


class SpeakerPageByEmail(SpeakerPage):
    def get(self):
        if not(self.request.params.has_key("email")):
            attentionpage.redirect_attention(self, "SpeakerAddressMissing")
            return

        email = self.request.get("email")
        if not(speaker.speaker_exists(email)):
            attentionpage.redirect_attention(self, "UnknownSpeaker")
            return

        who = speaker.retreive_speaker(email)
        write_readonly_speaker_page(self, who)

class SpeakerPageByKey(SpeakerPage):
    def get(self):
        if not(self.request.params.has_key("key")):
            attentionpage.redirect_attention(self, "SpeakerAddressMissing")
            return

        key = ndb.Key(urlsafe=self.request.get("key"))
        write_readonly_speaker_page(self, key.get())

class SpeakerUpdatePage(SpeakerPage):
    def get(self):
        if self.request.params.has_key("email"):
            email = self.request.get("email")
        else:
            sorrypage.redirect_sorry(self, "SpeakerPageAccessDenied")
            return

        if self.request.params.has_key("key"):
            requested_speaker = self.request.get("key")
        else:
            sorrypage.redirect_sorry(self, "SpeakerPageKeyNotSupplied")
            return

        if speaker.speaker_exists(email):
            speaker_details = speaker.retreive_speaker(email)
            speaker_key = speaker_details.key.urlsafe()
        else:
            speaker_key = None
            speaker_details = None

        if speaker_key != requested_speaker:
            sorrypage.redirect_sorry(self, "SpeakerPageCredentialsDoNotMatch")
            return

        template_values = {
            'new_speaker': False,
            'speaker': speaker_details,
            'speakerKey': speaker_key,
            'readonly': "",
            "emaillocked": "readonly",
            "updateable": True,
            "dir_selected": speakerdir.SpeakerDir().is_speaker_listed(speaker_key),
            "speaker_tags": tags.TagList(speaker_key).pretty_tag_list()
        }

        self.write_page('speakerpage.html', template_values)

    def post_update_redirect(self):
        attentionpage.redirect_attention(self, "SpeakUpdateDone")
