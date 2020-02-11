#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedulepage.py
#

# System imports

# Google imports
import logging
from google.appengine.ext import ndb

# Local imports
import basehandler
from conference_lib import conference
from submission_lib import submissionrecord
from schedule_lib import schedule

class SchedulePage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.get_crrt_conference_key()
        sched = schedule.get_conference_schedule(conf_key)

        if self.request.params.has_key("day"):
            selected_day = self.request.get("day")
        else:
            selected_day = ""

        crrt_conference=conf_key.get()
        tracks = crrt_conference.track_options()

        submissions = {}
        for t in tracks:
            submissions[t] = submissionrecord.retrieve_conference_submissions_by_track_round_and_decision(
                                conf_key, t, 2, "Accept")

        self.write_page('schedule_lib/schedulepage.html',
                        { "sched": sched.get(),
                          "selectedDay": selected_day,
                          "conf_tracks": tracks,
                          "submissions": submissions,
                          "crrt_conference": crrt_conference,
                          })
