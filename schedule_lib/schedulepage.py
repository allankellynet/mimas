#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedulepage.py
#

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import basehandler
from conference_lib import conference
from schedule_lib import schedule

class SchedulePage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.get_crrt_conference_key()
        sched = schedule.get_conference_schedule(conf_key)

        if self.request.params.has_key("day"):
            selected_day = self.request.get("day")
        else:
            selected_day = ""

        self.write_page('schedule_lib/schedulepage.html',
                        { "sched": sched.get(),
                          "selectedDay": selected_day,
                        })

    def post(self):
        if self.request.get("submitNewDay"):
            self.add_new_day()

        if self.request.get("deleteDay"):
            self.delete_day()

        if self.request.get("submitNewTrack"):
            self.add_track()

        self.redirect("/schedulepage")

    def add_new_day(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.add_day(self.request.get("newDay"), 1)

    def delete_day(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.delete_day(self.request.get("daysList"))

    def add_track(self):
        sched = ndb.Key(urlsafe=self.request.get("sched_key")).get()
        sched.get_day(self.request.get("daysList")).add_track(self.request.get("newTrack"))
