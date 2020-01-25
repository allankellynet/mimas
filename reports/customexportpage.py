#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import basehandler
from reports import customexport
from submission_lib import submissionrecord, submissions_aux

class CustomExportPage(basehandler.BaseHandler):
    def get(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))

        submission_options = {"Track": "track",
                              "Format": "format",
                              "Decision": "decision",
                              "Final decision": "final_decision",
                              }

        self.write_page('reports/customexportpage.html', {"submission_options": submission_options,
                                                          "reports": customexport.list_all_report_names(conf_key),
                                                          })
    def post(self):
        if self.request.get("SubmitExport"):
            self.update_report()

    def update_report(self):
        report_name = self.request.get("ExportName")
        if len(report_name) == 0:
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        customexport.mk_report(conf_key, report_name)
        self.redirect("/customexport?conf_key=" + conf_key.urlsafe())
