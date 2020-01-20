#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from conference_lib import conference
from conference_lib import confoptions
from reports import exportcsv
from speaker_lib import speaker, cospeaker
from submission_lib import submissionrecord
from talk_lib import talk


class MockOutStream:
    def __init__(self):
        self.write_count = 0
        self.sequence = {}

    def write(self, str):
        self.sequence[self.write_count] = str
        self.write_count = self.write_count + 1

    def number_of_writes(self):
        return self.write_count

    def reset(self):
        self.write_count = 0

class TestExportCsv(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_field_access(self):
        t = talk.Talk()
        self.assertEquals(t.title, "")
        t.title = "Wonderful"
        self.assertEquals(t.title, "Wonderful")
        self.assertEquals(t.title, "Wonderful".encode('ascii', 'ignore'))

    def test_single_quotes_inside(self):
        src = exportcsv.single_quotes_inside('quote "qo" quote')
        self.assertEquals(src, "quote 'qo' quote")

        src = exportcsv.single_quotes_inside("single 'quotes' untouched")
        self.assertEquals(src, "single 'quotes' untouched")

        src = exportcsv.single_quotes_inside("unmatched ' still unmatched")
        self.assertEquals(src, "unmatched ' still unmatched")

        src = exportcsv.single_quotes_inside('unmatched " still unmatched but changed')
        self.assertEquals(src, "unmatched ' still unmatched but changed")

    def test_add_quotes(self):
        self.assertEquals(exportcsv.add_quotes('allan'), '"allan"')

    def test_write_with_comma(self):
        output = MockOutStream()
        exportcsv.write_with_comma(output, "allan")
        self.assertEquals(output.sequence[0], "allan, ")

        exportcsv.write_with_comma(output, None)
        self.assertEquals(output.sequence[1], ", ")

    def test_export_submission(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()
        track1 = confoptions.make_conference_track(c.key, "track")
        format1 = confoptions.make_conference_option(confoptions.TalkFormatOption, c.key, "lecture")
        duration1 = confoptions.make_conference_option(confoptions.DurationOption, c.key, "10mins")
        expenses1 = confoptions.make_conference_option(confoptions.ExpenseOptions, c.key, "Long haul")

        s = speaker.make_new_speaker("arnold@reddwarf.com")
        s.name = 'Arnold "J" Rimmer'
        s.telephone = "051 652 0538"
        s.address = "Cabin 42, Deck 3, Red Dwarf"
        s.set_field("affiliation", "Mining Corp")
        s.set_field("twitter", "@arnold")
        s.bio = "Arnold 'J' Rimmer joined Mining Corp (Space Division) at, what now seems, a very young age."
        s.set_field("experience", "None at all")
        s.put()

        t = talk.Talk(parent=s.key)
        t.title = "A testing talk"
        t.set_field(talk.SHORT_SYNOPSIS, "A few words about the tests you need")
        t.set_field(talk.LONG_SYNOPSIS, "Many more words about testing.... 1, 2, 3")
        t.put()

        sub_key = submissionrecord.make_submission_plus(t.key, c.key,
                                                        track1.shortname(), format1.shortname(),
                                                        duration1.shortname(), expenses1.shortname())

        cospeak = cospeaker.make_cospeaker(sub_key, "Harry Potter", "hpotter@hogwarts.org")

        output = MockOutStream()
        exportcsv.write_sub(output, sub_key.get())

        self.assertEquals(output.sequence[0], 'No decision, ')
        self.assertEquals(output.sequence[1], "Arnold 'J' Rimmer, ")
        self.assertEquals(output.sequence[2], 'arnold@reddwarf.com, ')
        self.assertEquals(output.sequence[3], '051 652 0538, ')
        self.assertEquals(output.sequence[4], '"Cabin 42, Deck 3, Red Dwarf", ')
        self.assertEquals(output.sequence[5], 'Harry Potter, ')
        self.assertEquals(output.sequence[6], ', ')
        self.assertEquals(output.sequence[7], 'Mining Corp, ')
        self.assertEquals(output.sequence[8], '@arnold, ')
        self.assertEquals(output.sequence[9], """"Arnold 'J' Rimmer joined Mining Corp (Space Division) at, what now seems, a very young age.", """)
        self.assertEquals(output.sequence[10], 'None at all, ')
        self.assertEquals(output.sequence[11], 'None, ')

        self.assertEquals(output.sequence[12], 'A testing talk, ')
        self.assertEquals(output.sequence[13], "A few words about the tests you need, ")
        self.assertEquals(output.sequence[14], '"Many more words about testing.... 1, 2, 3", ')

        self.assertEquals(output.sequence[15], 'track, ')
        self.assertEquals(output.sequence[16], 'lecture, ')
        self.assertEquals(output.sequence[17], '10mins, ')
        self.assertEquals(output.sequence[18], 'Long haul, ')

        self.assertEquals(output.number_of_writes(), 19)

    def test_export_submissions_list(self):
        c = conference.Conference()
        c.name = "TestConf"
        c.put()
        track1 = confoptions.make_conference_track(c.key, "track")
        track2 = confoptions.make_conference_track(c.key, "another track")
        format1 = confoptions.make_conference_option(confoptions.TalkFormatOption, c.key, "lecture")
        duration1 = confoptions.make_conference_option(confoptions.DurationOption, c.key, "10mins")
        expenses1 = confoptions.make_conference_option(confoptions.ExpenseOptions, c.key, "Money")

        s = speaker.make_new_speaker("arnold@reddwarf.com")
        s.put()
        t = talk.Talk(parent=s.key)
        t.title = "A testing talk"
        t.put()
        sub_key = submissionrecord.make_submission_plus(t.key, c.key, track1.shortname(),
                                                        format1.shortname(), duration1.shortname(),
                                                        expenses1.shortname())

        s2 = speaker.make_new_speaker("lister@reddwarf.com")
        s2.put()
        t2 = talk.Talk(parent=s2.key)
        t2.title = "Knowing Rimmer"
        t2.put()
        sub_key2 = submissionrecord.make_submission_plus(t2.key, c.key, track2.shortname(),
                                                         format1.shortname(), duration1.shortname(),
                                                         expenses1.shortname())

        output = MockOutStream()
        exportcsv.write_sub_list(output, [sub_key, sub_key2])
        self.assertEquals(output.number_of_writes(), 40)

    def test_header_row(self):
        output = MockOutStream()
        exportcsv.write_title_row(output)
        self.assertEquals(output.number_of_writes(), 19)

