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
from conference_lib import confstate


class ConferencePage(basehandler.BaseHandler):
    def get(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf"))

        template_values = {
            "conference": conf_key.get(),
            "conf_key": conf_key,
        }

        self.write_page('conference_lib/confstatepage.html', template_values)

    def post(self):
        safe_key = self.request.get("safe_key")
        conference = ndb.Key(urlsafe=safe_key).get()

        this_page = "/confstate_page?conf="+safe_key

        if self.request.get("OpenSubmissions"):
            conference.open_for_submissions()
            self.redirect(this_page)
        elif self.request.get("CloseSubmissions"):
            conference.close_submissions()
            self.redirect(this_page)
        elif self.request.get("Round1Review"):
            conference.start_round1_reviews()
            self.redirect(this_page)
        elif self.request.get("Round2Review"):
            self.close_round1_and_advance(conference, this_page)
        elif self.request.get("CloseRound2"):
            self.close_round2(conference, this_page)
        elif self.request.get("HideComments"):
            conference.hide_comments()
            self.redirect(this_page)
        elif self.request.get("ShowComments"):
            conference.show_comments()
            self.redirect(this_page)


    def close_round1_and_advance(self, conf, this_page):
        if not (confstate.can_close_conference(conf.key, 1)):
            self.redirect("/sorry_page?reason=CannotCloseR1")
        else:
            confstate.close_round1_and_open_round2(conf)
            self.redirect(this_page)

    def close_round2(self, conf, this_page):
        if not(confstate.can_close_conference(conf.key, 2)):
            self.redirect("/sorry_page?reason=CannotClose")
        else:
            conf.finish_reviews()
            self.redirect(this_page)
