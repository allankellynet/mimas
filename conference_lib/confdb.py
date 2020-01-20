#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports
from conference import Conference
from scaffold import userrights


# Stand alone functions for getting conferences from the database
# May be used with other classes, e.g. UserRights

def retrieve_all_conferences():
    return Conference.query().fetch()


def retrieve_all_conferences_by_state(state):
    return Conference.query().filter(Conference.conf_state == state).fetch()

def retrieve_special_rights_conferences(user_email):
    rights = userrights.RightsRecord.query().filter(userrights.RightsRecord.username == user_email).fetch()
    results = []
    for r in rights:
        results.append(r.key.parent().get())

    return results


def get_conf_by_name(n):
    confs = Conference.query().filter(Conference.conf_name == n).fetch(1)
    if confs == []:
        return None
    else:
        return confs[0]

def get_conf_by_shortname(shortname):
    confs = Conference.query().filter(Conference.conf_shortname == shortname).fetch(1)
    if confs == []:
        return None
    else:
        return confs[0]


def get_any_conf():
    # used when no conference_lib selected
    # presumably gets "first" conference_lib
    # normally only 1 conference_lib live in the system at any time
    confs = Conference.query().fetch(1)
    if confs == []:
        return None
    else:
        return confs[0]

def count_conferences():
    return Conference.query().count()

def delete_conference(conf_key):
    # query will get conference too
    children = ndb.Query(ancestor=conf_key).fetch(keys_only=True)
    for child in children:
        child.delete()
