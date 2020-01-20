#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system import

import logging

from google.appengine.ext import ndb

# library imports
import basehandler
# local imports
import reports.commentreport


class CommentReviewPage(basehandler.BaseHandler):
    def get(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf"))

        template_values = {
            "conf_key": conf_key.urlsafe(),
            "comment_report": reports.commentreport.retrieve_commented_report(conf_key),
        }

        self.write_page("subreview_lib/commentreviewpage.html", template_values)

    def post(self):
        if self.request.get("generatecommentreprt"):
            self.gen_comment_report(ndb.Key(urlsafe=self.request.get("conf_key")))
        if self.request.get("deleteChosen"):
            self.delete_comments()

    def gen_comment_report(self, conf_key):
        reports.commentreport.make_comment_report(conf_key)
        self.redirect("/commentreviewpage?conf=" + conf_key.urlsafe())

    def get_all_checked(self):
        checked = self.request.get_all("chosen")
        vote_keys = []
        logging.info("For......")
        logging.info("Checked = " + str(checked))
        for c in checked:
            logging.info("Round the loop....")
            vote_keys.append(ndb.Key(urlsafe=c))

        return vote_keys

    def delete_comments(self):
        reports.commentreport.delete_vote_comments(self.get_all_checked())
        # will utlimatelt want to defer this as it could take time
        # same as report generation
        self.gen_comment_report(ndb.Key(urlsafe=self.request.get("conf_key")))

        # so we'll want go to an attention page
        self.redirect("/commentreviewpage?conf=" + self.request.get("conf_key"))
