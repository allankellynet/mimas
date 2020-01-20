#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
from speaker_lib import speaker

# Recgonised fields	
SHORT_SYNOPSIS = "shortsynopsis"
LONG_SYNOPSIS = "longsynopsis"


class Talk(ndb.Model):
    talk_title = ndb.StringProperty()
    details = ndb.PickleProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    directory_listing = ndb.StringProperty()

    def __init__(self, *args, **kwargs):
        super(Talk, self).__init__(*args, **kwargs)
        self.talk_title = ""
        self.directory_listing = "Listed"
        self.details = {}

    def field(self, f):
        if (self.details.has_key(f)):
            return self.details[f]

        return ""

    def field_ascii(self, f):
        return self.field(f).encode('ascii', 'ignore')

    def set_field(self, field, value):
        self.details[field] = value

    @property
    def title(self):
        return self.talk_title

    @title.setter
    def title(self, t):
        self.talk_title = t

    def is_listed(self):
        return "Listed" == self.directory_listing

    def hide_listing(self):
        self.directory_listing = "Not listed"

    def show_listing(self):
        self.directory_listing = "Listed"

def mk_talk(parent_key, title):
    t = Talk(parent=parent_key)
    t.talk_title = title
    t.put()
    return t.key

def all_user_talks_by_email(username):
    if not speaker.speaker_exists(username):
        return {}

    who = speaker.retreive_speaker(username)
    return Talk.query(ancestor=who.key).fetch()

def speaker_talks_by_key(speaker_key):
    return Talk.query(ancestor=speaker_key).fetch()