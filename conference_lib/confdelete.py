#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system includes

# framework includes
from google.appengine.ext import ndb

# app imports
from conference_lib import conference, confoptions
from submission_lib import submission_ans, submissionrecord, votecomment, voterecord
from subreview_lib import confreviewconfig, reviewer, dedupvotes
from scaffold import userrights

def delete_class_entries(cls, conference_key):
    children = cls.query(ancestor=conference_key).fetch(keys_only=True)
    map(lambda child: child.delete(), children)
    conference_key.delete()


def cascade_delete_conference(conference_key):
    delete_class_entries(userrights.RightsRecord, conference_key)

    delete_class_entries(confoptions.OptionCounter, conference_key)
    delete_class_entries(confoptions.TrackOption, conference_key)
    delete_class_entries(confoptions.TalkFormatOption, conference_key)
    delete_class_entries(confoptions.DurationOption, conference_key)
    delete_class_entries(confoptions.ExpenseOptions, conference_key)
    delete_class_entries(confoptions.AcknowledgementEmailCCAddresses, conference_key)
    delete_class_entries(confoptions.AcknowledgementEmailBCCAddresses, conference_key)
    delete_class_entries(confoptions.AcceptEmailCCAddress, conference_key)

    delete_class_entries(submission_ans.AnswerClass, conference_key)
    delete_class_entries(submissionrecord.SubmissionRecord, conference_key)
    delete_class_entries(votecomment.VoteComment, conference_key)
    delete_class_entries(voterecord.VoteRecord, conference_key)

    delete_class_entries(confreviewconfig.ConferenceReviewFactory, conference_key)
    delete_class_entries(confreviewconfig.ClassicReview, conference_key)
    delete_class_entries(confreviewconfig.NewScoringReview, conference_key)
    delete_class_entries(confreviewconfig.RankReview, conference_key)

    delete_class_entries(dedupvotes.DuplicateVoteReport, conference_key)
    delete_class_entries(reviewer.ReviewAssignment, conference_key)
    delete_class_entries(voterecord.VoteRecord, conference_key)
    delete_class_entries(reviewer.Reviewer, conference_key)

    conference_key.delete()

