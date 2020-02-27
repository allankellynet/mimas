#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedulepage.py
#

# System imports
from datetime import datetime, time

# Google imports
import logging
from google.appengine.ext import ndb

# Local imports
import basehandler
from conference_lib import conference
from scaffold import userrights, userrightsnames, sorrypage
from submission_lib import submissionrecord, submissions_aux
from schedule_lib import schedule, schedelement, schedexport
from reports import reportrecord

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

    def remove_scheduled(self, accepted, scheduled):
        for sched in scheduled:
            sched_key = ndb.Key(urlsafe = sched)
            for i in range(0, len(accepted)):
                if accepted[i].key == sched_key:
                    del accepted[i]
                    break

        return accepted

    def show_schedule_page(self, crrt_conference):
        sched = schedule.get_conference_schedule(crrt_conference.key).get()
        accepted_subs = submissions_aux.retrieve_by_final_decision_track_ordered(crrt_conference.key, "Accept")
        submissions = self.remove_scheduled(accepted_subs, sched.get_assigned_submissions())

        tracks = crrt_conference.track_options()
        self.write_page('schedule_lib/schedulepage.html',
                        { "sched": sched,
                          "selectedDay": self.selectedDay(),
                          "conf_tracks": tracks,
                          "track_count": len(tracks),
                          "elements": schedelement.retreieve_elements(sched.key),
                          "submissions": submissions,
                          "crrt_conference": crrt_conference,
                          "talkTitle": talkTitle,
                          })

    def selectedDay(self):
        if self.request.params.has_key("day"):
            selected_day = self.request.get("day")
        else:
            selected_day = ""
        return selected_day

    def mkExport(self):
        url = schedexport.schedule_to_excel(schedule.get_conference_schedule(self.get_crrt_conference_key()))
        rpt_key = reportrecord.mk_report_record(self.retrieve_conf_key(), "Schedule", url)
        self.redirect("/exportspage?newrpt=" + rpt_key.urlsafe())

    def post(self):
        if self.request.get("exportExcel"):
            self.mkExport()
            return

        if self.request.get("scheduleTalk"):
            self.scheduleTalk()
        if self.request.get("deschedule"):
            self.deScheduleTalk()

        self.redirect("/schedulepage?day="+self.selectedDay())

    def scheduleTalk(self):
        day = self.request.get("daysList")
        track = self.request.get("selectedSlotTrack")
        slot = datetime.strptime(self.request.get("selectedSlot"),"%H:%M:%S").time()
        sub_key = self.request.get("selectedTalkKey")

        schedule.get_conference_schedule(self.get_crrt_conference_key()).get().assign_talk(sub_key, day, track, slot)

    def deScheduleTalk(self):
        day = self.request.get("daysList")
        track = self.request.get("selectedSlotTrack")
        slot = datetime.strptime(self.request.get("selectedSlot"),"%H:%M:%S").time()
        schedule.get_conference_schedule(self.get_crrt_conference_key()).get().clear_talk(day, track, slot)

def talkTitle(safeKey):
    if safeKey=="Empty":
        return "Empty"

    sub = ndb.Key(urlsafe=safeKey).get()
    return sub.title()