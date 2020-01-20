#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
import msgtemplate


class CustomMsg(msgtemplate.SubmissionMessageTemplate):
    msg_name = ndb.StringProperty()

    def __init__(self, *args, **kwargs):
        super(CustomMsg, self).__init__(*args, **kwargs)
        self.msg_name = ""

    def set_name(self, name):
        self.msg_name = name

    def name(self):
        return self.msg_name

    def default_subject_line(self):
        return ""

    def default_msg(self):
        return ""

    def cc_addresses(self, sub_key):
        return None

    def bcc_addresses(self, sub_key):
        return None

    def mark_pending(self, submission):
        # null operation for custom messages
        pass

    def mark_comms(self, submission):
        # null operation for custom messages
        pass

    def mark_comms_fail(self, submission):
        # null operation for custom messages
        pass

def make_custom_msg(conf_parent_key, name, subject, message):
    msg = CustomMsg(parent=conf_parent_key)
    msg.set_name(name)
    msg.set_subject_line(subject)
    msg.set_message(message)
    return msg.put()

def retrieve_custom_message(conf_parent_key):
    return CustomMsg.query(ancestor=conf_parent_key).fetch()
