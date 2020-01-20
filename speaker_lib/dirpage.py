#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import speakerdir
from scaffold import tags
import basehandler


class SpeakerDirectoryPage(basehandler.BaseHandler):
    def show_page(self, speakers, tag_filter):
        template_values = {
            "speakers": speakers,
            "taglist": tags.taglist_func,
            "tag_filter": tag_filter,
        }

        self.write_page('speaker_lib/dirpage.html', template_values)

    def get(self):
        self.show_page(speakerdir.SpeakerDir().get_speaker_list(), "")

    def post(self):
        if self.request.get("searchtags"):
            self.search_tags()

        if self.request.get("clear_tags"):
            self.get()

    def search_tags(self):
        speakers = tags.search_tags(self.request.get("searchbox"))
        self.show_page(speakers, self.request.get("searchbox"))