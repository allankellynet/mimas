#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports
import sys

sys.path.append("external/python-http-client")
sys.path.append("external/sendgrid-python")

import unittest
from talk_lib import talk
from speaker_lib import speaker
from conference_lib import conference
from conference_lib import confoptions
from submission_lib import submissionrecord
from mailmsg import msgtemplate, postmail

from google.appengine.ext import testbed

from mock import patch

class TestPostMail(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def common_setup(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()
        track1 = confoptions.make_conference_track(c.key, "track")
        format1 = confoptions.make_conference_option(confoptions.TalkFormatOption, c.key, "lecture")
        duration1 = confoptions.make_conference_option(confoptions.DurationOption, c.key, "10mins")
        expenses1 = confoptions.make_conference_option(confoptions.ExpenseOptions, c.key, "Money")

        s = speaker.make_new_speaker("arnold@email")
        s.name = "Arnold Rimmer"
        s.put()

        t1 = talk.Talk(parent=s.key)
        t1.title = "Talk T1"
        t1.put()
        sub_key1 = submissionrecord.make_submission_plus(t1.key, c.key,
                                                         track1.shortname(), format1.shortname(),
                                                         duration1.shortname(), expenses1.shortname())
        return c, sub_key1

    '''
    #@patch("sendgrid.helpers.mail")
    @patch.object(python_http_client.Client, 'mock_client')
    def test_ack_submission(self, mock_client):
        c, sub_key1 = self.common_setup()

        acknowledge = msgtemplate.retrieveTemplate(msgtemplate.AcknowledgeMsg, c.key)
        mock_client = Mock()
        postmail.Postman().post_one(c, acknowledge, sub_key1)

        mock_mail = Mock()
        postmail.ack_submission(sub_key1.get(), c.key)
        self.assertTrue(mock_mail.sender.called_with("submission@mimas-aotb.appspotmail.com"))
        self.assertTrue(mock_mail.message_to.called_with("arnold@email"))
        self.assertTrue(mock_send.called)

        mock_send.side_effect = mail_errors.Error()
        self.assertRaises(Exception, postmail.ack_submission, sub_key1.get(), c.key)


    @patch("google.appengine.api.mail.EmailMessage")
    @patch.object(mail.EmailMessage, 'send')
    @patch("sendgrid.helpers.mail")
    @patch.object(sendgrid.helpers.mail.Mail, '__init__')
    def test_accept(self, mock_mail, mock_send, mock_sg_mail, mock_sg_send):
        c, sub_key1 = self.common_setup()

        accept = msgtemplate.retrieveTemplate(msgtemplate.AcceptMsg, c.key)
        mock_sg_mail = Mock()
        postmail.Postman().post_one(accept, sub_key1)
        self.assertTrue(mock_mail.sender.called_with("submission@mimas-aotb.appspotmail.com"))
        self.assertTrue(mock_mail.message_to.called_with("arnold@email"))
        self.assertTrue(mock_send.called)
        self.assertEquals("Accepted", sub_key1.get().communication)

        mock_send.side_effect = mail_errors.Error()
        try:
            postmail.Accept().post_one(sub_key1)
        except:
            self.assertTrue(True, "Exception rasied as expected")
        else:
            self.assertTrue(False, "Exception not rasied as expected")

    # patch sendgrid.SendGridAPIClient
    @patch("google.appengine.api.mail.EmailMessage")
    @patch.object(mail.EmailMessage, 'send')
    @patch("sendgrid.helpers.mail")
    @patch.object(sendgrid.helpers.mail.Mail, '__init__')
    def test_decline(self, mock_mail, mock_send, mock_sg_mail, mock_sg_send):
        c, sub_key1 = self.common_setup()

        decline = msgtemplate.retrieveTemplate(msgtemplate.DeclineMsg, c.key)
        mock_mail = Mock()
        postmail.Postman().post_one(c, decline, sub_key1)
        self.assertTrue(mock_mail.sender.called_with("submission@mimas-aotb.appspotmail.com"))
        self.assertTrue(mock_mail.message_to.called_with("arnold@email"))
        self.assertTrue(mock_send.called)
        self.assertEquals("Declined", sub_key1.get().communication)

        mock_send.side_effect = mail_errors.Error()
        try:
            postmail.post_one(decline, sub_key1)
        except:
            self.assertTrue(True, "Exception rasied as expected")
        else:
            self.assertTrue(False, "Exception not rasied FAIL")
    '''

    # With removal of deferred sendint this test doesn't do much
    # Mail needs a good overhaul :(
    @patch("mailmsg.postmail.Postman.post_one")
    def test_post_many(self, mock_deferred_func):
        c, sub_key1 = self.common_setup()

        t2 = talk.Talk()
        t2.title = "Talk T2"
        t2.put()
        sub_key2 = submissionrecord.make_submission_plus(t2.key, c.key,
                                                         "track", "format",
                                                         "time", "exp")

        t3 = talk.Talk()
        t3.title = "Talk T3"
        t3.put()
        sub_key3 = submissionrecord.make_submission_plus(t3.key, c.key,
                                                         "track", "format", "time", "exp")

        accept = msgtemplate.retrieveTemplate(msgtemplate.AcceptMsg, c.key)
        try:
            postmail.Postman().post_many(c,
                                         accept,
                                         [sub_key1.get(), sub_key2.get(), sub_key3.get()],
                                         send_gap_seconds=10)
        except:
            self.assertTrue(False, "Exception rasied unexpectedly")
        else:
            self.assertTrue(True, "Exception not rasied as expected")

    def test_massage_none_list(self):
        self.assertEquals(postmail.massage_none_list(None), [])
        self.assertEquals(postmail.massage_none_list([]), [])
        self.assertEquals(postmail.massage_none_list(["a", "b", "c"]), ["a", "b", "c"])
