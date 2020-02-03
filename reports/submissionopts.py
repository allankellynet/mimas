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

def write_boolean(flag):
    return str(flag)

def write_track(sub):
    return sub.key.parent().get().track_options()[sub.track]

def write_duration(sub):
    return sub.key.parent().get().duration_options()[sub.duration]

def write_decision(sub, review_round):
    return sub.review_decision(review_round)

def write_format(sub):
    return sub.key.parent().get().delivery_format_options()[sub.delivery_format]

def write_expenses(sub):
    return sub.key.parent().get().expenses_options()[sub.expenses]

def write_option(sub, option_list, opt):
    return option_list[opt]

def write_comms(sub):
    return sub.communication

#                      Key -> ("Description", writer_func)
submission_options = {
    "created": ("Date and time created", write_created),
    "track": ("Track", write_track),
    "format": ("Format", write_format),
    "decision1": ("Decision round 1", lambda sub:write_decision(sub, 1)),
    "decision2": ("Decision round 2", lambda sub:write_decision(sub, 2)),
    "duration": ("Length", write_duration),
    "speaker_comms": ("Communication", write_comms),
    "expenses": ("Expenses",
                lambda sub:write_option(sub, sub.key.parent().get().expenses_options(), sub.expenses)),
    "withdrawn": ("Withdrawn", lambda sub:write_boolean(sub.withdrawn)),
    "grdp_agreed": ("Agreed GDPR policy", lambda sub:write_boolean(sub.gdpr_agreed_flag)),
    }
