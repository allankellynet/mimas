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
from submission_lib import submissions_aux
from reports import status_descriptions

class ExpenseListPage(basehandler.BaseHandler):
    def get(self):
        conf = ndb.Key(urlsafe=self.request.get("conf")).get()

        if not conf.pays_expenses():
            attentionpage.redirect_attention(self, "DoesNotPayExpenses")
            return

        if self.request.params.has_key("expenses"):
            expenses_filter = self.request.get("expenses")
            exp_filter_description = conf.expenses_options()[expenses_filter]

        submissions = submissions_aux.retrieve_submissions_by_expenses(conf.key, expenses_filter)

        if self.request.params.has_key("status"):
            status_filter = self.request.get("status")
        else:
            status_filter = "All"

        status_description = status_descriptions.status_description_map[status_filter]

        if status_filter != "All":
            submissions = submissions_aux.filter_by_final_decision(status_description, submissions)

        template_values = {
            "conference": conf,
            "expenses_filter": expenses_filter,
            "expenses_description": exp_filter_description,
            "status_filter": status_filter,
            "status_description": status_description,
            "submissions": submissions,
            "submissions_count": len(submissions),
            "expenses_options": conf.expenses_options(),
        }

        self.write_page('reports/expenseslistpage.html', template_values)
