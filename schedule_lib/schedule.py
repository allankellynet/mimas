#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedule_lib.py
#

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports

class ScheduleDay():

    def __init__(self, day_pos):
        self.day_pos = day_pos
        self.day_tracks = []

    def day_number(self):
        return self.day_pos

    def tracks(self):
        return self.day_tracks

    def add_track(self, track):
        self.day_tracks.append(track)

    def del_track(self, track):
        self.day_tracks.remove(track)

class Schedule(ndb.Model):
    days_db = ndb.PickleProperty()

    def __init__(self, *args, **kwargs):
        super(Schedule, self).__init__(*args, **kwargs)
        self.days_db = {}

    def day_names(self):
        return self.days_db.keys()

    def add_day(self, day_name, day_position):
        self.days_db[day_name] = ScheduleDay(day_position)
        self.put()

    def get_day(self, day_name):
        return self.days_db[day_name]

    def delete_day(self, day_name):
        if self.days_db.has_key(day_name):
            del self.days_db[day_name]
            self.put()

def make_schedule(conf_key):
    sched = Schedule(parent=conf_key)
    sched.put()
    return [sched.key]

def get_conference_schedule(conf_key):
    sched_keys = Schedule.query(ancestor=conf_key).fetch(keys_only=True)
    if len(sched_keys) == 0:
        sched_keys = make_schedule(conf_key)

    return sched_keys[0]
