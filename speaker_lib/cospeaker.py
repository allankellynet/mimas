#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
from speaker_lib.speaker import Speaker
from speaker_lib.speaker import make_new_speaker


class CoSpeaker(ndb.Model):
    cospeaker_email = ndb.StringProperty()
    cospeaker_name = ndb.StringProperty()

    @property
    def name(self):
        return self.cospeaker_name

    @property
    def email(self):
        return self.cospeaker_email

    def make_empty_profile(self):
        profile = make_new_speaker(self.cospeaker_email)
        profile.name = self.cospeaker_name
        profile.bio = "No bio supplied"
        return profile

    def profile(self):
        r = Speaker.query(Speaker.speaker_email == self.cospeaker_email).fetch(1)
        if (len(r) == 0):
            return self.make_empty_profile()
        else:
            return r[0]

    def profile_exists(self):
        return len(Speaker.query(Speaker.speaker_email == self.cospeaker_email).fetch(1))>0

# Factory rather than a constructor
def make_cospeaker(submission_key, name, email):
    cospeaker = CoSpeaker(parent=submission_key)
    cospeaker.cospeaker_email = email.lower()
    cospeaker.cospeaker_name = name
    cospeaker.put()
    return cospeaker

def get_cospeakers(submission_key):
    return CoSpeaker.query(ancestor=submission_key).fetch()

def delete_cospeakers(submission_key):
    for co in CoSpeaker.query(ancestor=submission_key).fetch():
        co.key.delete()

def filter_for_cospeakers(submission_keys):
    r = {}
    for sub in submission_keys:
        cospeakers = get_cospeakers(sub)
        if len(cospeakers) > 0:
            r[sub] = cospeakers

    return r

def get_pretty_list(submission_key):
    r = ""
    for co in get_cospeakers(submission_key):
        if r != "":
            r+=", "
        r += u"{} ({})".format(co.name, co.email)

    return r


class SpeakerTotals:
    def __init__(self):
        self.speaker_totals = {}
        self.speaker_names = {}

    def speaker(self, email):
        if self.speaker_totals.has_key(email):
            return self.speaker_totals[email]
        else:
            return 0

    def add_speaker(self, email, name):
        if self.speaker_totals.has_key(email):
            self.speaker_totals[email] += 1
        else:
            self.speaker_totals[email] = 1
            self.speaker_names[email] = name

    def total_number_of_speakers(self):
        return len(self.speaker_totals)

    def has_speaker(self, email):
        return self.speaker_names.has_key(email)

    def name(self, email):
        return self.speaker_names[email]

    def speaker_key(self, email):
        spk = Speaker.query(Speaker.speaker_email == email).fetch(1, keys_only=True)
        if len(spk)==0:
            return None
        else:
            return spk[0]

def count_all_speakers(submission_keys):
    speakers = SpeakerTotals()
    for key in submission_keys:
        sub = key.get()
        speakers.add_speaker(sub.email(), sub.submitter())
        for cospeaker in get_cospeakers(key):
            speakers.add_speaker(cospeaker.email, cospeaker.name)

    return speakers

def make_db_emails_lower_case():
    all_co_speakers = CoSpeaker.query().fetch()
    for co in all_co_speakers:
        co.cospeaker_email = co.cospeaker_email.lower()
        co.put()

def is_listed_cospeaker(email):
    return CoSpeaker.query(CoSpeaker.cospeaker_email==email).count()>0
