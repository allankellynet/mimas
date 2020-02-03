#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# submissionopts.py - Submission Options
# Built for custom reports

# System imports

# Google imports

# Local imports
from submission_lib import submissionrecord

def write_created(sub):
    return str(sub.created)

def write_gdpr(sub):
    return str(sub.gdpr_agreed_flag)

def write_track(sub):
    return sub.key.parent().get().track_options()[sub.track]

def write_duration(sub):
    return sub.key.parent().get().duration_options()[sub.duration]

#                      Key -> ("Description", writer_func)
submission_options = {"created": ("Date and time created", write_created),
                      "track": ("Track", write_track),
                      "format": ("Format", None),
                      "decision": ("Decision", None),
                      "final_decision": ("Final decision", None),
                      "grdp_agreed": ("Agreed GDPR policy", write_gdpr),
                      "duration": ("Length", write_duration),
                      }
