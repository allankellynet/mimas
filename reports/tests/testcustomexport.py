#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from mock import Mock, patch, call
import mock

from google.appengine.ext import testbed

from conference_lib import conference
from reports import customexport, exportexcel
from talk_lib import talk
from submission_lib import submissionrecord

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
        potter_report.add_submission_options(["Gryffindor", "Ravenclaw", "Slytherin", "Hufflepuff"])
        potter_report.export_submissions_to_excel([])
        self.assertEquals(4, mock_sheet_write.call_count)

        # multiple asserts appears long winded, should be closer to
        #self.assertEquals(worksheet_object, mock_sheet_write.mock_calls[0][1])
        # but
        # a. worksheet object is a memory location so will change
        # b. "ValueError: too many values to unpack"

        self.assertEquals(1, mock_sheet_write.mock_calls[0][1][1])
        self.assertEquals(1, mock_sheet_write.mock_calls[0][1][2])
        self.assertEquals("Gryffindor", mock_sheet_write.mock_calls[0][1][3])

        self.assertEquals("Ravenclaw", mock_sheet_write.mock_calls[1][1][3])
        self.assertEquals("Slytherin", mock_sheet_write.mock_calls[2][1][3])

        self.assertEquals(1, mock_sheet_write.mock_calls[3][1][1])
        self.assertEquals(4, mock_sheet_write.mock_calls[3][1][2])
        self.assertEquals("Hufflepuff", mock_sheet_write.mock_calls[3][1][3])

    @patch('reports.customexport.worksheet_write_wrapper')
    @patch('cloudstorage.open')
    def test_excel_export_with_data(self, mock_storage_open, mock_sheet_write):
        print "???????????????????????????????????????????????????????????????????????"
        sub_report_key = customexport.mk_report(self.conf.key, "SubmissionRecord")
        sub_report = sub_report_key.get()
        self.assertEquals([], sub_report.submission_options())

        sub_report.add_submission_options(["created"])
        sub_report.add_submission_options(["grdp_agreed"])
        sub_report.add_submission_options(["track"])

        conf_key = None
        t1 = None # talk.Talk()
        #t1.title = "Talk T1"
        #t1.put()
        sub = submissionrecord.make_submission(t1, None, "track", "format").get()

        sub_report.export_submissions_to_excel([sub.key])
        self.assertEquals(6, mock_sheet_write.call_count)

        # test header row
        print mock_sheet_write.mock_calls[0][1]
        header_row=1
        # cell A1 (1,1) contains "created"
        self.assertEquals((header_row,1,"Date and time created"), mock_sheet_write.mock_calls[0][1][1:])

        print mock_sheet_write.mock_calls[1][1]
        self.assertEquals((header_row,2,"Agreed GDPR policy"), mock_sheet_write.mock_calls[1][1][1:])

        print mock_sheet_write.mock_calls[2][1]
        self.assertEquals((header_row,3,"Track"), mock_sheet_write.mock_calls[2][1][1:])

        # test data rows
        data_row1 = 2
        # worksheet entry for Created (cell 2,1)
        print mock_sheet_write.mock_calls[3][1]
        self.assertEquals((data_row1, 1), mock_sheet_write.mock_calls[3][1][1:3])
        # datetime.now hasn't been stubbed so just test it is not empty
        self.assertIsNot(0, len(mock_sheet_write.mock_calls[3][1][3]))

        # worksheet entry for GDPR (cell 2,2)
        self.assertEquals((data_row1, 2, "False"), mock_sheet_write.mock_calls[4][1][1:])

        self.assertEquals((data_row1, 3, "Track"), mock_sheet_write.mock_calls[5][1][1:])


        # TODO - before going live!!!!

        # 1. Add more fields - allow all submission record fields to be used
        # 2. Test multiple rows in export
        # 3. Add Talk
        # 4. Add Speaker
