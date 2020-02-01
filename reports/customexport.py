#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
import datetime

# framework imports
from google.appengine.ext import ndb
import cloudstorage
import xlsxwriter

# app imports
import exportexcel, submissionopts

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

    def write_title_row(self, worksheet):
        column = 1
        for opt in self.submission_options_db:
            worksheet_write_wrapper(worksheet, 1, column, opt)
            column = column + 1

    def write_submissions_list(self, wks, submissions):
        row = 2
        for sub in submissions:
            column = 1
            for opt in self.submission_options_db:
                self.write_submission_field(opt, sub, wks, row, column)
                column = column +1

    def export_submissions_to_excel(self, submission_keys):
        fullname, url = exportexcel.mk_filename(self.report_name_db, datetime.datetime.now())
        with cloudstorage.open(fullname, "w",
                           content_type="text/plain; charset=utf-8",
                           options={'x-goog-acl': 'public-read'}) as output:
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet()
            self.write_title_row(worksheet)
            self.write_submissions_list(worksheet, submission_keys)
            workbook.close()

        output.close()
        return url

    def write_submission_field(self, opt, sub, wks, row, column):
        worksheet_write_wrapper(wks, row, column,
                                submissionopts.submission_options[opt][1](sub.get()))


def worksheet_write_wrapper(wksheet, row, col, text):
    wksheet.write(row, col, text)

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

