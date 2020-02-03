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

def write_str(flag):
    return str(flag)

def write_decision(sub, review_round):
    return sub.review_decision(review_round)

def write_option(option_list, opt):
    return option_list[opt]

#  Key -> ("Description", writer_func)
submission_options = {
    "created": ("Date and time created",
        lambda sub:write_str(sub.created)),
    "track": ("Track",
        lambda sub:write_option(sub.key.parent().get().track_options(), sub.track)),
    "format": ("Format",
        lambda sub:write_option(sub.key.parent().get().delivery_format_options(), sub.delivery_format)),
    "decision1": ("Decision round 1",
        lambda sub:write_decision(sub, 1)),
    "decision2": ("Decision round 2",
        lambda sub:write_decision(sub, 2)),
    "duration": ("Length",
        lambda sub:write_option(sub.key.parent().get().duration_options(), sub.duration)),
    "speaker_comms": ("Communication",
        lambda sub:write_str(sub.communication)),
    "expenses": ("Expenses",
        lambda sub:write_option(sub.key.parent().get().expenses_options(), sub.expenses)),
    "withdrawn": ("Withdrawn",
        lambda sub:write_str(sub.withdrawn)),
    "grdp_agreed": ("Agreed GDPR policy",
        lambda sub:write_str(sub.gdpr_agreed_flag)),
    }
