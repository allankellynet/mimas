#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

import confoptions
# app imports
from scaffold import userrights, openrights, image


# Not imported -> Keeping module dependency free
# Not import Submission Record
# Not import Talk


class Conference(ndb.Model):
    conf_name = ndb.StringProperty()
    conf_state = ndb.StringProperty()
    conf_dates = ndb.StringProperty()
    conf_review_comments_visible = ndb.BooleanProperty()
    conf_user_rights = None
    created = ndb.DateTimeProperty(auto_now_add=True)
    conf_shortname = ndb.StringProperty()
    conf_website = ndb.StringProperty()
    conf_gdpr_link = ndb.StringProperty()
    conf_cfp_address = ndb.StringProperty()
    conf_max_submissions = ndb.IntegerProperty()
    conf_contact_address = ndb.StringProperty()
    conf_creator = ndb.StringProperty()
    conf_cospeaker_limit = ndb.IntegerProperty()

    def __init__(self, *args, **kwargs):
        super(Conference, self).__init__(*args, **kwargs)
        self.conf_name = ""
        self.conf_dates = ""
        self.conf_state = "Closed"
        self.conf_review_comments_visible = False
        self.conf_user_rights = None
        self.conf_shortname = ""
        self.conf_website = ""
        self.conf_gdpr_link = ""
        self.conf_cfp_address = ""
        self.conf_max_submissions = 3
        self.conf_contact_address = ""
        self.conf_creator = ""
        self.conf_cospeaker_limit = 3

    def contact_email(self):
        return self.conf_contact_address

    def set_contact_email(self, address):
        self.conf_contact_address = address

    def max_submissions(self):
        return self.conf_max_submissions

    def set_max_submissions(self, limit):
        self.conf_max_submissions = limit

    def max_cospeakers(self):
        return self.conf_cospeaker_limit

    def set_max_cospeakers(self, limit):
        self.conf_cospeaker_limit = limit

    @property
    def name(self):
        return self.conf_name

    @name.setter
    def name(self, n):
        self.conf_name = n

    @property
    def shortname(self):
        return self.conf_shortname

    @shortname.setter
    def shortname(self, n):
        self.conf_shortname = n

    @property
    def creator_id(self):
        return self.conf_creator

    @creator_id.setter
    def creator_id(self, id):
        self.conf_creator = id

    @property
    def comments_visible(self):
        return self.conf_review_comments_visible

    def show_comments(self):
        self.conf_review_comments_visible = True
        self.put()

    def hide_comments(self):
        self.conf_review_comments_visible = False
        self.put()

    @property
    def dates(self):
        return self.conf_dates

    @dates.setter
    def dates(self, ds):
        self.conf_dates = ds

    def track_objects(self):
        return confoptions.TrackOption.query(ancestor=self.key).fetch()

    def track_options(self):
        return self.generic_options(confoptions.TrackOption)

    def mapped_track_obects(self):
        return dict(map(lambda x: [x.shortname_m, x], confoptions.TrackOption.query(ancestor=self.key).fetch()))

    def track_names(self, track_key_list):
        tracks = self.track_options()
        track_names = []
        for opt in track_key_list:
            track_names = track_names + [tracks[opt]]
        return track_names

    def tracks_string(self, track_key_list):
        return ', '.join(self.track_names(track_key_list))

    def generic_options(self, Option_Type):
        options = Option_Type.query(ancestor=self.key).fetch()
        map = {}
        for opt in options:
            map[opt.shortname()] = opt.full_text()
        return map

    def duration_options(self):
        return self.generic_options(confoptions.DurationOption)

    def delivery_format_options(self):
        return self.generic_options(confoptions.TalkFormatOption)

    def ack_cc_addresses(self):
        return self.generic_options(confoptions.AcknowledgementEmailCCAddresses)

    def ack_bcc_addresses(self):
        return self.generic_options(confoptions.AcknowledgementEmailBCCAddresses)

    def accept_cc_addresses(self):
        return self.generic_options(confoptions.AcceptEmailCCAddress)

    def pays_expenses(self):
        return True

    def expenses_options(self):
        return self.generic_options(confoptions.ExpenseOptions)

    def state(self):
        return self.conf_state

    def open_for_submissions(self):
        self.conf_state = "Open"
        self.put()

    def close_submissions(self):
        self.conf_state = "Closed"
        self.put()

    def start_round1_reviews(self):
        self.conf_state = "Round1Reviews"
        self.put()

    @property
    def is_round1(self):
        return self.conf_state == "Round1Reviews"

    def start_round2_reviews(self):
        self.conf_state = "Round2Reviews"
        self.put()

    @property
    def is_round2(self):
        return self.conf_state == "Round2Reviews"

    def finish_reviews(self):
        self.conf_state = "Finished"
        self.put()

    @property
    def is_reviewing_compete(self):
        return self.conf_state == "Finished"

    def user_rights(self):
        if self.key is None:
            return None
        elif self.is_dummy_conf():
            return openrights.OpenRights(self.key)
        else:
            return userrights.UserRights(self.key)

    def is_dummy_conf(self):
        return False

    def are_submissions_open(self):
        return self.conf_state == "Open"

    def website(self):
        return self.conf_website

    def set_website(self, url):
        self.conf_website = url

    def cfp_address(self):
        return self.conf_cfp_address

    def set_cfp_address(self, url):
        self.conf_cfp_address = url

    def gdpr_address(self):
        return self.conf_gdpr_link

    def set_gdpr_address(self, url):
        self.conf_gdpr_link  = url

    def has_image(self):
        return image.image_exists(self.key)

    def set_image(self, img):
        img_key = image.retrieve_image_key(self.key)
        if img_key != None:
            img_key.delete()

        return image.store_only_image(self.key, img)

    def get_image_key(self):
        return image.retrieve_image_key(self.key)

    def get_image(self):
        return self.get_image_key().get().picture
