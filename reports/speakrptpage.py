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
import speaker_lib.cospeaker
from submission_lib import submissionrecord, submissions_aux

messages = { "All" : "All submissions",
             "NoDecision": "Submissions with no decision",
             "Accepts": "Accpeted submissions only"}

class SpeakerReportPage(basehandler.BaseHandler):
    def get(self):
        conf = ndb.Key(urlsafe=self.request.get("conf")).get()

        if self.request.params.has_key("f"):
            submissions = self.retrieve_submissions(conf.key, self.request.get("f"))
            msg = self.request.get("f")
        else:
            submissions = submissionrecord.retrieve_conference_submissions(conf.key)
            msg = "All"

        if submissions is not None:
            submission_keys = map(lambda sub: sub.key, submissions)
            submission_cospeakers = speaker_lib.cospeaker.filter_for_cospeakers(submission_keys)
            all_speakers = speaker_lib.cospeaker.count_all_speakers(submission_keys)
        else:
            # deal with null to avoid nasty error message
            submission_cospeakers = {}
            all_speakers = speaker_lib.cospeaker.SpeakerTotals()

        template_values = {
            "conference": conf,
            "speakers_map": submission_cospeakers,
            "conf_tracks": conf.track_options(),
            "speaker_total": all_speakers,
            "sorted_speakers": sorted(all_speakers.speaker_totals),
            "filter_msg": messages[msg],
            "expand_pictures": self.request.params.has_key("expand"),
        }

        self.write_page('reports/speakrptpage.html', template_values)

    def retrieve_submissions(self, conference_key, filter):
        if (filter == "NoDecision"):
            return submissions_aux.retrieve_by_final_decision(conference_key, "No decision")
        if (filter == "Accepts"):
            return submissions_aux.retrieve_by_final_decision(conference_key, "Accept")

