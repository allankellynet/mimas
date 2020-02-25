#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
from scaffold import sysinfo, image, tags
import speakerdir

class Speaker(ndb.Model):
    FIELD_WEBPAGE = "Webpage"
    FIELD_BLOG = "Blog"
    FIELD_LINKEDIN = "Linkedin"
    FIELD_COUNTRY = "country"
    FIELD_TWITTER = "twitter"
    FIELD_AFFILICATION = "affiliation"
    FIELD_TELEPHONE = "Telephone"
    FIELD_ADDRESS = "Address"
    FIELD_JOBTITLE = "JobTitle"

    speaker_email = ndb.StringProperty()
    profile = ndb.PickleProperty()
    picture = ndb.BlobProperty()    # Small picture deprecated
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    fullsize_picture = ndb.BlobProperty() # Full size image deprecated
    zero_deleted = ndb.BooleanProperty()

    def __init__(self, *args, **kwargs):
        super(Speaker, self).__init__(*args, **kwargs)
        self.zero_deleted = False

    @property
    def name(self):
        if self.profile.has_key("first_name") or self.profile.has_key("later_names"):
            return self.concat_name_parts()

        return self.profile["name"]

    @name.setter
    def name(self, n):
        self.profile["name"] = n

    def set_names(self, first, later_names):
        self.profile["first_name"] = first
        self.profile["later_names"] = later_names

    def concat_name_parts(self):
        if self.profile.has_key("first_name") and self.profile.has_key("later_names"):
            return self.profile["first_name"] + " " + self.profile["later_names"]

        if self.profile.has_key("first_name"):
            return self.profile["first_name"]

        if self.profile.has_key("later_names"):
            return self.profile["later_names"]

        return ""

    def first_name(self):
        if self.profile.has_key("first_name"):
            return self.profile["first_name"]

        if self.profile.has_key("name"):
            # legacy data
            return split_name_into_two_parts(self.profile["name"])[0]

        return ""

    def set_first_name(self, first_name):
        self.profile["first_name"] = first_name

    def later_names(self):
        if self.profile.has_key("later_names"):
            return self.profile["later_names"]

        if self.profile.has_key("name"):
            # legacy data
            return split_name_into_two_parts(self.profile["name"])[1]

        return ""

    def set_later_names(self, later_names):
        self.profile["later_names"] = later_names

    @property
    def email(self):
        return self.speaker_email

    @email.setter
    def email(self, address):
        self.speaker_email = address

    @property
    def telephone(self):
        return self.profile["phone"]

    @telephone.setter
    def telephone(self, num):
        self.profile["phone"] = num

    @property
    def address(self):
        return self.profile["address"]

    @address.setter
    def address(self, addr):
        self.profile["address"] = addr

    @property
    def bio(self):
        return self.profile["bio"]

    @bio.setter
    def bio(self, bibliography):
        self.profile["bio"] = bibliography
        self.profile["bio"] = bibliography

    def field(self, f):
        if self.profile.has_key(f):
            return self.profile[f]
        else:
            return ""

    def set_field(self, f, value):
        self.profile[f] = value

    def has_full_size_image(self):
        # Todo: refactor out this dependency on image
        return image.image_exists(self.key)

    def full_image_url(self):
        if image.image_exists(self.key):
            return sysinfo.home_url() + "/speakerfullimg?spk_id=" + self.key.urlsafe()
        else:
            return sysinfo.home_url() + "/sorry_page?reason=NoImage"

    def set_empty_profile(self, email):
        self.speaker_email = email
        self.profile = {"name": "",
                     "phone": "",
                     "address": "",
                     "bio": ""}
        return self

    def zero_out_speaker(self):
        speakerdir.SpeakerDir().remove_speaker(self.key)
        tags.TagList(self.key).remove_all_tags()
        self.set_empty_profile("none@deleted.mimascr.com")
        image.delete_image(self.key)
        self.zero_deleted = True
        self.put()

    def is_zero_deleted(self):
        return self.zero_deleted

def speaker_exists(email):
    count = Speaker.query(Speaker.speaker_email == email).count()
    return count > 0

def retreive_speaker(email):
    return Speaker.query(Speaker.speaker_email == email).fetch()[0]

def make_new_speaker(email):
    s = Speaker()
    return s.set_empty_profile(email)

def make_and_store_new_speaker(email):
    s = make_new_speaker(email)
    return s.put()

def make_speaker_from_proto(proto):
    s = make_new_speaker(proto.email())
    names = split_name_into_two_parts(proto.name())
    s.set_names(names[0], names[1])
    return s

def retrieve_or_make(email):
    speaker = Speaker.query(Speaker.speaker_email == email).fetch()
    if len(speaker)>0:
        return speaker[0]
    else:
        s = make_new_speaker(email)
        s.put()
        return s

def part_or_null(parts, idx):
    if len(parts)>idx:
        return parts[idx]

    return ""

def split_name_into_two_parts(name):
    parts = name.split(" ", 1)
    return (part_or_null(parts, 0), part_or_null(parts, 1))

def eat_leading_duplicates(lst):
    if len(lst) >= 1:
        if lst[0].speaker_email == lst[1].speaker_email:
            return eat_leading_duplicates(lst[1:])

    return lst

def search_list_for_duplicates(lst):
    if len(lst) <= 1:
        return []

    if lst[0].speaker_email == lst[1].speaker_email:
        return [lst[0]] + search_list_for_duplicates(eat_leading_duplicates(lst[1:]))

    return search_list_for_duplicates(lst[1:])

def find_duplicate_speakers():
    return search_list_for_duplicates(Speaker.query().order(Speaker.speaker_email).fetch())


