#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import logging

# Local imports
import basehandler
from speaker_lib import speaker_checks
from submission_lib import submissions_aux, submissionrecord, submissionnotifynames


class MasterControlPage(basehandler.BaseHandler):
    def check_blank_bios(self):
        msg = "<h1>Blank bio report</h1>"
        blank_list = speaker_checks.find_blank_bio_submissions(self.get_crrt_conference_key())
        msg += "<p>Conference: " + self.get_crrt_conference_key().get().name
        msg += "<p>Speakers with a blank bio: " + str(len(blank_list))

        msg += "\n<p><table><th>Name<th>email<th>Created"
        for blank in blank_list:
            msg += "\n<tr><td>" + blank.name + "<td>" + blank.email + "<td>" + blank.created_date.isoformat()

        msg += "\n</table>"

        self.response.write(msg)

    def change_submission_communication(self):
        conf_key = self.get_crrt_conference_key()
        submissions = submissionrecord.retrieve_conference_submissions(conf_key)
        for sub in submissions:
            logging.info("Change subs comms:" + sub.communication + ";" + submissionnotifynames.SUBMISSION_ACCEPT_ACKNOWLEDGED + ".")
            if sub.communication == submissionnotifynames.SUBMISSION_ACCEPT_ACKNOWLEDGED:
                sub.acknowledge_receipt()

        self.response.write("Done: submission comms updated")

    def fix_expenses(self, criteria, new_value):
        conf_key = self.get_crrt_conference_key()
        submissions_aux.change_all_expenses(conf_key, criteria, new_value)
        self.response.write("Done: " + criteria + " -> " + new_value)

    def get(self):
        template_values = {
        }

        self.write_page("scaffold/masterpage.html", template_values)

    def post(self):
        if self.request.get("BlankBio"):
            self.check_blank_bios()
        if self.request.get("ShortHaul"):
            self.fix_expenses("Option9", "Option15")
        if self.request.get("LongHaul"):
            self.fix_expenses("Option8", "Option16")
        if self.request.get("AckReceipt"):
            self.change_submission_communication()


