#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
import datetime

# framework imports
from google.appengine.ext import ndb

# app imports

def patchable_now_time():
    return datetime.datetime.now()

class ReportRecord(ndb.Model):
    created_db = ndb.DateTimeProperty()
    name_db = ndb.StringProperty()
    url_db = ndb.StringProperty()

    def __init__(self, *args, **kwargs):
        super(ReportRecord, self).__init__(*args, **kwargs)
        self.created_db = patchable_now_time()
        self.name_db = ""
        self.url_db = ""

def mk_report_record(conf_key, name, url):
    new_record = ReportRecord(parent=conf_key)
    new_record.name_db = name
    new_record.url_db = url
    new_record.put()
    return new_record.key

def retrieve_reports_newest_to_oldset(conf_key):
    return ReportRecord.query(ancestor=conf_key).order(-ReportRecord.created_db).fetch()
