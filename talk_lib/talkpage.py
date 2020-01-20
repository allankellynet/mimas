#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import talk
import talk_fragment
from speaker_lib import speaker
from submission_lib import submissionrecord
from scaffold import tags
import basehandler


class TalkPage(basehandler.BaseHandler):
    def existing_talk_values(self):
        t = ndb.Key(urlsafe=self.request.params['talk']).get()
        return {
            "talk_details": t,
            "is_new": False,
            "talk_key": t.key.urlsafe(),
            "tags": tags.TagList(t.key).pretty_tag_list(["Talk"]),
        }

    def new_talk(self):
        return {
            "talk_details": talk.Talk(parent=speaker.retreive_speaker(self.get_crrt_user().email()).key),
            "is_new": True,
            "talk_key": None,
            "tags": "",
        }

    def get(self):
        if self.request.params.has_key('talk'):
            template_values = self.existing_talk_values()
        else:
            template_values = self.new_talk()

        self.write_page('talk_lib/talkpage.html', template_values)

    def getTalkObject(self):
        if self.request.get("talk_key") == "None":
            spk = speaker.retreive_speaker(self.get_crrt_user().email())
            return talk.Talk(parent=spk.key)
        else:
            key = ndb.Key(urlsafe=self.request.get("talk_key"))
            return key.get()

    def deleteTalk(self):
        if self.request.get("talk_key") != "None":
            key = ndb.Key(urlsafe=self.request.get("talk_key"))
            submissionrecord.delete_submission_by_talk(key)
            key.delete()

    def post(self):
        if self.request.get("savetalk"):
            talk_fragment.readAndSave(self, self.getTalkObject())
            self.redirect("/list_submission")

        if self.request.get("savetalktags"):
            talk_key = talk_fragment.readAndSave(self, self.getTalkObject())
            self.redirect("/edittags?talk="+talk_key.urlsafe())

        if self.request.get("deletetalk"):
            self.deleteTalk()
            self.redirect("/list_submission")


