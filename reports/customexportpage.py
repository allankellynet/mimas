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


class CustomExportPage(basehandler.BaseHandler):
    def get(self):
        conf = ndb.Key(urlsafe=self.request.get("conf_key")).get()

        self.write_page('reports/customexportpage.html', {})
