#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from scaffold import attentionpage
import basehandler
from submission_lib import submissionrecord, submissions_aux
from reports import status_descriptions

class ExpenseReportPage(basehandler.BaseHandler):

    def get(self):
        conf = ndb.Key(urlsafe=self.request.get("conf")).get()

        if not conf.pays_expenses():
            attentionpage.redirect_attention(self, "DoesNotPayExpenses")
            return

        if self.request.params.has_key("status"):
            filter_key = self.request.params.get("status")

        else:
            filter_key = "All"

        submissions = self.retrieve_submissions(conf.key, filter_key)

        expenses = submissions_aux.expenses_summary(submissions)

        template_values = {
            "conference": conf,
            "expense_categories": expenses,
            "filter_key": filter_key,
            "description": status_descriptions.status_description_map[filter_key],
        }

        self.write_page('reports/expensereportpage.html', template_values)

    def retrieve_submissions(self, conference_key, filter):
        submissions = submissionrecord.retrieve_conference_submissions(conference_key)

        if (filter == "NoDecision"):
            return submissions_aux.filter_by_final_decision("No decision", submissions)
        if (filter == "AcceptAll"):
            return submissions_aux.filter_by_final_decision("Accept", submissions)

        return submissions
