#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import logging

from google.appengine.ext import ndb

# app imports


class VolunteerReviewer(ndb.Model):
    name_db = ndb.StringProperty()
    email_db = ndb.StringProperty()
    tracks_db = ndb.PickleProperty()
    accepted_db = ndb.StringProperty()

    def name(self):
        return self.name_db

    def email(self):
        return self.email_db

    def tracks(self):
        return self.tracks_db

    def accepted(self):
        return self.accepted_db

    def accept(self):
        self.accepted_db = "Accepted"
        self.put()

    def reject(self):
        self.accepted_db = "Rejected"
        self.put()

def mk_volunteer_reviewer(conf_key, name, email, tracks):
    vr = VolunteerReviewer(parent=conf_key)
    vr.name_db = name
    vr.email_db = email
    vr.tracks_db = tracks
    vr.accepted_db = ""
    vr.put()
    return vr

def retrieve_all_volunteers(conf_key):
    return VolunteerReviewer.query(ancestor=conf_key).fetch()
