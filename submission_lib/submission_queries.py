#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Application imports

# Local imports
import submissionrecord
from submissionrecord import retrieve_conference_submissions


def is_submitted(conf_key, speaker_email, talk_title):
    for s in submissionrecord.retrieve_conference_submissions(conf_key):
        if speaker_email == s.email():
            if talk_title == s.title():
                return True

    return False


def count_submissions(conf_key, speaker_key):
    subs = retrieve_conference_submissions(conf_key)
    count = 0
    for s in subs:
        if s.talk.parent() == speaker_key:
            count = count + 1

    return count