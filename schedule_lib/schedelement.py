#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# scheduleelement.py
#

# System imports
import datetime

# Google imports
import logging
from google.appengine.ext import ndb

# Local imports

class ScheduleElement(ndb.Model):
    title_db = ndb.StringProperty()

    def title(self):
        return self.title_db

def mk_element(sched_key, title):
    element = ScheduleElement(parent=sched_key)
    element.title_db = title
    return element.put()

def retreieve_elements(sched_key):
    return ScheduleElement.query(ancestor=sched_key).fetch()
