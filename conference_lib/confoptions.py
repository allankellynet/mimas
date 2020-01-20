#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import logging
from google.appengine.api import users
from google.appengine.ext import ndb

# app imports

# Does not import conference_lib
# Conference class imports this class

class OptionCounter(ndb.Model):
    counter = ndb.IntegerProperty()

    def __init__(self, *args, **kwargs):
        super(OptionCounter, self).__init__(*args, **kwargs)
        self.counter = 0

def get_next_counter(conf_key):
    # No parent, should only be 1 instance in db
    counters = OptionCounter.query(ancestor=conf_key).fetch(1)
    if len(counters) == 0:
        crrt_counter = OptionCounter(parent=conf_key)
        crrt_counter.put()
    else:
        crrt_counter = counters[0]

    crrt_counter.counter = crrt_counter.counter+1
    crrt_counter.put()
    return crrt_counter.counter

class ConferenceOption(ndb.Model):
    shortname_m = ndb.StringProperty()
    full_text_m = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

    def shortname(self):
        return self.shortname_m

    def set_shortname(self, name):
        self.shortname_m = name

    def full_text(self):
        return self.full_text_m

    def set_full_text(self, txt):
        self.full_text_m = txt


class TrackOption(ConferenceOption):
    slots = ndb.IntegerProperty()

    def __init__(self, *args, **kwargs):
        super(TrackOption, self).__init__(*args, **kwargs)
        self.slots = 3

class DurationOption(ConferenceOption):
    pass

class TalkFormatOption(ConferenceOption):
    pass

class ExpenseOptions(ConferenceOption):
    pass

class AcknowledgementEmailCCAddresses(ConferenceOption):
    pass

class AcknowledgementEmailBCCAddresses(ConferenceOption):
    pass

class AcceptEmailCCAddress(ConferenceOption):
    pass

def make_conference_track(conf_key, text):
    track_opt = TrackOption(parent=conf_key)
    track_opt.set_shortname("Option"+str(get_next_counter(conf_key)))
    track_opt.set_full_text(text)
    track_opt.put()
    return track_opt

def make_conference_option(Option_Class, conf_key, text):
    option = Option_Class(parent=conf_key)
    option.set_shortname("Option"+str(get_next_counter(conf_key)))
    option.set_full_text(text)
    option.put()
    return option

def delete_track(conf_key, track_shortname):
    track = TrackOption.query(ancestor=conf_key).filter(ConferenceOption.shortname_m==track_shortname).fetch(1)
    track[0].key.delete()

def delete_option(option_type, conf_key, track_shortname):
    track = option_type.query(ancestor=conf_key).filter(ConferenceOption.shortname_m==track_shortname).fetch(1)
    track[0].key.delete()