#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedule_lib.py
#

# System imports
import datetime

# Google imports
import logging
from google.appengine.ext import ndb

# Local imports

class Slot():
    def __init__(self, start, end, type):
        self.start_time = start
        self.end_time = end
        self.slot_type = type # Tracks or Plenary

class ScheduleDay():
    def __init__(self):
        self.day_tracks = []
        self.day_slots = {}

class Schedule(ndb.Model):
    setup_days_db = ndb.PickleProperty()
    assignment_db = ndb.PickleProperty() # map: Dayname -> SlotsName -> SubKey

    def __init__(self, *args, **kwargs):
        super(Schedule, self).__init__(*args, **kwargs)
        self.setup_days_db = {}
        self.assignment_db = {}

    def day_names(self):
        return self.setup_days_db.keys()

    def add_day(self, day_name):
        self.setup_days_db[day_name] = ScheduleDay()
        self.put()

    def get_day(self, day_name):
        return self.setup_days_db[day_name]

    def delete_day(self, day_name):
        if self.setup_days_db.has_key(day_name):
            del self.setup_days_db[day_name]
            self.put()

    def tracks(self, day_name):
        if self.setup_days_db.has_key(day_name):
            return self.setup_days_db[day_name].day_tracks

        return []

    def add_track(self, day_name, track):
        self.setup_days_db[day_name].day_tracks.append(track)
        self.put()

    def del_track(self, day_name, track):
        self.setup_days_db[day_name].day_tracks.remove(track)
        self.put()

    def slots(self, day_name):
        if self.setup_days_db.has_key(day_name):
            return self.setup_days_db[day_name].day_slots

        return []

    def orderd_slot_keys(self, day_name):
        if self.setup_days_db.has_key(day_name):
            keys = self.setup_days_db[day_name].day_slots.keys()
            keys.sort()
            return keys

        return []

    def add_slot(self, day_name, slot):
        self.setup_days_db[day_name].day_slots[slot.start_time]=slot
        self.put()

    def delete_slot_by_start_time(self, day_name, start_time):
        self.setup_days_db[day_name].day_slots.pop(start_time, None)
        self.put()

    def get_assignment(self, day, track, slot):
        if self.assignment_db.has_key(day):
            if self.assignment_db[day].has_key(track):
                if self.assignment_db[day][track].has_key(slot):
                    return self.assignment_db[day][track][slot]

        return "Empty"

    def assign_talk(self, sub_key, day, track, slot):
        if not(self.assignment_db.has_key(day)):
            self.assignment_db[day] = {}

        if not(self.assignment_db[day].has_key(track)):
            self.assignment_db[day][track] = {}

        self.assignment_db[day][track][slot] = sub_key
        self.put()

    def clear_talk(self, day, track, slot):
        if not(self.assignment_db.has_key(day)):
            return

        if not(self.assignment_db[day].has_key(track)):
            return

        del self.assignment_db[day][track][slot]
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

