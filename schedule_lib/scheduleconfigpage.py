#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedulepage.py
#

# System imports
import logging
from google.appengine.ext import ndb
from datetime import datetime, time

# Local imports
import basehandler
from conference_lib import conference
from schedule_lib import schedule


class ScheduleConfigPage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.get_crrt_conference_key()
        sched = schedule.get_conference_schedule(conf_key).get()

        selected_day = self.selected_day(sched)

        self.write_page('schedule_lib/scheduleconfigpage.html',
                        {"sched": sched,
                         "selectedDay": selected_day,
                         })

    def selected_day(self, sched):
        if self.request.params.has_key("day"):
            return self.request.get("day")
        else:
            return ""

    def post(self):
        crrt_day = self.request.get("daysList")

        if self.request.get("submitNewDay"):
            crrt_day = self.add_new_day()

        if self.request.get("deleteDay"):
            self.delete_day()

        if self.request.get("submitNewTrack"):
            self.add_track()

        if self.request.get("deleteTrack"):
            self.delete_tracks()

        if self.request.get("submitNewSlot"):
            self.add_slot()

        if self.request.get("deleteSlot"):
            self.delete_slots()

        self.redirect("/scheduleconfigpage?day=" + crrt_day)

    def add_new_day(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.add_day(self.request.get("newDay"))
        return self.request.get("newDay")

    def delete_day(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.delete_day(self.request.get("daysList"))

    def add_track(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.add_track(self.request.get("daysList"), self.request.get("newTrack"))

    def delete_tracks(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        for track_name in self.request.get_all("trackCheck"):
            sched.del_track(self.request.get("daysList"), track_name)

    def add_slot(self):
        start = datetime.strptime(self.request.get("newSlotStart"),"%H:%M").time()
        end = datetime.strptime(self.request.get("newSlotEnd"),"%H:%M").time()

        audience = self.request.get("audiencetype")

        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.add_slot(self.request.get("daysList"), schedule.Slot(start, end, audience))

    def delete_slots(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        slots_to_delete = self.request.get_all("slotCheck")
        for slot in slots_to_delete:
            sched.delete_slot_by_start_time(self.request.get("daysList"), slot)
