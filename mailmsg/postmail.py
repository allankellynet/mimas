#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# System imports
# App Engine imports
import logging
import os
import urllib2

import sendgrid
from google.appengine.ext import deferred

from mailmsg import msgtemplate
# Local imports
from scaffold import sysinfo


def ack_submission(submission, conf_key):
    ack_msg = msgtemplate.retrieveTemplate(msgtemplate.AcknowledgeMsg, conf_key)

    Postman().post_one(conf_key.get(), ack_msg, submission.key)

def massage_none_list(lst):
    if lst is None:
        return []
    else:
        return lst

class Postman:
    def __init__(self, *args, **kwargs):
        self.sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

    def post_many(self, conference, msg, submissions, send_gap_seconds=10):
        i = 0
        # 4 Feb 2018
        # Changed as per post_many_by_key to remove use of defer
        for s in submissions:
            self.post_one(conference, msg, s.key)
            msg.mark_pending(s)
            i += 1

    def post_many_by_key(self, conference, msg, sub_keys, send_gap_seconds=10):
        i = 0
        # 11 December 2017
        # Removed defer sending, it was a remenent from before switching to sendgrid
        # And today defer started hitting a pickle error
        # So implest fix is to remove defer element... still a bit nervous...
        for s in sub_keys:
            msg.mark_pending(s)
            self.post_one(conference, msg, s)
            i += 1

    def post_one(self, conference, msg, submission_key):
        submission = submission_key.get()
        mail = sendgrid.helpers.mail.Mail(
                    sendgrid.helpers.mail.Email(conference.contact_email(), conference.name),
                    msg.build_subject(submission),
                    sendgrid.helpers.mail.Email(submission.talk.get().key.parent().get().email),
                    sendgrid.helpers.mail.Content("text/plain", msg.build_message(submission)))

        for cc in massage_none_list(msg.cc_addresses(submission_key)):
            mail.personalizations[0].add_cc(sendgrid.helpers.mail.Email(cc))

        for bcc in massage_none_list(msg.bcc_addresses(submission_key)):
            mail.personalizations[0].add_bcc(sendgrid.helpers.mail.Email(bcc))

        logging.info("Mail sending to: " +
                         submission.talk.get().key.parent().get().email)

        self.do_send(mail, msg, submission)

    # post_addressed_one and post_one should be the same function
    # all msgs should have from and to fields so post_one can merge into post_addressed_one
    def post_addressed_one(self, conference, msg, submission_key):
        submission = submission_key.get()
        mail = sendgrid.helpers.mail.Mail(
                    sendgrid.helpers.mail.Email(msg.from_address(), msg.from_name()),
                    msg.build_subject(submission),
                    sendgrid.helpers.mail.Email(msg.to_address()),
                    sendgrid.helpers.mail.Content("text/plain", msg.build_message(submission)))

        for cc in massage_none_list(msg.cc_addresses(submission_key)):
            mail.personalizations[0].add_cc(sendgrid.helpers.mail.Email(cc))

        for bcc in massage_none_list(msg.bcc_addresses(submission_key)):
            mail.personalizations[0].add_bcc(sendgrid.helpers.mail.Email(bcc))

        if sysinfo.is_running_local():
            logging.info("Mail sending to: " +
                         submission.talk.get().key.parent().get().email)

        self.do_send(mail, msg, submission)

    def post_conference_msg(self, msg):
        mail = sendgrid.helpers.mail.Mail(
                    sendgrid.helpers.mail.Email(msg.from_address(), msg.from_name()),
                    msg.build_subject(),
                    sendgrid.helpers.mail.Email(msg.to_address()),
                    sendgrid.helpers.mail.Content("text/plain", msg.build_message()))

        for cc in massage_none_list(msg.cc_addresses(None)):
            mail.personalizations[0].add_cc(sendgrid.helpers.mail.Email(cc))

        for bcc in massage_none_list(msg.bcc_addresses(None)):
            mail.personalizations[0].add_bcc(sendgrid.helpers.mail.Email(bcc))

        if sysinfo.is_running_local():
            logging.info("Mail sending to: " + msg.conference.creator_id)
            logging.info("Body = " + msg.build_message())

        self.do_send(mail, msg, None)

    def do_send(self, mail, msg, submission):
        try:
            # Note: Sockets do not operate on local dev server
            # So don't do the call
            if not sysinfo.is_running_local():
                response = self.sg.client.mail.send.post(request_body=mail.get())
                status_code = response.status_code
            else:
                logging.info(mail.get())
                status_code = 201

            # SendGrid error messages https://sendgrid.com/docs/API_Reference/Web_API_v3/Mail/errors.html
            if status_code >= 200 and status_code <= 300:
                msg.mark_comms(submission)
            else:
                logging.error("Mail failure sending to: " + " Response status code: " + status_code)
                logging.info(mail.get())
                msg.mark_comms_fail(submission)
        except urllib2.HTTPError, e:
            logging.error("Mail failure with HTTPError exception.")
            logging.info(mail.get())
            logging.info(e.code)
            logging.info(e.reason)
            logging.info(e.headers)
            logging.info(e.read())
            msg.mark_comms_fail(submission)

