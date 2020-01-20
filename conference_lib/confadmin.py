#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import confdb
import conference
import confmsgs
from mailmsg import postmail
from scaffold import sorrypage, sysinfo, userrightsnames
import basehandler


class ConferenceAdminPage(basehandler.BaseHandler):
    def new_conference_values(self):
        crrt_conf = conference.Conference()
        template_values = {
            "usr_email": self.get_crrt_user().email(),
            "conf_key": None,
            "crrt_conf": crrt_conf,
            "creator_rights": "",
            "home_url": sysinfo.home_url(),
        }

        return template_values

    def existing_conference(self):
        conf = self.get_crrt_conference_key().get()
        template_values = {
            "usr_email": self.get_crrt_user().email(),
            "conf_key": conf.key,
            "crrt_conf": conf,
            "creator_rights": self.rights(conf),
            "home_url": sysinfo.home_url(),
        }

        return template_values

    def rights(self, conf):
        if not (conf.user_rights().has_permission(
                self.get_crrt_user().email(),
                userrightsnames.CONF_CREATOR)):
            creator_rights = "disabled"
        else:
            creator_rights = ""
        return creator_rights

    def get(self):
        if self.request.params.has_key("new"):
            self.clear_crrt_conference()
            self.write_page('conference_lib/confadmin.html', self.new_conference_values())
            return

        if self.get_crrt_conference_key() == None:
            self.redirect("/chooseconf")
            return

        rights = self.get_crrt_conference_key().get().user_rights()
        if rights.has_permission(self.get_crrt_user().email(), userrightsnames.CONF_ADMINISTRATOR):
            self.write_page('conference_lib/confadmin.html', self.existing_conference())
        else:
            sorrypage.redirect_sorry(self, "AdminRightsReq")

    def read_fields(self, conf):
        conf.name = self.request.get("newconfname")
        conf.dates = self.request.get("dates")
        conf.shortname = self.request.get("shortname")
        conf.set_website(self.request.get("website"))
        conf.set_gdpr_address(self.request.get("gdpr"))
        conf.set_cfp_address(self.request.get("cfp"))
        conf.set_contact_email(self.request.get("contact_email"))

    def read_image(self, conf):
        if self.request.get("confimage"):
            conf.set_image(self.request.get("confimage"))

    def validate_fields(self):
        suggested_name = self.request.get("newconfname")
        if len(suggested_name)==0:
            sorrypage.redirect_sorry(self, "BlankNameField")
            return False

        if len(self.request.get("dates"))==0:
            sorrypage.redirect_sorry(self, "BlankDateField")
            return False

        if len(self.request.get("shortname"))==0:
            sorrypage.redirect_sorry(self, "BlankShortnameField")
            return False

        if len(self.request.get("contact_email"))==0:
            sorrypage.redirect_sorry(self, "ContactEmailMandatory")
            return False

        return True

    def make_conference(self):
        c = conference.Conference()
        c.creator_id = self.get_crrt_user().email()
        self.read_fields(c)
        c.put()

        self.read_image(c)

        c.user_rights().add_permission(c.creator_id, userrightsnames.CHANGE_CONF_STATE)
        c.user_rights().add_permission(c.creator_id, userrightsnames.APPOINT_REVIEWERS)
        c.user_rights().add_permission(c.creator_id, userrightsnames.ROUND1_DECISION)
        c.user_rights().add_permission(c.creator_id, userrightsnames.ROUND2_DECISION)
        c.user_rights().add_permission(c.creator_id, userrightsnames.CONF_CREATOR)
        c.user_rights().add_permission(c.creator_id, userrightsnames.CONF_ADMINISTRATOR)
        return c

    def new_conference(self):
        if self.validate_fields():
            if confdb.get_conf_by_name(self.request.get("newconfname")):
                sorrypage.redirect_sorry(self, "ConfNameInUse")
                return

            if confdb.get_conf_by_shortname(self.request.get("shortname")):
                sorrypage.redirect_sorry(self, "ConfShortnameInUse")
                return

            conf = self.make_conference()
            postmail.Postman().post_conference_msg(confmsgs.make_conference_created_msg(conf))
            self.redirect("/confconfigpage?conf=" + conf.key.urlsafe())

    def update_conference(self):
        if self.validate_fields():
            conf_key = ndb.Key(urlsafe=self.request.get("conf_safekey"))
            conf = conf_key.get()
            self.read_fields(conf)
            conf.put()
            self.read_image(conf)
            self.redirect("/createconf?conf="+conf_key.urlsafe())

    def delete_conference(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_safekey"))

        if conf_key.get().user_rights().has_permission(self.get_crrt_user().email(), userrightsnames.CONF_CREATOR):
            self.redirect("/delete_con_page?conf="+conf_key.urlsafe())
        else:
            self.redirect("/sorry_page?reason=NoDeleteRights")

    def post(self):
        if self.request.get("SubmitNewConf"):
            self.new_conference()
        elif self.request.get("UpdateConf"):
            self.update_conference()
        elif self.request.get("DeleteConf"):
            self.delete_conference()
