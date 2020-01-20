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


class ConferenceOptionsPage(basehandler.BaseHandler):

    def get(self):
        if not(self.request.params.has_key("conf")):
            sorrypage.redirect_sorry(self, "ConfKeyMissing")
            return

        conf_key = ndb.Key(urlsafe=self.request.get("conf"))
        conference = conf_key.get()

        disabled = ""
        if conference.state() != "Closed":
            disabled = "disabled"

        if not(conference.user_rights().has_permission(self.get_crrt_user().email(),
                                                       userrightsnames.CONF_CREATOR)):
            sorrypage.redirect_sorry(self, "NoAccess")
            return

        template_values = {
            "crrt_conf": conference,
            "tracks": conference.track_objects(),
            "conf_key": conference.key,
            "aotb_extras": conference.shortname=="AOTB2021",
            "test_setup": conference.shortname == "TEST2017" or conference.shortname == "TEST2018",
            "durations": conference.duration_options(),
            "formats": conference.delivery_format_options(),
            "expenses": conference.expenses_options(),
            "read_only": disabled,
        }

        self.write_page('conference_lib/confoptionspage.html', template_values)

    def default_setup(self):
        self.set_crrt_conference_key(ndb.Key(urlsafe=self.request.get("conf_key")))
        self.redirect("/testdata?test='DefaultData'")

    def test_setup(self):
        self.set_crrt_conference_key(ndb.Key(urlsafe=self.request.get("conf_key")))
        self.redirect("/testdata?test=StandardData")


    def aotb_options(self):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        confoptions.make_conference_track(conf_key, "Software delivery")
        confoptions.make_conference_track(conf_key, "Product Design")
        confoptions.make_conference_track(conf_key, "Product Management")
        confoptions.make_conference_track(conf_key, "Team working")
        confoptions.make_conference_track(conf_key, "Agile Practices")
        confoptions.make_conference_track(conf_key, "Agility in software business")
        confoptions.make_conference_track(conf_key, "Agility in general business")

        confoptions.make_conference_option(confoptions.DurationOption,
                                           conf_key,
                                           "Single session (45 minutes)")
        confoptions.make_conference_option(confoptions.DurationOption,
                                           conf_key,
                                           "Double session (90 minutes+)")

        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Lecture style")
        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Interactive with exercises (no computers)")
        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Interactive hands on computers")
        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Panel discussion")
        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Other (use long synopsis to describe)")

        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "Local - no expenses required, accommodation available")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "UK - accommodation and travel from within UK")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,"Short-haul - accommodation and travel from within Europe")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "Mid-haul - accommodation and travel from outside Europe e.g. Russia, Israel")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "Long-haul - accommodation and long haul travel e.g. USA")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "Long-haul limited - accommodation and travel within UK; will pay own way to UK")

        self.redirect('/confoptionspage?conf='+self.request.get("conf_key"))

    def add_option(self, input_field, Option_Class):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        field = self.request.get(input_field)
        if len(field)>0:
            confoptions.make_conference_option(Option_Class, conf_key, field)

        self.redirect('/confoptionspage?conf=' + self.request.get("conf_key"))

    def delete_options(self, check_field, Option_Class):
        conf_key = ndb.Key(urlsafe=self.request.get("conf_key"))
        for opt in self.request.get_all(check_field):
            confoptions.delete_option(Option_Class, conf_key, opt)

        self.redirect('/confoptionspage?conf=' + conf_key.urlsafe())

    def update_track_slots(self):
        conference = ndb.Key(urlsafe=self.request.get("conf_key")).get()
        tracks = conference.track_objects()
        for t in tracks:
            slots = int(self.request.get("slots"+t.shortname_m))
            t.slots = slots
            t.put()

        self.redirect('/confoptionspage?conf=' + conference.key.urlsafe())


    def post(self):
        if self.request.get("NewTrackSubmit"):
            self.add_option("NewTrack", confoptions.TrackOption)
        elif self.request.get("DeleteTracks"):
            self.delete_options("selectTrack", confoptions.TrackOption)
        elif self.request.get("UpdateTrackSlots"):
            self.update_track_slots()
        elif self.request.get("NewDurationSubmit"):
            self.add_option("NewDuration", confoptions.DurationOption)
        elif self.request.get("DeleteDuration"):
            self.delete_options("selectDuration", confoptions.DurationOption)
        elif self.request.get("NewFormatSubmit"):
            self.add_option("NewFormat", confoptions.TalkFormatOption)
        elif self.request.get("DeleteFormat"):
            self.delete_options("selectFormat", confoptions.TalkFormatOption)
        elif self.request.get("NewExpensesSubmit"):
            self.add_option("NewExpenses", confoptions.ExpenseOptions)
        elif self.request.get("DeleteExpenses"):
            self.delete_options("selectExpenses", confoptions.ExpenseOptions)
        elif self.request.get("AOTBOPTS"):
            self.aotb_options()
        elif self.request.get("TESTSETUP"):
            self.test_setup()
        elif self.request.get("DEFAULTSETUP"):
            self.default_setup()

