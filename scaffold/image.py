#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb


# app imports


class MimasImage(ndb.Model):
    picture = ndb.BlobProperty()


def image_exists(key):
    if key==None:
        return None

    images = MimasImage.query(ancestor=key).count()
    return images > 0

def store_only_image(key, image):
    if len(image) < 1:
        return None
    
    existing_images = MimasImage.query(ancestor=key).fetch(10, keys_only=True)
    if len(existing_images)>0:
        for i in existing_images:
            i.delete()

    conf_image = MimasImage(parent=key)
    conf_image.picture = image
    conf_image.put()
    return conf_image.key

def retrieve_image_key(key):
    images = MimasImage.query(ancestor=key).fetch(1, keys_only=True)
    if len(images)>0:
        return images[0]
    else:
        return None

def delete_image(key):
    images = MimasImage.query(ancestor=key).fetch(1, keys_only=True)
    if len(images)>0:
        images[0].delete()

def convert_speaker_full_image_to_mimas_image(spkr):
    if spkr.fullsize_picture == None:
        return

    store_only_image(spkr.key, spkr.fullsize_picture)
    spkr.fullsize_picture = None
    spkr.put()

def convert_speaker_list_full_image_to_mimas_image(spk_list):
    for s in spk_list:
        convert_speaker_full_image_to_mimas_image(s.get())
