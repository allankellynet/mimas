#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

import unittest

# Library imports
from google.appengine.ext import testbed

# Local imports
from conference_lib import conference
from conference_lib import confoptions
from mailmsg import msgtemplate
from speaker_lib import speaker
from submission_lib import submissionrecord
from talk_lib import talk


class TestMsgTemplate(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def create_conference(self):
        self.c = conference.Conference()
        self.c.name = "Wizard Con 2018"
        self.c.put()

        self.s = speaker.make_new_speaker("harry@hogwarts.com")
        self.s.name = "Harry Potter"
        self.s.bio = "Harry is an amazing wizard"
        self.s.put()

        self.t = talk.Talk(parent=self.s.key)
        self.t.title = "Fighting Voldermort"
        self.t.put()

        self.sub_key = submissionrecord.make_submission(self.t.key, self.c.key, "track", "format")

    def test_Accept(self):
        accept = msgtemplate.AcceptMsg()
        self.assertTrue(len(accept.subject()) > 0)
        self.assertTrue(len(accept.message())>0)

        self.create_conference()
        self.assertEquals(accept.bcc_addresses(self.sub_key), None)
        self.assertEquals(accept.cc_addresses(self.sub_key), None)

        confoptions.make_conference_option(confoptions.AcceptEmailCCAddress, self.c.key, "harry@hogwarts.com")
        self.assertEquals(accept.cc_addresses(self.sub_key), ["harry@hogwarts.com"])


    def test_Decline(self):
        decline = msgtemplate.DeclineMsg()
        self.assertTrue(len(decline.subject())>0)
        self.assertTrue(len(decline.message()) > 0)

        self.assertEquals(decline.cc_addresses(None), None)
        self.assertEquals(decline.bcc_addresses(None), None)

    def test_retrieveTemplate(self):
        self.create_conference()

        template = msgtemplate.retrieveTemplate(msgtemplate.AcceptMsg, self.c.key)
        self.assertTrue(template != None)

        template.set_subject_line("Acceptance - yahoo!")
        template.put()

        template2 = msgtemplate.retrieveTemplate(msgtemplate.AcceptMsg, self.c.key)
        self.assertEqual("Acceptance - yahoo!", template2.subject())

    def test_make_substitution_map(self):
        self.create_conference()

        substitutions = msgtemplate.AcceptMsg().make_substitution_map(self.sub_key.get())

        self.assertEqual(substitutions["%CONFERENCE_NAME%"], "Wizard Con 2018")
        self.assertEqual(substitutions["%SPEAKER%"], "Harry Potter")
        self.assertEqual(substitutions["%SPEAKER_BIO%"], "Harry is an amazing wizard")
        self.assertEqual(substitutions["%SUBMISSION_TITLE%"], "Fighting Voldermort")

    def test_msgBuilder(self):
        self.create_conference()

        template = msgtemplate.AcceptMsg()
        template.set_subject_line("Acceptance %CONFERENCE_NAME%")

        self.assertEquals("Acceptance Wizard Con 2018", template.build_subject(self.sub_key.get()))

        template.set_message(
            'Dear %SPEAKER%,||\n' \
            'I am pleased to inform you that "%SUBMISSION_TITLE%" has been accepted to %CONFERENCE_NAME%.||\n'\
            'Yours sincerely,||\n'\
            'Dumbledor')

        self.assertEquals('Dear Harry Potter,||\n'\
                           'I am pleased to inform you that "Fighting Voldermort" '\
                           'has been accepted to Wizard Con 2018.||\n'\
                           'Yours sincerely,||\n'\
                           'Dumbledor',
                            template.build_message(self.sub_key.get())
                          )

    def test_ack_message(self):
        self.create_conference()
        self.c.set_contact_email("mail@conference.co")

        ack_msg = msgtemplate.retrieveTemplate(msgtemplate.AcknowledgeMsg, self.c.key)

        self.assertEquals("Submission acknowledgement: Wizard Con 2018",
                          ack_msg.build_subject(self.sub_key.get()))

        expected = u"Confirm 'Fighting Voldermort' has been received by Wizard Con 2018." + \
                "\n\n" + \
                "In the meantime if you have any question please contact us on mail@conference.co." +\
                "\n\n" +\
                "...................................................................\n\n" + \
                "Title: Fighting Voldermort\n\n" + \
                "Track: %SUBMISSION_TRACK%\n\n" + \
                "Format: %SUBMISSION_FORMAT%\n\n" + \
                "Duration: %SUBMISSION_DURATION%\n\n" + \
                "Speaker bio: Harry is an amazing wizard\n\n" + \
                "Short synopsis: \n\n" \
                "Long synopsis: \n\n"

        self.assertEquals(
                expected,
                ack_msg.build_message(self.sub_key.get())
                )

    def test_mk_speaker_edit_url(self):
        self.create_conference()
        url = msgtemplate.SubmissionMessageTemplate().mk_speaker_edit_url(self.sub_key.get())
        expected = "/speakerupdate?key=" + self.s.key.urlsafe() + \
                    "&email=harry@hogwarts.com"
        self.assertEquals(expected, url)

    def test_mk_feedback_url(self):
        self.create_conference()
        url = msgtemplate.SubmissionMessageTemplate().mk_feedback_url(self.sub_key.get())
        expected = "/review_feedback?k=" + self.sub_key.urlsafe()
        self.assertEquals(expected, url)
