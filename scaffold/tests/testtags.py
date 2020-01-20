#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest

from google.appengine.ext import testbed

from scaffold import sysinfo
from speaker_lib import speaker
from scaffold.tags import TagList
from scaffold import tags
from talk_lib import talk

class TestTags(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_add_remove_one_tag(self):
        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts")

        self.assertEquals(0, len(TagList(spk_key).get_all_tags([])))

        new_tag_key = TagList(spk_key).add_tag("Tag1", "Speaker")
        self.assertEquals("Tag1", new_tag_key.get().tag_text)

        self.assertEquals(1, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals("Tag1", TagList(spk_key).get_all_tags([])[0])

        TagList(spk_key).add_tag("Tag2", "Speaker")
        TagList(spk_key).add_tag("Tag3", "Speaker")
        self.assertEquals(3, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals(["Tag1", "Tag2", "Tag3"], TagList(spk_key).get_all_tags([]))

        TagList(spk_key).remove_tag("Tag2", ["Speaker"])
        self.assertEquals(2, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals(["Tag1", "Tag3"], TagList(spk_key).get_all_tags([]))

    def test_pretty_tag_list(self):
        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts")

        self.assertEquals(0, len(TagList(spk_key).get_all_tags([])))

        TagList(spk_key).add_tag_list(["Tag1", "Tag2", "Tag3"], "Speaker")
        self.assertEquals(3, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals("Tag1, Tag2, Tag3", TagList(spk_key).pretty_tag_list([]))

    def test_remove_all_tags(self):
        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts")
        TagList(spk_key).add_tag_list(["Tag1", "Tag2", "Tag3"], "Speaker")
        TagList(spk_key).remove_all_tags()
        self.assertEquals(0, len(TagList(spk_key).get_all_tags([])))

    def test_all_unique_tags(self):
        self.assertSetEqual(set(), tags.retrieve_all_unique_tags())

        spk_key1 = speaker.make_and_store_new_speaker("harry@hogwarts")
        TagList(spk_key1).add_tag_list(["Tag1", "Tag2", "Tag3"], "Speaker")

        expected = set(["Tag1", "Tag2", "Tag3"])
        self.assertSetEqual(expected, tags.retrieve_all_unique_tags())

        spk_key2 = speaker.make_and_store_new_speaker("ron@hogwarts")
        TagList(spk_key2).add_tag_list(["Tag1", "Tag20", "Tag30"], "Other")

        expected = set(["Tag1", "Tag2", "Tag3", "Tag20", "Tag30"])
        self.assertSetEqual(expected, tags.retrieve_all_unique_tags())

    def test_taglist_func(self):
        direct_creation = TagList(None)
        indirect_creation = tags.taglist_func(None)
        self.assertEqual(type(direct_creation), type(indirect_creation))

    def test_split_tag_list(self):
        self.assertEquals(["ron", "harry potter", "malfoy", "hammi"],
                            tags.split_tag_list("ron, harry potter, malfoy,hammi"))


    def test_tag_search(self):
        spk_key1 = speaker.make_and_store_new_speaker("harry@hogwarts")
        TagList(spk_key1).add_tag_list(["Tag1", "Tag2", "Tag3"], "Speaker")


        self.assertEquals(frozenset([spk_key1]), tags.search_tags("Tag1"))
        self.assertEquals(frozenset([spk_key1]), tags.search_tags("Tag2"))
        self.assertEquals(frozenset([spk_key1]), tags.search_tags("Tag1, Tag2"))
        self.assertEquals(frozenset(), tags.search_tags("TagX"))

        spk_key2 = speaker.make_and_store_new_speaker("harry@hogwarts")
        TagList(spk_key2).add_tag_list(["Tag1"], "Speaker")

        self.assertSetEqual(frozenset([spk_key1, spk_key2]), (tags.search_tags("Tag1")))
        self.assertSetEqual(frozenset([spk_key1]), (tags.search_tags("Tag1, Tag2")))
        self.assertEquals(frozenset(), tags.search_tags("TagX"))


    def test_different_tag_types(self):
        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts")
        new_tag_key = TagList(spk_key).add_tag("Tag1", "Talk")
        self.assertEquals("Tag1", new_tag_key.get().tag_text)

        self.assertEquals(1, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals(1, len(TagList(spk_key).get_all_tags(["Talk"])))
        self.assertEquals(0, len(TagList(spk_key).get_all_tags(["Speaker"])))
        self.assertEquals(1, len(TagList(spk_key).get_all_tags(["Speaker", "Talk"])))
        self.assertEquals("Tag1", TagList(spk_key).get_all_tags(["Talk"])[0])

        TagList(spk_key).add_tag("SpeakerTag2", "Speaker")
        self.assertEquals(1, len(TagList(spk_key).get_all_tags(["Talk"])))
        self.assertEquals(1, len(TagList(spk_key).get_all_tags(["Speaker"])))
        self.assertEquals(2, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals(2, len(TagList(spk_key).get_all_tags(["Speaker", "Talk"])))

        TagList(spk_key).add_tag("TalkTag3", "Talk")
        self.assertEquals(3, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals(["Tag1", "SpeakerTag2", "TalkTag3"], TagList(spk_key).get_all_tags([]))
        self.assertEquals(["SpeakerTag2"], TagList(spk_key).get_all_tags(["Speaker"]))
        self.assertEquals(["Tag1", "TalkTag3"], TagList(spk_key).get_all_tags(["Talk"]))

        TagList(spk_key).remove_tag("TalkTag3", ["Talk"])
        self.assertEquals(2, len(TagList(spk_key).get_all_tags([])))
        self.assertEquals(1, len(TagList(spk_key).get_all_tags(["Talk"])))
        self.assertEquals(1, len(TagList(spk_key).get_all_tags(["Speaker"])))

    def test_remove_different_tags(self):
        spk_key = speaker.make_and_store_new_speaker("harry@hogwarts")
        TagList(spk_key).add_tag("GenericTag1", "Speaker")
        TagList(spk_key).add_tag("GenericTag2", "Speaker")
        TagList(spk_key).add_tag("SpeakerTag3", "Speaker")

        talk_key = talk.mk_talk(spk_key, "Talking")
        TagList(talk_key).add_tag("GenericTag1", "Talk")
        TagList(talk_key).add_tag("GenericTag2", "Talk")
        TagList(talk_key).add_tag("TalkTag4", "Talk")

        self.assertEqual(["GenericTag1", "GenericTag2", "TalkTag4"], TagList(talk_key).get_all_tags([]))
        self.assertEqual(6, len(TagList(spk_key).get_all_tags([])))
        self.assertSetEqual(frozenset(["GenericTag1", "GenericTag2", "SpeakerTag3", "TalkTag4"]),
                            TagList(spk_key).get_unique_tags())

        TagList(talk_key).remove_tag("GenericTag1", ["Talk"])
        self.assertEquals(["GenericTag2", "TalkTag4"], TagList(talk_key).get_all_tags([]))
        self.assertEquals(5, len(TagList(spk_key).get_all_tags([])))
        self.assertSetEqual(frozenset(["GenericTag1", "GenericTag2", "SpeakerTag3", "TalkTag4"]),
                            TagList(spk_key).get_unique_tags())

        TagList(spk_key).remove_tag("GenericTag2", ["Speaker"])
        self.assertEquals(["GenericTag2", "TalkTag4"], TagList(talk_key).get_all_tags([]))
        self.assertEquals(4, len(TagList(spk_key).get_all_tags([])))
        self.assertSetEqual(frozenset(["GenericTag1", "GenericTag2", "SpeakerTag3", "TalkTag4"]),
                          TagList(spk_key).get_unique_tags())
        self.assertEquals(["GenericTag1", "SpeakerTag3"], TagList(spk_key).get_all_tags(["Speaker"]))

