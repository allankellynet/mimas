#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

from google.appengine.ext import ndb

# Local imports
from scaffold import tags
import basehandler


class EditTagsPage(basehandler.BaseHandler):
    def get(self):
        speaker = None
        talk = None
        tag_list = []

        if self.request.params.has_key("spk"):
            tag_type = "Speaker"
            speaker = ndb.Key(urlsafe=self.request.get("spk")).get()
            tags_list = tags.TagList(speaker.key).pretty_tag_list([tag_type])
            parent_key = speaker.key.urlsafe()

        if self.request.params.has_key("talk"):
            tag_type="Talk"
            talk = ndb.Key(urlsafe=self.request.get("talk")).get()
            tags_list = tags.TagList(talk.key).pretty_tag_list([tag_type])
            parent_key = talk.key.urlsafe()

        template_values = {
            "speaker":      speaker,
            "talk":         talk,
            "parent_key":   parent_key,
            "tags":         tags_list,
            "tag_type":     tag_type,
            "all_tags":     tags.retrieve_all_unique_tags(),
        }

        self.write_page("scaffold/edittags.html", template_values)

    def post(self):
        parent_key = ndb.Key(urlsafe=self.request.get("parent_key"))
        if self.request.get("remove_tag"):
            tags.TagList(parent_key).remove_tag(self.request.get("newtag"), [self.request.get("tag_type")])

        if self.request.get("tag_type") == "Speaker":
            self.redirect("/edittags?spk=" + parent_key.urlsafe())
        else:
            self.redirect("/edittags?talk=" + parent_key.urlsafe())

class AddTagPost(basehandler.BaseHandler):
    def post(self):
        k = ndb.Key(urlsafe=self.request.get("key"))
        tags.TagList(k).add_tag(self.request.get("tag"), self.request.get("tag_type"))
