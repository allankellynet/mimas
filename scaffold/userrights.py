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
from scaffold import userrightsnames


class RightsRecord(ndb.Model):
    username = ndb.StringProperty()
    conference_admin = ndb.BooleanProperty()
    track_reviews = ndb.PickleProperty()
    permissions = ndb.PickleProperty()

    def __init__(self, *args, **kwargs):
        super(RightsRecord, self).__init__(*args, **kwargs)
        self.username = ""
        self.conference_admin = False
        self.track_reviews = []
        self.permissions = set()

class UserRights():
    def __init__(self, conf_key):
        self.conference_key = conf_key

    def query_rights(self, user):
        # when conference is None (which can happen)
        # then no existing records will be found so a new but empty object will be returned
        # but the object has no rights so everything will be false
        # (there are tests to show that)
        rights = RightsRecord.query(ancestor=self.conference_key).filter(RightsRecord.username == user).fetch()
        if len(rights) == 0:
            new_right = RightsRecord(parent=self.conference_key)
            new_right.username = user
            return new_right
        else:
            return rights[0]

    def drop_conference_admin(self, user):
        rights = self.query_rights(user)
        rights.conference_admin = False
        rights.put()

    def is_track_reviewer(self, name, track):
        rights = self.query_rights(name)
        if rights == None:
            return False

        return track in rights.track_reviews

    def tracks_to_review(self, name):
        return self.query_rights(name).track_reviews

    def has_track_review_rights(self, name):
        rights = self.query_rights(name)
        if rights == None:
            return False

        return len(rights.track_reviews) > 0

    def add_track_reviewer(self, name, track):
        if not (self.is_track_reviewer(name, track)):
            rights = self.query_rights(name)
            rights.track_reviews.append(track)
            rights.put()

    def drop_track_reviewer(self, name, track):
        if (self.is_track_reviewer(name, track)):
            rights = self.query_rights(name)
            del rights.track_reviews[rights.track_reviews.index(track)]
            rights.put()

    def drop_track(self, track):
        rights = RightsRecord.query(ancestor=self.conference_key).fetch()
        for r in rights:
            if track in r.track_reviews:
                self.drop_track_reviewer(r.username, track)

    def remove_all_review_rights(self, name):
        rights = self.query_rights(name)
        rights.track_reviews = []
        rights.put()

    def track_assignments_string(self, name):
        return ", ".join(self.query_rights(name).track_reviews)

    def track_assignments(self, name):
        return self.query_rights(name).track_reviews

    def list_all_reviewers(self):
        r = []
        for usr in RightsRecord.query(ancestor=self.conference_key).fetch():
            if self.has_review_rights(usr.username):
                r.append(usr.username)

        return r

    def has_permission(self, name, permission):
        rights = self.query_rights(name)
        if rights == None:
            logging.info("UserRights::has_permission: no rights")
            return False

        r = permission in rights.permissions
        return r

    def add_permission(self, name, permission):
        rights = self.query_rights(name)
        if rights == None:
            rights = RightsRecord()

        rights.permissions.add(permission)
        rights.put()

    def drop_permission(self, name, permission):
        rights = self.query_rights(name)
        if rights is not None:
            rights.permissions.discard(permission)
            rights.put()

    def drop_all_permissions(self, name):
        rights = self.query_rights(name)
        if rights is not None:
            rights.permissions = rights.permissions - rights.permissions
            rights.put()

    def permissions(self):
        return {
            userrightsnames.CHANGE_CONF_STATE: "Change conference state",
            userrightsnames.APPOINT_REVIEWERS: "Assign track reviewers",
            userrightsnames.ROUND1_REVIEWER: "Round 1 review permissions",
            userrightsnames.ROUND2_REVIEWER: "Round 2 review permissions",
            userrightsnames.ROUND1_DECISION: "Round 1 final decision authority",
            userrightsnames.ROUND2_DECISION: "Round 2 final decision authority",
            userrightsnames.ROUND1_FULL_VIEW: "Round 1 full read only view",
            userrightsnames.ROUND2_FULL_VIEW: "Round 2 full read only view",
            userrightsnames.SPEAK_COMMS_COMMS: "Speaker communications",
            userrightsnames.CONF_DATA_DUMPS: "Export conferences data to files",
            userrightsnames.CONF_ADMINISTRATOR: "Conference administrator",
            userrightsnames.CONF_SCHEDULE: "Conference scheduler",
        }

    def list_permission_holders(self):
        all = RightsRecord.query(ancestor=self.conference_key).fetch()
        r = []
        for usr in all:
            if len(usr.permissions) > 0:
                r.append(usr.username)

        return r

    def readable_permissions(self, name):
        return ", ".join(self.query_rights(name).permissions)

    def can_view_all(self, name):
        rights = self.query_rights(name)
        if rights == None:
            return False
        elif userrightsnames.ROUND1_DECISION in rights.permissions:
            return True
        elif userrightsnames.ROUND2_DECISION in rights.permissions:
            return True
        elif userrightsnames.ROUND1_FULL_VIEW in rights.permissions:
            return True
        elif userrightsnames.ROUND2_FULL_VIEW in rights.permissions:
            return True
        else:
            return False

    def has_special_rights(self, user):
        rights = RightsRecord.query(ancestor=self.conference_key).\
            filter(RightsRecord.username == user).count()
        return rights>0

    def has_review_rights(self, name):
        rights = self.query_rights(name)
        if rights == None:
            return False
        elif userrightsnames.ROUND1_DECISION in rights.permissions:
            return True
        elif userrightsnames.ROUND2_DECISION in rights.permissions:
            return True
        elif userrightsnames.ROUND1_REVIEWER in rights.permissions:
            return True
        elif userrightsnames.ROUND2_REVIEWER in rights.permissions:
            return True
        elif userrightsnames.ROUND1_FULL_VIEW in rights.permissions:
            return True
        elif userrightsnames.ROUND2_FULL_VIEW in rights.permissions:
            return True
        else:
            return False

    def has_decision_rights(self, name):
        rights = self.query_rights(name)
        if rights == None:
            return False
        elif userrightsnames.ROUND1_DECISION in rights.permissions:
            return True
        elif userrightsnames.ROUND2_DECISION in rights.permissions:
            return True
        else:
            return False

    def has_decision_right_for_round(self, email, review_round):
        round_to_permission = { 1: userrightsnames.ROUND1_DECISION,
                                2: userrightsnames.ROUND2_DECISION}
        return round_to_permission[review_round] in self.query_rights(email).permissions

    def list_reviewers(self, review_round):
        round_review_permission = {
                                1: userrightsnames.ROUND1_REVIEWER,
                                2: userrightsnames.ROUND2_REVIEWER }

        rights_records = RightsRecord.query(ancestor=self.conference_key).fetch()
        reviewers = filter(lambda r: round_review_permission[review_round] in r.permissions,
                           rights_records)
        names = map(lambda n: n.username, reviewers)

        return names
