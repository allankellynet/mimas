#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
import logging

from google.appengine.ext import ndb


# app imports

# Having to this working for round 1 quite nicely...
# Getting it working in round 2 looks like a mistake
#
# The intention was to later refactor all vote comments over to this approach
# (and remove commetn from VoteRecord)
# But right now that looks like a mistake
# And the refactoring should go the other way
# such that private comments are folded into vote record
#
# That would partly remove the need for VoteSummary
# But VotyeSummary shold also help clean up round2reviewpage


class VoteComment(ndb.Model):
    # database parent is a existing vote
    message = ndb.StringProperty()
    visibility = ndb.StringProperty()

    def is_private(self):
        return self.visibility=="Private"

    def comment_text(self):
        return self.message


def mk_new_comment(vote_key, visibility, message):
    comment=VoteComment(parent=vote_key)
    comment.visibility = visibility
    comment.message = message
    comment.put()
    return comment

def retrieve_vote_comment(vote_key):
    logging.info((">>>>>> retrieve_vote_comment"))
    r = VoteComment.query(ancestor=vote_key).fetch(1)
    if len(r) == 0:
        return None

    return r[0]

def retrieve_comment_text(vote_key):
    comment = retrieve_vote_comment(vote_key)
    if comment == None:
        return ""

    return comment.message

def update_comment(vote_key, visibility, new_message):
    existing_comment = retrieve_vote_comment(vote_key)
    if  existing_comment == None:
        existing_comment = mk_new_comment(vote_key, visibility, new_message)
    else:
        existing_comment.visibility = visibility
        existing_comment.message = new_message
        existing_comment.put()

    return existing_comment