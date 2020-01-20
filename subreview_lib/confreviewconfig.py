#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports
import logging

from google.appengine.ext import ndb

# Local imports


class ReviewConfigBase(ndb.Model):
    config_review_round = ndb.IntegerProperty()
    speaker_named = ndb.BooleanProperty()

    def __init__(self, *args, **kwargs):
        super(ReviewConfigBase, self).__init__(*args, **kwargs)
        self.config_review_round = 1
        self.speaker_named = True

    def name(self):
        return "Base"

    def review_round(self):
        return self.config_review_round

    def set_review_round(self, rround):
        self.config_review_round = rround
        self.put()

    def reviewpage(self):
        return "No review page"

    def decisionpage(self):
        return "No decision page"

    def has_config_options(self):
        return False

    def config_page(self):
        return ""

    def is_speaker_named(self):
        return self.speaker_named

    def set_speaker_anoymous(self):
        self.speaker_named = False
        self.put()

    def set_speaker_named(self, named_flag):
        self.speaker_named = named_flag

class ClassicReview(ReviewConfigBase):
    def name(self):
        return "Classic scoring"

    def reviewpage(self):
        return "classicreview"

    def decisionpage(self):
        return "classic_review_decisions"

class NewScoringReview(ReviewConfigBase):
    minimum_vote = ndb.IntegerProperty()
    maximum_vote = ndb.IntegerProperty()
    track_assignment_limit = ndb.PickleProperty()
    private_comments_flag = ndb.BooleanProperty()

    def __init__(self, *args, **kwargs):
        super(NewScoringReview, self).__init__(*args, **kwargs)
        self.minimum_vote = 1
        self.maximum_vote = 10
        self.track_assignment_limit = None
        self.private_comments_flag = True

    def name(self):
        return "New scoring"

    def reviewpage(self):
        return "scoringreview"

    def decisionpage(self):
        return "classic_review_decisions"

    def has_config_options(self):
        return True

    def config_page(self):
        return "newscoreconfigpage"

    def min_vote(self):
        return self.minimum_vote

    def set_min_vote(self, lower):
        self.minimum_vote = lower
        self.put()

    def max_vote(self):
        return self.maximum_vote

    def set_max_vote(self, upper):
        self.maximum_vote = upper
        self.put()

    def track_limits(self):
        if self.track_assignment_limit is None:
            self.track_assignment_limit = {}

        for t in self.key.parent().parent().get().track_options().keys():
            if not(self.track_assignment_limit.has_key(t)):
                self.track_assignment_limit[t] = 10

        self.put()
        return self.track_assignment_limit

    def set_track_limit(self, trackname, assignment_limit):
        self.track_assignment_limit[trackname] = assignment_limit
        self.put()

    def private_comments(self):
        return self.private_comments_flag

    def set_private_comments(self, onOff):
        self.private_comments_flag = onOff
        self.put()

class RankReview(ReviewConfigBase):
    def name(self):
        return "Ranking"

    def reviewpage(self):
        return "rankingreview"

    def decisionpage(self):
        return "rankingdecision"


Available_Review_Models = [
    RankReview,
    NewScoringReview,
    ClassicReview
    ]


def review_name(m):
    return m().name()


def available_review_models():
    return map(review_name, Available_Review_Models)


class ConferenceReviewFactory(ndb.Model):
    round1_review_key = ndb.KeyProperty()
    round2_review_key = ndb.KeyProperty()

    def make_review_round(self, ReviewType, review_round):
        review = ReviewType(parent=self.key)
        review.set_review_round(review_round)
        review.put()
        return review

    def set_default_reviews(self):
        self.round1_review_key = self.make_review_round(NewScoringReview, 1).key
        self.round2_review_key = self.make_review_round(RankReview, 2).key
        self.put()

    def get_round_config(self, round):
        if (1 == round):
            return self.round1_review_key.get()

        if (2 == round):
            return self.round2_review_key.get()

        return None

    def delete_crrt_round(self, key):
        if key is not None:
            key.delete()


    def set_round(self, round, new_review_config_type):
        if (1 == round):
            self.delete_crrt_round(self.round1_review_key)
            self.round1_review_key = self.make_review_round(new_review_config_type, round).key

        if (2 == round):
            self.delete_crrt_round(self.round2_review_key)
            self.round2_review_key = self.make_review_round(new_review_config_type, round).key

        self.put()


    def set_round_by_name(self, round, review_text_name):
        for i in Available_Review_Models:
            if (review_name(i) == review_text_name):
                self.set_round(round, i)
                break

def get_conference_review_factory(conference_key):
    fetched_factory = ConferenceReviewFactory.query(ancestor = conference_key).fetch()
    if (0 == len(fetched_factory)):
        new_factory = ConferenceReviewFactory(parent=conference_key)
        new_factory.put() # must put to make sure key is valid
        new_factory.set_default_reviews()
        return new_factory
    else:
        return fetched_factory[0]
