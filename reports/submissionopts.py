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
from speaker_lib import speaker, cospeaker
from scaffold import sysinfo

def write_str(s):
    return str(s)

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
    # talk details
    "title": ("Talk title",
        lambda sub:(sub.talk.get().title)),
    "short_synopsis": ("Short synopsis",
        lambda sub: (sub.talk.get().field("shortsynopsis"))),
    "long_synopsis": ("Long synopsis",
        lambda sub: (sub.talk.get().field("longsynopsis"))),
    # speaker details
    "email": ("Email",
        lambda sub: (sub.talk.parent().get().email)),
    "first_name": ("First name",
        lambda sub: (sub.talk.parent().get().first_name())),
    "last_name": ("Later names",
        lambda sub: (sub.talk.parent().get().later_names())),
    "bio": ("Biography",
        lambda sub: (sub.talk.parent().get().bio)),
    "picture": ("Picture",
        lambda sub: write_str("https://" + sysinfo.home_url() + sub.talk.parent().get().full_image_url())),
    "webpage": ("Webpage",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_WEBPAGE))),
    "blog": ("Blog",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_BLOG))),
    "linkedin": ("Linkedin",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_LINKEDIN))),
    "country": ("Country",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_COUNTRY))),
    "twitter": ("Twitter",
        lambda sub: "https://twitter.com/" + (sub.talk.parent().get().field(speaker.Speaker.FIELD_TWITTER))),
    "affiliation": ("Affiliation",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_AFFILICATION))),
    "telephone": ("Telephone",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_TELEPHONE))),
    "address": ("Address",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_ADDRESS))),
    "jobtitle": ("JobTitle",
        lambda sub: (sub.talk.parent().get().field(speaker.Speaker.FIELD_JOBTITLE))),
    "cospeakers": ("Co-speakers",
        lambda sub: write_str(cospeaker.get_pretty_list(sub.key))),
}
