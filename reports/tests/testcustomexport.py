#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from mock import Mock, patch, call
import mock

from google.appengine.ext import testbed

from conference_lib import conference, confoptions
from reports import customexport, exportexcel
from talk_lib import talk
from speaker_lib import speaker, cospeaker
from submission_lib import submissionrecord, submissionnotifynames

class TestCustomReport(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.conf = conference.Conference()
        self.conf.name = "Test Dummy Conf"
        self.conf.put()


    def tearDown(self):
        self.testbed.deactivate()

    def test_list_all_report_names(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        new_report_key = customexport.mk_report(self.conf.key, "Potter")
        self.assertEquals("Potter", new_report_key.get().report_name())
        self.assertEquals(["Potter"], customexport.list_all_report_names(self.conf.key))

        customexport.mk_report(self.conf.key, "Weesley")
        self.assertEquals(["Potter", "Weesley"], customexport.list_all_report_names(self.conf.key))

    def test_get_report_by_name(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        customexport.mk_report(self.conf.key, "Potter")
        potter_report = customexport.get_report_by_name(self.conf.key, "Potter")
        self.assertIsNotNone(potter_report)
        self.assertEquals("Potter", potter_report.report_name())

        customexport.mk_report(self.conf.key, "Weesley")
        weesley_report = customexport.get_report_by_name(self.conf.key, "Weesley")
        self.assertIsNotNone(weesley_report)
        self.assertEquals("Weesley", weesley_report.report_name())

    def test_delete_report(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        potter_report = customexport.mk_report(self.conf.key, "Potter")
        weesley_report = customexport.mk_report(self.conf.key, "Weesley")
        self.assertEquals(["Potter", "Weesley"], customexport.list_all_report_names(self.conf.key))

        potter_report.get().delete_report()

        self.assertEquals(["Weesley"], customexport.list_all_report_names(self.conf.key))
        self.assertIsNone(customexport.get_report_by_name(self.conf.key, "Potter"))

        weesley_report.get().delete_report()
        self.assertIsNone(customexport.get_report_by_name(self.conf.key, "Weesley"))

    def test_set_name(self):
        self.assertEquals([], customexport.list_all_report_names(self.conf.key))

        potter_report = customexport.mk_report(self.conf.key, "Potter")
        self.assertIsNone(customexport.get_report_by_name(self.conf.key, "Weesley"))

        potter_report.get().set_name("Weesley")
        self.assertIsNotNone(customexport.get_report_by_name(self.conf.key, "Weesley"))

    def test_submission_options(self):
        potter_report_key = customexport.mk_report(self.conf.key, "Potter")
        potter_report = potter_report_key.get()
        self.assertEquals([], potter_report.submission_options())

        potter_report.add_submission_options(["Hedwig"])
        self.assertEquals(["Hedwig"], potter_report.submission_options())

        potter_report.replace_submission_options(["Ernie", "Meenie", "Moo"])
        self.assertEquals(["Ernie", "Meenie", "Moo"], potter_report.submission_options())

    @patch('reports.customexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_excel_export_basic(self, mock_storage_open, mock_sheet_write):
        potter_report_key = customexport.mk_report(self.conf.key, "Potter")
        potter_report = potter_report_key.get()

        self.assertEquals(0, mock_storage_open.call_count)
        url = potter_report.export_submissions_to_excel([])
        self.assertEquals(1, mock_storage_open.call_count)
        self.assertEquals("https:///mimas-aotb.appspot.com.storage.googleapis.com/Potter", url[0:61])

        # nothing to export
        self.assertEquals(0, mock_sheet_write.call_count)

        # add some headers
        potter_report.add_submission_options(["created", "track", "format", "decision1"])
        potter_report.export_submissions_to_excel([])
        self.assertEquals(4, mock_sheet_write.call_count)

        self.assertEquals( (1,1, "Date and time created"), mock_sheet_write.mock_calls[0][1][1:])
        self.assertEquals( (1,2, "Track"), mock_sheet_write.mock_calls[1][1][1:])
        self.assertEquals( (1,3, "Format"), mock_sheet_write.mock_calls[2][1][1:])
        self.assertEquals( (1,4, "Decision round 1"), mock_sheet_write.mock_calls[3][1][1:])

    @patch('reports.customexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_excel_export_with_data(self, mock_storage_open, mock_sheet_write):
        sub_report_key = customexport.mk_report(self.conf.key, "SubmissionRecord")
        sub_report = sub_report_key.get()
        self.assertEquals([], sub_report.submission_options())

        sub_report.add_submission_options([])
        sub_report.add_submission_options(["created", "grdp_agreed", "track", "duration", "decision1", "decision2",
                                           "format", "withdrawn", "speaker_comms", "expenses",
                                           "title", "short_synopsis", "long_synopsis",
                                           "email", "first_name", "last_name", "picture", "blog",
                                           "cospeakers",
                                          ])

        # add some detail to conference to check mappings
        track_option = confoptions.make_conference_track(self.conf.key, "New Track")
        time_option = confoptions.make_conference_option(confoptions.DurationOption, self.conf.key, "30 minutes")
        format_option = confoptions.make_conference_option(confoptions.TalkFormatOption, self.conf.key, "Lecture")
        expenses_option = confoptions.make_conference_option(confoptions.ExpenseOptions, self.conf.key, "Longhaul")

        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts.com")
        spk = spk_key.get()
        spk.set_first_name("Harry")
        spk.set_later_names("J Potter")
        spk.set_field(speaker.Speaker.FIELD_BLOG, "www.myblog.com")
        spk.put()

        t1 = talk.Talk(parent=spk_key)
        t1.title = "Talk T1"
        t1.set_field("shortsynopsis", "Very short synopsis")
        t1.set_field("longsynopsis", "A much much longer synopsis that goes on and on")
        t1.put()
        sub = submissionrecord.make_submission_plus(t1.key,
                                                    self.conf.key,
                                                    track_option.shortname(),
                                                    format_option.shortname(),
                                                    time_option.shortname(),
                                                    expenses_option.shortname()).get()
        sub.set_review_decision(1, "Shortlist")
        sub.set_review_decision(2, "Decline")

        cospeaker.make_cospeaker(sub.key, "Ron Weesley", "ron@howarts.com")
        cospeaker.make_cospeaker(sub.key, "H Granger", "hgranger@howarts.com")

        sub_report.export_submissions_to_excel([sub.key])
        self.assertEquals(38, mock_sheet_write.call_count)

        # test header row
        call_cnt = 0
        header_row=1
        # cell A1 (1,1) contains "created"
        self.assertEquals((header_row,1,"Date and time created"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        self.assertEquals((header_row,2,"Agreed GDPR policy"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        self.assertEquals((header_row,3,"Track"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 4, "Length"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 5, "Decision round 1"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 6, "Decision round 2"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 7, "Format"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 8, "Withdrawn"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 9, "Communication"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 10, "Expenses"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 11, "Talk title"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 12, "Short synopsis"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 13, "Long synopsis"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 14, "Email"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 15, "First name"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 16, "Later names"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 17, "Picture"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 18, "Blog"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 19, "Co-speakers"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        # test data rows
        data_row1 = 2
        # worksheet entry for Created (cell 2,1)
        self.assertEquals((data_row1, 1), mock_sheet_write.mock_calls[call_cnt][1][1:3])
        # datetime.now hasn't been stubbed so just test it is not empty
        self.assertIsNot(0, len(mock_sheet_write.mock_calls[call_cnt][1][3]))
        call_cnt += 1

        # worksheet entry for GDPR (cell 2,2)
        self.assertEquals((data_row1, 2, "False"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        self.assertEquals((data_row1, 3, "New Track"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 4, "30 minutes"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 5, "Shortlist"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 6, "Decline"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 7, "Lecture"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 8, "False"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 9, submissionnotifynames.SUBMISSION_NEW), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 10, "Longhaul"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 11, "Talk T1"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 12, "Very short synopsis"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 13, "A much much longer synopsis that goes on and on"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 14, "harry@hogwarts.com"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 15, "Harry"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 16, "J Potter"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 17, "/sorry_page?reason=NoImage"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 18, "www.myblog.com"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 19, "Ron Weesley (ron@howarts.com), H Granger (hgranger@howarts.com)"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

    def test_excel_export_with_multiple_rows(self):
        # TO DO ------------------------------------
        # TEST MULTIPLE ROWS
        pass
