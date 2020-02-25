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

        self.assertEquals( (0,0, "Date and time created"), mock_sheet_write.mock_calls[0][1][1:])
        self.assertEquals( (0,1, "Track"), mock_sheet_write.mock_calls[1][1][1:])
        self.assertEquals( (0,2, "Format"), mock_sheet_write.mock_calls[2][1][1:])
        self.assertEquals( (0,3, "Decision round 1"), mock_sheet_write.mock_calls[3][1][1:])

    @patch('reports.customexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_excel_export_with_data(self, mock_storage_open, mock_sheet_write):
        sub_report_key = customexport.mk_report(self.conf.key, "AllTheFieldsReport")
        sub_report = sub_report_key.get()
        self.assertEquals([], sub_report.submission_options())

        sub_report.add_submission_options(["created", "grdp_agreed", "track", "duration", "decision1", "decision2",
                                           "format", "withdrawn", "speaker_comms", "expenses",
                                           "title", "short_synopsis", "long_synopsis",
                                           "email", "first_name", "last_name", "picture", "blog",
                                           "cospeakers", "address"
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
        zurich = "Z\xc3\xbcric"
        spk.set_field(speaker.Speaker.FIELD_ADDRESS, zurich)
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
        self.assertEquals(40, mock_sheet_write.call_count)

        # test header row
        call_cnt = 0
        header_row=0
        # cell A1 (1,1) contains "created"
        self.assertEquals((header_row,0,"Date and time created"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        self.assertEquals((header_row,1,"Agreed GDPR policy"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        self.assertEquals((header_row,2,"Track"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 3, "Length"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 4, "Decision round 1"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 5, "Decision round 2"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 6, "Format"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 7, "Withdrawn"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 8, "Communication"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 9, "Expenses"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 10, "Talk title"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 11, "Short synopsis"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 12, "Long synopsis"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 13, "Email"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 14, "First name"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 15, "Later names"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 16, "Picture"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 17, "Blog"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 18, "Co-speakers"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 19, "Address"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        # test data rows
        data_row1 = 1
        # worksheet entry for Created (cell 2,1) - excel is zero based so A1 is 0,0
        self.assertEquals((data_row1, 0), mock_sheet_write.mock_calls[call_cnt][1][1:3])
        # datetime.now hasn't been stubbed so just test it is not empty
        self.assertIsNot(0, len(mock_sheet_write.mock_calls[call_cnt][1][3]))
        call_cnt += 1

        # worksheet entry for GDPR (cell 2,2)
        self.assertEquals((data_row1, 1, "False"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        self.assertEquals((data_row1, 2, "New Track"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 3, "30 minutes"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 4, "Shortlist"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 5, "Decline"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 6, "Lecture"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 7, "False"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 8, submissionnotifynames.SUBMISSION_NEW), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 9, "Longhaul"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 10, "Talk T1"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 11, "Very short synopsis"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 12, "A much much longer synopsis that goes on and on"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 13, "harry@hogwarts.com"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 14, "Harry"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 15, "J Potter"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        # odd return on local but server address makes sense when live
        self.assertEquals((data_row1, 16, "https:///sorry_page?reason=NoImage"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 17, "www.myblog.com"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 18, "Ron Weesley (ron@howarts.com), H Granger (hgranger@howarts.com)"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row1, 19, "Z\xc3\xbcric"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

    @patch('reports.customexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_excel_export_with_multiple_rows(self, mock_storage_open, mock_sheet_write):
        sub_report_key = customexport.mk_report(self.conf.key, "MultipleRowsReport")
        sub_report = sub_report_key.get()
        sub_report.add_submission_options(["grdp_agreed", "speaker_comms",
                                            "title",
                                            "email", "first_name", "last_name"
                                            ])

        # submission 1
        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts.com")
        spk = spk_key.get()
        spk.set_first_name("Harry")
        spk.set_later_names("J Potter")
        spk.put()

        harry_talk = talk.Talk(parent=spk_key)
        harry_talk.title = "Harry talks"
        harry_talk.put()
        sub_key = submissionrecord.make_submission_plus(harry_talk.key, self.conf.key, None, None, None, None)

        # submission 2
        spk_key2 = speaker.make_and_store_new_speaker("Hermione@hogwarts.com")
        spk2 = spk_key2.get()
        spk2.set_first_name("Hermione")
        spk2.set_later_names("Granger")
        spk2.put()

        hammy_talk = talk.Talk(parent=spk_key2)
        hammy_talk.title = "Hermione talks"
        hammy_talk.put()
        sub_key2 = submissionrecord.make_submission_plus(hammy_talk.key, self.conf.key, None, None, None, None)

        sub_report.export_submissions_to_excel([sub_key, sub_key2])
        self.assertEquals(18, mock_sheet_write.call_count)

        call_cnt = 0
        header_row=0
        self.assertEquals((header_row, 0,"Agreed GDPR policy"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 1, "Communication"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 2, "Talk title"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 3, "Email"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 4, "First name"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((header_row, 5, "Later names"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        data_row = 1
        self.assertEquals((data_row, 0, "False"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 1, submissionnotifynames.SUBMISSION_NEW), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 2, "Harry talks"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 3, "harry@hogwarts.com"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 4, "Harry"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 5, "J Potter"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1

        data_row = 2
        self.assertEquals((data_row, 0, "False"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 1, submissionnotifynames.SUBMISSION_NEW), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 2, "Hermione talks"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 3, "Hermione@hogwarts.com"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 4, "Hermione"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
        self.assertEquals((data_row, 5, "Granger"), mock_sheet_write.mock_calls[call_cnt][1][1:])
        call_cnt += 1
