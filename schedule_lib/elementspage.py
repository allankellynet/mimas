#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# elementspage.py
#

# System imports
from datetime import datetime, time

# Google imports
import logging
from google.appengine.ext import ndb

# Local imports
import basehandler
from schedule_lib import schedule, schedelement

class ElementsPage(basehandler.BaseHandler):
    def get(self):
        conf_key=self.get_crrt_conference_key()

        self.write_page('schedule_lib/elementspage.html', {
                        "elements" : schedelement.retreieve_elements(schedule.get_conference_schedule(conf_key)),
        })

    def post(self):
        if self.request.get("commonElements"):
            self.addCommonElements()

        if self.request.get("addNewElement"):
            self.addNewElement()

        if self.request.get("deleteElements"):
            self.removeElements()

        self.redirect("/elementspage")

    def addCommonElements(self):
        sched_key = schedule.get_conference_schedule(self.get_crrt_conference_key())
        schedelement.mk_element(sched_key, "Coffee")
        schedelement.mk_element(sched_key, "Lunch")

    def addNewElement(self):
        schedelement.mk_element(schedule.get_conference_schedule(self.get_crrt_conference_key()),
                                self.request.get("newElement"))

    def removeElements(self):
        sched_key = schedule.get_conference_schedule(self.get_crrt_conference_key())

        for safe_key in self.request.get_all("elementSelect"):
            key = ndb.Key(urlsafe=safe_key)
            key.delete()
