#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system
import datetime

# library
from google.appengine.ext import ndb

# local
from speaker_lib import speaker

class MimasUser(ndb.Model):
    user_name = ndb.StringProperty()
    user_email = ndb.StringProperty()
    user_given_unique_id = ndb.StringProperty()
    user_last_login = ndb.DateTimeProperty()

    def __init__(self, *args, ** kwargs):
        super(MimasUser, self).__init__(*args, **kwargs)
        self.user_email=""
        self.user_name=""
        self.user_speaker_key = None
        self.user_given_unique_id = ""
        self.user_last_login = datetime.datetime(2017,9,23)

    def name(self):
        return self.user_name

    def set_name(self, name):
        self.user_name = name

    def email(self):
        return self.user_email

    def set_email(self, email):
        self.user_email = email

    def speaker_key(self):
        return self.user_speaker_key

    def set_speaker_key(self, key):
        self.user_speaker_key = key

    def unique_id(self):
        return self.user_given_unique_id

    def set_unique_id(self, id):
        self.user_given_unique_id = id

    def last_login(self):
        return self.user_last_login

    def set_last_login(self,login_time):
        self.user_last_login = login_time

def mk_MimasUser(name, email, unique_id):
    usr = MimasUser()
    usr.set_name(name)
    usr.set_email(email)
    usr.set_unique_id(unique_id)
    usr.put()
    return usr

def find_user_by_id(unique_id):
    r = MimasUser.query().filter(MimasUser.user_given_unique_id == unique_id).fetch()
    if len(r) == 0:
        return None

    return r[0]

def find_user_by_email(email):
    r = MimasUser.query().filter(MimasUser.user_email == email).fetch()
    if len(r) == 0:
        return None

    return r[0]

