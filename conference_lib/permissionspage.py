#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
from scaffold import userrightsnames, sorrypage
import basehandler


class PermissionsPage(basehandler.BaseHandler):
    def get(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        if not(conference.user_rights().has_permission(self.get_crrt_user().email(),
                                                       userrightsnames.CONF_CREATOR)):
            sorrypage.redirect_sorry(self, "NoAccess")
            return

        if self.request.params.has_key("usr"):
            email = self.request.get("usr")
            update = True
        else:
            email = ""
            update = False

        template_values = {
            "conference": conference,
            "conf_key": conference.key,
            "email": email,
            "update": update,
            "sorted_permissions": sorted(conference.user_rights().permissions().keys()),
        }

        self.write_page('conference_lib/permissionspage.html', template_values)

    def add_permissions(self, conf, this_page):
        user_name = self.request.get("new_email")
        if len(user_name) == 0:
            return

        for permission in conf.user_rights().permissions():
            if self.request.get(permission):
                conf.user_rights().add_permission(user_name, permission)

        self.redirect(this_page)

    def remove_authority(self, conf, this_page):
        to_delete = self.request.get("authorityToDelete")
        if (to_delete == self.get_crrt_user().email()):
            self.redirect("/sorry_page?reason=NoDeleteSelf")
        else:
            conf.user_rights().drop_all_permissions(to_delete)
            self.redirect(this_page)

    def update_authority(self, conf, this_page):
        user_name = self.request.get("new_email")

        # Creator permission cannot be deleted(at the moment)
        if conf.user_rights().has_permission(user_name, userrightsnames.CONF_CREATOR):
            creator = True
        else:
            creator = False

        conf.user_rights().drop_all_permissions(user_name)

        if creator:
            conf.user_rights().add_permission(user_name, userrightsnames.CONF_CREATOR)

        self.add_permissions(conf, this_page)

    def post(self):
        safe_key = self.request.get("conf_safe_key")
        this_page = "/permissionspage?conf=" + safe_key
        conf = ndb.Key(urlsafe=safe_key).get()
        if self.request.get("SubmitNew"):
            self.add_permissions(conf, this_page)
        elif self.request.get("remove_authority"):
            self.remove_authority(conf, this_page)
        elif self.request.get("UpdateExisting"):
            self.update_authority(conf, this_page)
