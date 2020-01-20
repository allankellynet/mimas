#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import logging
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore

# app imports


class ProtoSpeaker(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    speaker_email = ndb.StringProperty()
    speaker_name = ndb.StringProperty()

    def __init__(self, *args, **kwargs):
        super(ProtoSpeaker, self).__init__(*args, **kwargs)
        self.speaker_email = ""
        self.speaker_name = ""

    def name(self):
        return self.speaker_name

    def set_name(self, n):
        self.speaker_name = n

    def email(self):
        return self.speaker_email

    def set_email(self, address):
        self.speaker_email = address.lower()

def mk_proto_speaker(parent_key, name, email):
    p = ProtoSpeaker(parent=parent_key)
    p.set_name(name)
    p.set_email(email)
    p.put()
    return p
