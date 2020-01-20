#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import confoptions
from scaffold import sorrypage, userrightsnames
import basehandler


class ConferenceEmailsPage(basehandler.BaseHandler):

    def get(self):
        if not(self.request.params.has_key("conf")):
            sorrypage.redirect_sorry(self, "ConfKeyMissing")
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        if not(conference.user_rights().has_permission(self.get_crrt_user().email(),
                                                       userrightsnames.CONF_CREATOR)):
            sorrypage.redirect_sorry(self, "NoAccess")
            return

        self.write_page('conference_lib/confemailrecipients.html', {
            "crrt_conf": conference,
            "tracks": conference.track_options(),
            "conf_key": conference.key,
            "email_ack_cc": conference.ack_cc_addresses(),
            "email_ack_bcc": conference.ack_bcc_addresses(),
            "email_accept_cc": conference.accept_cc_addresses(),
        })

    # TODO Extract and unit test
    def add_for_selected(self, conf_key, email):
        if self.request.get("AckCC"):
            confoptions.make_conference_option(confoptions.AcknowledgementEmailCCAddresses, conf_key, email)
        if self.request.get("AckBCC"):
            confoptions.make_conference_option(confoptions.AcknowledgementEmailBCCAddresses, conf_key, email)
        if self.request.get("AcceptCC"):
            confoptions.make_conference_option(confoptions.AcceptEmailCCAddress, conf_key, email)

    # TODO Extract and unit test
    def add_email(self):
        conf_key = ndb.Key(urlsafe=self.request.get("crrt_conf_key"))
        email = self.request.get("NewMail")
        if len(email)>0:
            self.add_for_selected(conf_key, email)

        self.redirect('/confemailcopy?conf=' + self.request.get("crrt_conf_key"))

    def delete_email(self, check_field, Option_Class):
        conf_key = ndb.Key(urlsafe=self.request.get("crrt_conf_key"))
        for opt in self.request.get_all(check_field):
            confoptions.delete_option(Option_Class, conf_key, opt)

        self.redirect('/confemailcopy?conf=' + conf_key.urlsafe())

    def post(self):
        if self.request.get("NewMail"):
            self.add_email()
        elif self.request.get("DeleteAckCCEmails"):
            self.delete_email("selectAckCCEmail", confoptions.AcknowledgementEmailCCAddresses)
        elif self.request.get("DeleteAckBCCEmails"):
            self.delete_email("selectAckBCCEmail", confoptions.AcknowledgementEmailBCCAddresses)
        elif self.request.get("DeleteAcceptCCEmails"):
            self.delete_email("selectAcceptCCEmail", confoptions.AcceptEmailCCAddress)
