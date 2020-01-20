#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports

# app imports
from mailmsg import msgtemplate
from scaffold import sysinfo


class ConferenceMsg(msgtemplate.EmailMessageTemplate):
    def set_conference(self, conf):
        self.conference = conf

    def build_subject(self):
        return self.expand_template(self.subject(), self.make_substitutions_map(self.conference))

    def build_message(self):
        return self.expand_template(self.message(), self.make_substitutions_map(self.conference))

    def mark_pending(self, submission):
        # null operation for conference_lib messages
        pass

    def mark_comms(self, submission):
        # null operation for conference_lib messages
        pass

    def mark_comms_fail(self, submission):
        # null operation for conference_lib messages
        pass

class ConferenceCreatedMsg(ConferenceMsg):
    def default_subject_line(self):
        return "%CONFERENCE_NAME% conference created"

    def default_msg(self):
        return "Congratulations! Conference '%CONFERENCE_NAME%' has successfully been created.\n\n" +\
                "If you have any problems or questions please mail us at contact@confreview.com.\n\n" +\
                "allan kelly"

    def to_address(self):
        return self.conference.creator_id

    def from_address(self):
        return "contact@confreview.com"

    def from_name(self):
        return "Mimas conference_lib system"

    def cc_addresses(self, sub_key):
        return ["allankellynet@gmail.com"]

    def bcc_addresses(self, sub_key):
        return None

    def make_substitutions_map(self, sub):
        return ConferenceMsg.make_conf_substitutions_map(self, self.conference)


def make_conference_created_msg(conference):
    msg = ConferenceCreatedMsg()
    msg.set_conference(conference)
    return msg


class ConferenceSpeakerRequestMsg(ConferenceMsg):
    def set_proto_speaker(self, proto):
        self.proto_speaker = proto

    def default_subject_line(self):
        return "Request to submit to %CONFERENCE_NAME%"

    def default_msg(self):
        return "Thank you for your request to speak at '%CONFERENCE_NAME%'.\n\n" +\
                "Please use the link below to make your submission.\n\n" \
                "%CONFERENCE_SPEAKER_REQUEST_URL%\n\n" \
                "You are allowed to make up to %CONFERENCE_MAX_SUBS% submissions.\n\n" +\
                "If you have any problems please contact using %CONFERENCE_NAME%\n\n"

    def to_address(self):
        return self.proto_speaker.email()

    def from_address(self):
        return self.conference.contact_email()

    def from_name(self):
        return self.conference.name

    def cc_addresses(self, sub_key):
        return None

    def bcc_addresses(self, sub_key):
        return None

    def mk_request_url(self):
        return sysinfo.home_url() + "/singlepagesubmission?p=" + self.proto_speaker.key.urlsafe()

    def make_request_substitutions_map(self):
        substitutions = {
            "%CONFERENCE_SPEAKER_REQUEST_URL%"  :   "http://" + self.mk_request_url(),
        }

        return substitutions

    def make_substitutions_map(self, sub):
        substitutes = ConferenceMsg.make_conf_substitutions_map(self, self.conference)
        substitutes.update(self.make_request_substitutions_map())
        return substitutes

def make_speaker_request_msg(conference, proto_speaker):
    msg = ConferenceSpeakerRequestMsg()
    msg.set_conference(conference)
    msg.set_proto_speaker(proto_speaker)
    return msg
