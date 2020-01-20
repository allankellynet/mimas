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
import cospeaker
from mailmsg import msgtemplate, postmail
from speaker_lib import speaker


class CoSpeakerListPage(basehandler.BaseHandler):
    def get(self):
        sub = ndb.Key(urlsafe=self.request.get("sub")).get()
        conf = sub.key.parent().get()
        cospeakers = cospeaker.get_cospeakers(sub.key)
        speaker_count = len(cospeakers)+1

        if speaker_count >= conf.max_cospeakers():
            more_speakers = "disabled"
        else:
            more_speakers = ""

        template_values = {
            "sub": sub,
            "cospeakers": cospeakers,
            "speaker_count": speaker_count,
            "max_speakers": conf.max_cospeakers(),
            "more_speakers": more_speakers,
        }

        self.write_page('speaker_lib/cospeakerlistpg.html', template_values)

    def post_notification(self, sub_key, cospeak_key):
        if speaker.speaker_exists(self.request.get("cospeakeremail")):
            msg = msgtemplate.CoSpeakerBioExistsMsg()
        else:
            msg = msgtemplate.CoSpeakerBioRequestMsg()

        msg.set_cospeaker(cospeak_key)

        conference = sub_key.parent().get()
        msg.set_from_name_and_address(conference.name, conference.contact_email())
        msg.set_to_address(self.request.get("cospeakeremail"))
        postmail.Postman().post_addressed_one(conference, msg, sub_key)

    def add_cospeakers(self):
        sub_key = ndb.Key(urlsafe=self.request.get("sub_key"))
        cospeak = cospeaker.make_cospeaker(sub_key,
                                           self.request.get("cospeakername"),
                                           self.request.get("cospeakeremail"))
        self.post_notification(sub_key, cospeak.key)


    def speakers_to_delete(self):
        checked = self.request.get_all("checked_cospeaker")
        co_speakers = []
        for c in checked:
            co_speakers.append(ndb.Key(urlsafe=c))

        return co_speakers

    def delete_cospeakers(self):
        for d in self.speakers_to_delete():
            d.delete()

    def post(self):
        if self.request.get("add_cospeakers"):
            self.add_cospeakers()
        elif self.request.get("delete_cospeakers"):
            self.delete_cospeakers()

        self.redirect("/cospeakerlist?sub=" + self.request.get("sub_key"))