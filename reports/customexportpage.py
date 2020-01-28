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

        report_name=""
        report_record = customexport.CustomExport()
        report_key = None
        if self.request.params.has_key("report"):
            report_name = self.request.get("report")
            report_record = customexport.get_report_by_name(conf_key, report_name)
            report_key = report_record.key

        self.write_page('reports/customexportpage.html', {"conf_key": conf_key,
                                                          "submission_options": submission_options,
                                                          "reports": customexport.list_all_report_names(conf_key),
                                                          "report_name": report_name,
                                                          "rpt_key": report_key.urlsafe(),
                                                          "rpt_subs_options": report_record.submission_options(),
                                                          })
    def post(self):
        if self.request.get("SubmitExport"):
            self.update_report()

    def update_report(self):
        report_name = self.request.get("ExportName")
        if len(report_name) == 0:
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        report = customexport.mk_report(conf_key, report_name).get()
        submission_options = self.request.get_all("SubmissionOption")
        report.replace_submission_options(submission_options)

        self.redirect("/customexport?conf_key=" + conf_key.urlsafe())
