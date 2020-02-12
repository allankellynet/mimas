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
from scaffold import userrights, userrightsnames, sorrypage
from submission_lib import submissionrecord
from schedule_lib import schedule

class SchedulePage(basehandler.BaseHandler):
    def get(self):
        crrt_conference=self.get_crrt_conference_key().get()

        if (crrt_conference.is_reviewing_compete):
            if crrt_conference.user_rights().has_permission(self.get_crrt_user().email(),
                                                            userrightsnames.CONF_SCHEDULE):
                self.show_schedule_page(crrt_conference)
            else:
                sorrypage.redirect_sorry(self, "NoSchedulingPerissoms")
        else:
            sorrypage.redirect_sorry(self, "NoSchedulingAtThisTime")

    def show_schedule_page(self, crrt_conference):
        if self.request.params.has_key("day"):
            selected_day = self.request.get("day")
        else:
            selected_day = ""

        tracks = crrt_conference.track_options()

        submissions = {}
        for t in tracks:
            submissions[t] = submissionrecord.retrieve_conference_submissions_by_track_round_and_decision(
                                crrt_conference.key, t, 2, "Accept")

        self.write_page('schedule_lib/schedulepage.html',
                        { "sched": schedule.get_conference_schedule(crrt_conference.key).get(),
                          "selectedDay": selected_day,
                          "conf_tracks": tracks,
                          "submissions": submissions,
                          "crrt_conference": crrt_conference,
                          })
