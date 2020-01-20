#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
from google.appengine.ext import ndb

# Local imports
import basehandler


class AcceptDeclinePage(basehandler.BaseHandler):
    def get(self):
        sub_key = ndb.Key(urlsafe=self.request.get("sub"))
        template_values = {
            'crrt_conf' : sub_key.parent().get(),
            'sub': sub_key.get(),
        }

        self.write_page('submission_lib/acceptdecline.html', template_values)

    def accept(self, sub_key):
        sub = sub_key.get()
        sub.mark_accept_acknowledged()
        self.response.write("Thank you for accepting, we will be in contract shortly.")

    def decline(self, sub_key):
        sub = sub_key.get()
        sub.mark_accept_declined()
        self.response.write("That is a shame.<p>    We would appreciate an e-mail to let us know what changed and whether we could do better in future.")


    def other(self, sub_key):
        sub = sub_key.get()
        sub.mark_accept_problem()
        self.response.write("O dear :) <p>Please e-mail us as soon as possible and lets see if we can fix this." +
                            "<p>Send mail to: " + sub_key.parent().get().contact_email() + ".")

    def post(self):
        sub_key = ndb.Key(urlsafe=self.request.get("sub_key"))

        if self.request.get("accept"):
            self.accept(sub_key)

        if self.request.get("decline"):
            self.decline(sub_key)

        if self.request.get("other"):
            self.other(sub_key)
