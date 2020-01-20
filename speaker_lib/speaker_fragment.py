#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# Functions to support multiple uses of the speaker_fragment.html

# system imports
import logging

# library imports
from google.appengine.api import images

# local imports
import speaker
from scaffold import image
import speakerdir

def read_and_store_fields(handler, speaker):
    speaker.set_names(handler.request.get("speaker_first_name"), handler.request.get("speaker_later_names"))
    speaker.telephone = handler.request.get("telephone")
    speaker.address = handler.request.get("address")
    speaker.bio = handler.request.get("bio")

    speaker.set_field(speaker.FIELD_JOBTITLE, handler.request.get("jobtitle"))
    speaker.set_field(speaker.FIELD_COUNTRY, handler.request.get("country"))
    speaker.set_field(speaker.FIELD_AFFILICATION, handler.request.get("affiliation"))
    speaker.set_field(speaker.FIELD_TWITTER, handler.request.get("twitter"))
    speaker.set_field(speaker.FIELD_WEBPAGE, handler.request.get("webpage"))
    speaker.set_field(speaker.FIELD_BLOG, handler.request.get("blogpage"))
    speaker.set_field(speaker.FIELD_LINKEDIN, handler.request.get("linkedinprofile"))
    speaker.set_field(speaker.FIELD_TELEPHONE, handler.request.get("telephone"))
    speaker.set_field(speaker.FIELD_ADDRESS, handler.request.get("address"))
    speaker.put()

    if handler.request.get("deletepicture"):
        image.delete_image(speaker.key)
    else:
        if handler.request.params.has_key('speakerpicture'):
            image.store_only_image(speaker.key, handler.request.get('speakerpicture'))

def read_speaker_dir(handler, spk):
    if handler.request.get("speakerdir"):
        speakerdir.SpeakerDir().add_speaker(spk.key)
    else:
        speakerdir.SpeakerDir().remove_speaker(spk.key)
