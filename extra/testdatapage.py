#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# System imports

# Google imports

# Local imports
from scaffold import attentionpage, userrightsnames
import basehandler
from conference_lib import confoptions, conference
from submission_lib import submissionrecord
from speaker_lib import speaker
from talk_lib import talk
from reports import reportrecord

class TestDataPage(basehandler.BaseHandler):
    def get(self):
        conf_key = self.get_crrt_conference_key()
        if conf_key is None:
            conference = None
        else:
            conference = conf_key.get()

        if self.request.params.has_key("test"):
            self.populate_test_data(self.request.get("test"))
            return

        template_values = {
            'conference' : conference,
        }

        self.write_page('extra/testdatapage.html', template_values)

    def default_data(self):
        conf_key = self.get_crrt_conference_key()
        conference = conf_key.get()
        track1 = confoptions.make_conference_track(conf_key, "Technical")
        track2 = confoptions.make_conference_track(conf_key, "Management")
        track3 = confoptions.make_conference_track(conf_key, "Teams")
        duration1 = confoptions.make_conference_option(confoptions.DurationOption,
                                                       conf_key,
                                           "Single session (45 minutes)")
        confoptions.make_conference_option(confoptions.DurationOption,
                                           conf_key,
                                           "Double session (90 minutes+)")

        format1 = confoptions.make_conference_option(confoptions.TalkFormatOption,
                                                     conf_key,
                                           "Lecture style")
        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Interactive (no computers)")

        expenses1 = confoptions.make_conference_option(confoptions.ExpenseOptions,
                                                       conf_key,
                                           "Long-haul")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "Short-haul")

        return '/confoptionspage?conf=' + conf_key.urlsafe()

    def standard_test_data(self):
        conf_key = self.get_crrt_conference_key()
        conference = conf_key.get()
        track1 = confoptions.make_conference_track(conf_key, "Software delivery")
        track2 = confoptions.make_conference_track(conf_key, "Product Management")
        track3 = confoptions.make_conference_track(conf_key, "Team working")
        duration1 = confoptions.make_conference_option(confoptions.DurationOption,
                                                       conf_key,
                                           "Single session (45 minutes)")
        confoptions.make_conference_option(confoptions.DurationOption,
                                           conf_key,
                                           "Double session (90 minutes+)")

        format1 = confoptions.make_conference_option(confoptions.TalkFormatOption,
                                                     conf_key,
                                           "Lecture style")
        confoptions.make_conference_option(confoptions.TalkFormatOption,
                                           conf_key,
                                           "Interactive with exercises (no computers)")

        expenses1 = confoptions.make_conference_option(confoptions.ExpenseOptions,
                                                       conf_key,
                                           "Local")
        confoptions.make_conference_option(confoptions.ExpenseOptions,
                                           conf_key,
                                           "UK")

        s = speaker.make_new_speaker("speaker@example.com")
        s.name = "Speaker Test"
        speaker_key = s.put()

        t = talk.Talk(parent=s.key)
        t.title = "All talk"
        t_key = t.put()

        sub_key = submissionrecord.make_submission_plus(
                                                    t_key,
                                                    conf_key,
                                                    track1.shortname(),
                                                    format1.shortname(),
                                                    duration1.shortname(),
                                                    expenses1.shortname())

        t2 = talk.Talk(parent=s.key)
        t2.title = "Talk2"
        t2_key = t.put()

        sub_key2 = submissionrecord.make_submission_plus(
                                                    t2_key,
                                                    conf_key,
                                                    track1.shortname(),
                                                    format1.shortname(),
                                                    duration1.shortname(),
                                                    expenses1.shortname())

        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.CONF_CREATOR)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.CHANGE_CONF_STATE)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.APPOINT_REVIEWERS)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.ROUND1_REVIEWER)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.ROUND1_DECISION)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.ROUND2_REVIEWER)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.ROUND2_DECISION)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.ROUND2_DECISION)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.SPEAK_COMMS_COMMS)
        conference.user_rights().add_permission("test@example.com",
                                                userrightsnames.CONF_DATA_DUMPS)

        conference.user_rights().add_track_reviewer("test@example.com",
                                                    track1.shortname())
        conference.user_rights().add_track_reviewer("test@example.com",
                                                    track2.shortname())
        conference.user_rights().add_track_reviewer("test@example.com",
                                                    track3.shortname())

        reportrecord.mk_report_record(conf_key, "Export", "none.such")

        return '/confoptionspage?conf='+conf_key.urlsafe()

    def named_conference_setup(self, shortname):
        conf = conference.Conference()
        conf.creator_id = self.get_crrt_user().email()
        conf.name = shortname
        conf.dates = "August"
        conf.shortname = shortname
        conf.set_website("http://www.mimascr.com")
        conf.set_gdpr_address("http://www.gdpr.eu")
        conf.set_cfp_address("http://www.mimascr.com/cfp")
        conf.set_contact_email("postmaster@mimascr.com")
        conf.put()

        conf.creator_id = self.get_crrt_user().email()
        conf.user_rights().add_permission(conf.creator_id, userrightsnames.CONF_CREATOR)
        conf.user_rights().add_permission(conf.creator_id, userrightsnames.CONF_ADMINISTRATOR)

        self.set_crrt_conference_key(conf.key)
        return "/createconf"

    def conference_test(self):
        self.named_conference_setup("TestCon2019")
        return self.standard_test_data()

    def empty_conference_setup(self):
        return self.named_conference_setup("EmptyCon")

    def add_test_speaker(self, name, email):
        s = speaker.make_new_speaker(email)
        s.name = name
        return s.put()

    def add_test_talk(self, speaker_key, title):
        t = talk.Talk(parent=speaker_key)
        t.title = title
        return t.put()


    def more_subs(self):
        conf_key = self.get_crrt_conference_key()
        conference = conf_key.get()
        track =    conference.track_options().keys()[0]
        duration = conference.duration_options().keys()[0]
        format =   conference.delivery_format_options().keys()[0]
        expenses = conference.expenses_options().keys()[0]

        skey1=self.add_test_speaker("Testing 1", "speaker@testing.com")
        tkey1=self.add_test_talk(skey1, "Talk from S1")
        submissionrecord.make_submission_plus(tkey1, conf_key, track, format, duration, expenses)

        skey2=self.add_test_speaker("Testing 2", "speaker2@testing.com")
        tkey2=self.add_test_talk(skey2, "Talk from S2")
        submissionrecord.make_submission_plus(tkey2, conf_key, track, format, duration, expenses)

        skey3=self.add_test_speaker("Testing 3", "speaker3@testing.com")
        tkey3=self.add_test_talk(skey3, "Talk from S3")
        submissionrecord.make_submission_plus(tkey3, conf_key, track, format, duration, expenses)

        skey4=self.add_test_speaker("Testing 4", "speaker4@testing.com")
        tkey4=self.add_test_talk(skey4, "Talk from S4")
        submissionrecord.make_submission_plus(tkey4, conf_key, track, format, duration, expenses)

        return "/createconf"

    def lots_more(self):
        conf_key = self.get_crrt_conference_key()
        conference = conf_key.get()
        tracks =    conference.track_options().keys()
        track_count = len(tracks)
        duration = conference.duration_options().keys()[0]
        format =   conference.delivery_format_options().keys()[0]
        expenses = conference.expenses_options().keys()[0]

        for i in range(1, int(self.request.get("how_many", "20"))+1):
            speaker = "Speaker Smith " + str(i)
            semail = "speakersmith" + str(i) + "@reward.com.co"
            skey = self.add_test_speaker(speaker, semail)
            tkey = self.add_test_talk(skey, "Talk from " + speaker)
            submissionrecord.make_submission_plus(tkey, conf_key, tracks[i%track_count], format, duration, expenses)

        return "/createconf"

    def delete_talks(self, speaker_key):
        talk_keys = talk.Talk.query(ancestor=speaker_key).fetch(keys_only=True)
        map(lambda t: t.delete(), talk_keys)

    def delete_speaker_data(self, skeys):
        for key in skeys:
            self.delete_talks(key)
            key.delete()

    def delete_speaker(self, semail):
        skeys = speaker.Speaker.query(speaker.Speaker.speaker_email == semail).fetch(keys_only=True)
        if len(skeys) > 0:
            self.delete_speaker_data(skeys)

    def delete_data(self):
        for i in range(1, 99):
            self.delete_speaker("speakersmith" + str(i) + "@reward.com.co")

        self.delete_speaker("speaker@example.com")
        self.delete_speaker("speaker@testing.com")
        self.delete_speaker("speaker2@testing.com")
        self.delete_speaker("speaker3@testing.com")
        self.delete_speaker("speaker4@testing.com")

        return "/createconf"

    def populate_test_data(self, test_name):
        data_options = {"DefaultData": self.default_data,
                        "StandardData": self.standard_test_data,
                        "TestCon2019": self.conference_test,
                        "EmptyConf": self.empty_conference_setup,
                        "MoreSubs": self.more_subs,
                        "LotsSubs": self.lots_more,
                        "DeleteData": self.delete_data,
                        }

        if data_options.has_key(test_name):
            next_page = data_options[test_name]()
        else:
            attentionpage.redirect_attention(self, "Unknown")
            return

        self.redirect(next_page)

    def post(self):
        if self.request.get("LotsSubs"):
            self.lots_more()

        self.redirect("/createconf")