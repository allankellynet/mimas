#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
from submission_lib import submissionrecord

def write_created(sub):
    return str(sub.created)

def write_gdpr(sub):
    return str(sub.gdpr_agreed_flag)

submission_options = {"created": ("Date and time created", write_created),
                      "track": ("Track", None),
                      "format": ("Format", None),
                      "decision": ("Decision", None),
                      "final_decision": ("Final decision", None),
                      "grdp_agreed": ("Agreed GDPR policy", write_gdpr),
                      }
