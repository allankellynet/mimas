#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports

class CustomExport(ndb.Model):
    report_name_db = ndb.StringProperty()
    submission_options_db = ndb.StringProperty(repeated=True)

    def report_name(self):
        return self.report_name_db

    def set_name(self, new_name):
        self.report_name_db = new_name
        self.put()

    def delete_report(self):
        self.key.delete()

    def submission_options(self):
        return self.submission_options_db

    def add_submission_options(self, option_list):
        self.submission_options_db.extend(option_list)
        self.put()

    def replace_submission_options(self, options):
        self.submission_options_db = options
        self.put()

def list_all_report_names(conf_key):
    # Did want to use a projection query here but
    # not for the first time projection query doesn't work
    # - return the whole object
    # reports = CustomExport.query(ancestor=conf_key).fetch(projection=[CustomExport.report_name_db])
    #
    # so until I work out what is going on...
    # get the whole thing and split out the name
    return map(lambda r: r.report_name_db, CustomExport.query(ancestor=conf_key).fetch())

def get_report_by_name(conf_key, report_name):
    reports = CustomExport.query(ancestor=conf_key).filter(CustomExport.report_name_db==report_name).fetch()
    if len(reports) == 0:
        return None

    return reports[0]

def mk_report(conf_key, report_name):
    rpt = CustomExport(parent=conf_key)
    rpt.report_name_db = report_name
    rpt.put()
    return rpt.key
