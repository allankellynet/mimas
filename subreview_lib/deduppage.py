#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import logging

from google.appengine.ext import deferred
from google.appengine.ext import ndb

# Local imports
import dedupvotes
# Local imports
from scaffold import sorrypage, attentionpage
import basehandler


def start_generate(conf_key, vote_round):
    logging.info("Start generate called ------------------")
    dedupvotes.generate_duplicate_vote_report(ndb.Key(urlsafe=conf_key), vote_round)

class DedupPage(basehandler.BaseHandler):
    def get(self):
        if not(self.request.params.has_key("conf")):
            sorrypage.redirect_sorry(self, "ConfKeyMissing")
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        report = dedupvotes.retrieve_duplicate_report(conf_key)

        template_values = {
            "crrt_conf": conference,
            "has_report": not(report==None),
            "report": report,
        }

        self.write_page('subreview_lib/deduppage.html', template_values)

    def post(self):
        if self.request.get("GenerateReport1"):
            deferred.defer(start_generate, self.request.get("conf_key"), 1)
            attentionpage.redirect_attention(self, "GeneratingVoteReport")
        if self.request.get("ActionReport"):
            self.run_dedup()
            attentionpage.redirect_attention(self, "DeDuplicateRunning")

    def run_dedup(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        report = dedupvotes.retrieve_duplicate_report(conf_key)
        if (report != None):
            deferred.defer(dedupvotes.remove_duplicates, report.duplicates)

