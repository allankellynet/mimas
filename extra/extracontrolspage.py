#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# System imports
import sys

# Google imports
import logging

# Local imports
import basehandler
from speaker_lib import cospeaker, speaker

class ExtraControlsPage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.get_crrt_conference_key()

        template_values = {
            "conference": conf_key.get(),
        }

        self.write_page('extra/extracontrolspage.html', template_values)

    def post(self):
        if self.request.get("LowerCaseCoSpeakers"):
            logging.info("+++++ Co speaker email addresses to lowercase +++++")
            cospeaker.make_db_emails_lower_case()
            self.redirect("/")

        if self.request.get("CheckDuplicateSpeakers"):
            self.check_dup_speakers()

        if self.request.get("DuplicateSpeakersTalks"):
            self.redirect("/extraspeakertalks")

    def check_dup_speakers(self):
        sys.setrecursionlimit(9999)
        duplicates = speaker.find_duplicate_speakers()
        self.response.out.write("Duplicate speakers list across all conferences:")
        for sp in duplicates:
            self.response.out.write("<p>" + sp.email)
        self.response.out.write("<p>List ends.")
