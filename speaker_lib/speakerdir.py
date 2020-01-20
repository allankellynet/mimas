#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports


class SpeakerDirEntry(ndb.Model):
    visible = ndb.BooleanProperty()

class SpeakerDir():
    def __init__(self):
        self.speaker_cache = None

    def retrieve_speaker_list(self):
        listed_speakers = SpeakerDirEntry.query().fetch(keys_only=True)
        l = map(lambda entry: entry.parent(), listed_speakers)
        return l

    def get_speaker_list(self):
        if self.speaker_cache == None:
            self.speaker_cache = self.retrieve_speaker_list()

        return self.speaker_cache

    def add_speaker(self, speaker_key):
        if self.is_speaker_listed(speaker_key):
            return

        new_speaker_entry = SpeakerDirEntry(parent=speaker_key)
        new_speaker_entry.visible = True
        new_speaker_entry.put()
        self.speaker_cache = None

    def remove_speaker(self, speaker_key):
        entries = SpeakerDirEntry.query(ancestor=speaker_key).fetch(keys_only=True)
        if len(entries)>0:
            entries[0].delete()
            self.speaker_cache = None

    def is_speaker_listed(self, speaker_key):
        return (SpeakerDirEntry.query(ancestor=speaker_key).count())>0
