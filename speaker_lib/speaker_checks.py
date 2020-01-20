#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
from speaker import Speaker
from submission_lib import submissionrecord

def is_bio_blank(spk):
    return spk.bio == ""

def filter_for_blank_bios(speakers):
    rlst = []
    for speaker in speakers:
        if speaker.bio == "":
            rlst.append(speaker)

    return rlst

def find_blank_bio_submissions(conf_key):
    submissions = submissionrecord.retrieve_conference_submissions(conf_key)
    speakers = map(lambda sub: sub.talk.parent().get(), submissions)
    return filter_for_blank_bios(speakers)
