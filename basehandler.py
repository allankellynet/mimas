# System imports
import os
import jinja2
import webapp2

# App Engine imports
from google.appengine.api import users
from google.appengine.ext import ndb
from webapp2_extras import sessions

# local includes

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def write_page(self, page_filename, params):
            params['logoutlink'] = self.logout_link()
            template = JINJA_ENVIRONMENT.get_template(page_filename)
            self.response.write(template.render(params))

    def get_crrt_user(self):
        return ndb.Key(urlsafe=self.session["uk"]).get()

    def is_logged_in(self):
        return self.session.has_key("uk")

    def set_crrt_conference_key(self, key):
        self.session["crrt_conference"] = key.urlsafe()

    def clear_crrt_conference(self):
        self.session.pop("crrt_conference", None)

    def get_crrt_conference_key(self):
        if self.request.params.has_key("conf"):
            key = ndb.Key(urlsafe=self.request.get("conf"))
            self.set_crrt_conference_key(key)
            return key

        if self.has_conference_session_key():
            return ndb.Key(urlsafe=self.session["crrt_conference"])

        return None

    def has_conference_session_key(self):
        return self.session.has_key("crrt_conference")

    def logout_link(self):
        if users.get_current_user() != None:
            # Google direct login so logging out
            # Calls Google URL which then presents this page
            return users.create_logout_url("logoutpageb")
        else:
            return "logoutpagef"
