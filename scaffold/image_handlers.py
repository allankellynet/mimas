#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

from google.appengine.ext import ndb

# Local imports
from scaffold import image
import basehandler


class SpeakerImage(basehandler.BaseHandler):
    def get(self):
        speaker_key = ndb.Key(urlsafe=self.request.get('spk_id'))
        if image.image_exists(speaker_key):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(image.retrieve_image_key(speaker_key).get().picture)
        else:
            self.response.out.write('No image')

class Image(basehandler.BaseHandler):
    def get(self):
        key = ndb.Key(urlsafe=self.request.get('img_id'))
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(key.get().picture)
