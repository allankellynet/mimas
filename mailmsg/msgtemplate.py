#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# system imports
import re

# framework imports
from google.appengine.ext import ndb

# app imports
from scaffold import sysinfo
from submission_lib import submissionnotifynames
from talk_lib import talk


class EmailMessageTemplate(ndb.Model):
    subject_line = ndb.StringProperty()
    template_msg = ndb.TextProperty()

    def __init__(self, *args, **kwargs):
        super(EmailMessageTemplate, self).__init__(*args, **kwargs)
        self.subject_line = None
        self.template_msg = None

    def subject(self):
        if self.subject_line == None:
            return self.default_subject_line()
        else:
            return self.subject_line

    def message(self):
        if self.template_msg == None:
            return self.default_msg()
        else:
            return self.template_msg

    def set_subject_line(self, subject):
        self.subject_line = subject

    def set_message(self, msg):
        self.template_msg = msg

    def expand_template(self, text, substitutions):
        # stolen from https://emilics.com/notebook/enblog/p869.html
        robj = re.compile('|'.join(substitutions.keys()))
        return robj.sub(lambda m: substitutions[m.group(0)], text)

    def make_conf_substitutions_map(self, conf):
        substitutions = {
            "%CONFERENCE_NAME%"  :   conf.name,
            "%CONFERENCE_EMAIL%" :   conf.contact_email(),
            "%CONFERENCE_MAX_SUBS%" : str(conf.max_submissions()),
        }

        return substitutions

    def build_subject(self, sub):
        return self.expand_template(self.subject(), self.make_substitution_map(sub))

    def build_message(self, sub):
        return self.expand_template(self.message(), self.make_substitution_map(sub))

class SubmissionMessageTemplate(EmailMessageTemplate):
    def mk_speaker_edit_url(self, sub):
        url = sysinfo.home_url() + "/speakerupdate?"
        url += "key=" + sub.talk.parent().urlsafe()
        url += "&email=" + sub.email()
        return url

    def mk_feedback_url(self, sub):
        return sysinfo.home_url() + "/review_feedback?k=" + sub.key.urlsafe()

    def mk_acceptdecline_url(self, sub):
        return sysinfo.home_url() + "/acceptance?sub=" + sub.key.urlsafe()

    def make_submission_substitution_map(self, sub, conf):
        substitutions = {
            "%SPEAKER%"          :   sub.submitter(),
            "%SPEAKER_BIO%"      :   sub.talk.parent().get().bio,
            "%SUBMISSION_TITLE%" :   sub.title(),
            "%SHORT_SYNOPSIS%"   :   sub.talk.get().field(talk.SHORT_SYNOPSIS),
            "%LONG_SYNOPSIS%"    :   sub.talk.get().field(talk.LONG_SYNOPSIS),
            "%EDIT_SPEAKER_URL%" :   "http://" + self.mk_speaker_edit_url(sub),
            "%SUB_FEEDBACK_URL%" :   "http://" + self.mk_feedback_url(sub),
            "%ACK_ACCEPT_URL%"   :   "http://" + self.mk_acceptdecline_url(sub),
            }

        if conf.track_options().has_key(sub.track):
            substitutions["%SUBMISSION_TRACK%"] = conf.track_options()[sub.track]

        if conf.delivery_format_options().has_key(sub.delivery_format_text):
            substitutions["%SUBMISSION_FORMAT%"] = conf.delivery_format_options()[sub.delivery_format_text]

        if conf.duration_options().has_key(sub.duration):
            substitutions["%SUBMISSION_DURATION%"] = conf.duration_options()[sub.duration]

        if conf.expenses_options().has_key(sub.expenses):
            substitutions["%SUBMISSION_EXPENSES%"] = conf.expenses_options()[sub.expenses],

        return substitutions

    def make_substitution_map(self, sub):
        conf = sub.key.parent().get()
        substitutes = SubmissionMessageTemplate.make_conf_substitutions_map(self, conf)
        substitutes.update(self.make_submission_substitution_map(sub, conf))
        return substitutes

class AcceptMsg(SubmissionMessageTemplate):
    def default_subject_line(self):
        return "Acceptance to %CONFERENCE_NAME%"

    def default_msg(self):
        return "Your submission has been accepted." \
                + "\nPlease use this link to confirm you will be able to attend and speak:" \
                + "\n%ACK_ACCEPT_URL%"

    def cc_addresses(self, sub_key):
        # TODO Change these to pass on conference key not submission key
        addresses = sub_key.parent().get().accept_cc_addresses().values()
        if addresses is not None:
            if len(addresses)==0:
                addresses = None

        return addresses

    def bcc_addresses(self, sub_key):
        return None

    def mark_pending(self, sub):
        sub.mark_acccept_pending()

    def mark_comms(self, sub):
        sub.mark_acccept()

    def mark_comms_fail(self, sub):
        sub.mark_comms(submissionnotifynames.SUBMISSION_FAILED_ACCEPT_NOTIFICATON)

class DeclineMsg(SubmissionMessageTemplate):
    def default_subject_line(self):
        return "Notification from %CONFERENCE_NAME%"

    def default_msg(self):
        return "We are sorry to inform you that you submission has been declined."

    def cc_addresses(self, sub_key):
        return None

    def bcc_addresses(self, sub_key):
        return None

    def mark_pending(self, sub):
        sub.mark_declined()

    def mark_comms(self, sub):
        sub.mark_comms(submissionnotifynames.SUBMISSION_DECLINED)

    def mark_comms_fail(self, sub):
        sub.mark_comms(submissionnotifynames.SUBMISSION_FAILED_DECLINE_NOTIFICATION)

class AcknowledgeMsg(SubmissionMessageTemplate):
    def default_subject_line(self):
        return "Submission acknowledgement: %CONFERENCE_NAME%"

    def default_msg(self):
        # For some reason "Expenses: %SUBMISSION_EXPENSES\n" in here causes a fail
        # in the regex substitution
        return "Confirm '%SUBMISSION_TITLE%' has been received by %CONFERENCE_NAME%." + \
                "\n\n" + \
                "In the meantime if you have any question please contact us on %CONFERENCE_EMAIL%." +\
                "\n\n" +\
                "...................................................................\n\n" + \
                "Title: %SUBMISSION_TITLE%\n\n" + \
                "Track: %SUBMISSION_TRACK%\n\n" + \
                "Format: %SUBMISSION_FORMAT%\n\n" + \
                "Duration: %SUBMISSION_DURATION%\n\n" + \
                "Speaker bio: %SPEAKER_BIO%\n\n" + \
                "Short synopsis: %SHORT_SYNOPSIS%\n\n" + \
                "Long synopsis: %LONG_SYNOPSIS%\n\n"

    def cc_addresses(self, sub_key):
        addresses = sub_key.parent().get().ack_cc_addresses().values()
        if addresses is not None:
            if len(addresses)==0:
                addresses = None

        return addresses

    def bcc_addresses(self, sub_key):
        addresses = sub_key.parent().get().ack_bcc_addresses().values()
        if addresses is not None:
            if len(addresses)==0:
                addresses = None

        return addresses

    def mark_pending(self, sub):
        sub.mark_comms(submissionnotifynames.SUBMISSION_PENDING_ACKNOWLEDGE)

    def mark_comms(self, sub):
        sub.mark_comms(submissionnotifynames.SUBMISSION_ACKNOWLEDGED)

    def mark_comms_fail(self, sub):
        sub.mark_comms(submissionnotifynames.SUBMISSION_FAILED_ACKNOWLEDGE)


class CoSpeakerBioRequestMsg(SubmissionMessageTemplate):
    def default_subject_line(self):
        return "Cospeaker inclusion: %CONFERENCE_NAME%"

    def default_msg(self):
        return "Hello,\n\n" \
                "You have been included on a submission to %CONFERENCE_NAME%.\n\n" + \
                "The submission was made by %SPEAKER% and was titled: '%SUBMISSION_TITLE%'.\n\n" + \
                "We have no biography on file for you so could you complete one please?\n\n" + \
                "The link below will take you to a page where you can submit your details.\n\n" + \
                "If your e-mail address has been included by mistake please contact the conference team (%CONFERENCE_EMAIL%) and who will, of course, remove your name from the submission.\n\n" + \
                "Thanks\n\n" + \
                "%COSPEAKER_BIO_URL%\n\n" + \
                "...................................................................\n"

    def cc_addresses(self, sub_key):
        return [ sub_key.get().email() ]

    def bcc_addresses(self, sub_key):
        return None

    def mark_pending(self, sub):
        pass

    def mark_comms(self, sub):
        pass

    def mark_comms_fail(self, sub):
        pass

    def set_from_name_and_address(self, name, email):
        self.sender_name = name
        self.sender_email = email

    def from_name(self):
        return self.sender_name

    def from_address(self):
        return self.sender_email

    def set_to_address(self, email):
        self.cospeaker_email = email

    def to_address(self):
        return self.cospeaker_email

    def set_cospeaker(self, cospeak_key):
        self.co_speaker_key = cospeak_key

    def mk_request_url(self):
        return sysinfo.home_url() + "/cospeakerpage?cospeaker=" + self.co_speaker_key.urlsafe()

    def make_cospeaker_substitutions_map(self):
        substitutions = {
            "%COSPEAKER_BIO_URL%"  :   "http://" + self.mk_request_url(),
        }

        return substitutions

    def make_substitution_map(self, sub):
        substitutes = SubmissionMessageTemplate.make_substitution_map(self, sub)
        substitutes.update(self.make_cospeaker_substitutions_map())
        return substitutes


class CoSpeakerBioExistsMsg(CoSpeakerBioRequestMsg):
    def default_msg(self):
        return "Hello,\n\n" \
                "You have been included on a submission to %CONFERENCE_NAME%.\n\n" + \
                "The submission was made by %SPEAKER% and was titled: '%SUBMISSION_TITLE%'.\n\n" + \
                "We already have you biography on file so there is nothing else you need to do.\n\n" + \
                "If you would like to change or update you bio then please use the link below.\n\n" + \
                "If your e-mail address has been included by mistake please contact the conference team (%CONFERENCE_EMAIL%) and who will, of course, remove your name from the submission.\n" + \
                "Thanks\n\n" + \
               "%COSPEAKER_BIO_URL%\n\n" + \
               "...................................................................\n"

def retrieveTemplate(msgType, conf_key):
    templates = msgType.query(ancestor=conf_key).fetch(1)
    if len(templates)>0:
        template = templates[0]
    else:
        template = msgType(parent=conf_key)

    return template

