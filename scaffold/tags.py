#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports
from google.appengine.ext import ndb

# app imports

class TagEntry(ndb.Model):
    tag_text = ndb.StringProperty()
    tag_type = ndb.StringProperty()

class TagList():
    def __init__(self, parent_key):
        self.key = parent_key

    def get_all_tags(self, tag_types):
        if self.key == None:
            return []

        if tag_types == []:
            query = TagEntry.query(ancestor=self.key)
        else:
            query = TagEntry.query(ancestor=self.key).filter(TagEntry.tag_type.IN(tag_types))

        return map(lambda tag: tag.tag_text, query.fetch())

    def get_unique_tags(self):
        if self.key == None:
            return []

        return frozenset(map(lambda tag: tag.tag_text, TagEntry.query(ancestor=self.key)))

    def add_tag(self, tag, tag_type):
        new_entry = TagEntry(parent=self.key)
        new_entry.tag_text = tag
        new_entry.tag_type = tag_type
        new_entry.put()
        return new_entry.key

    def remove_tag(self, tag, tag_types):
        query = TagEntry().query(ancestor=self.key).filter(TagEntry.tag_text==tag)
        if tag_types != []:
            query = query.filter(TagEntry.tag_type.IN(tag_types))

        for t in query.fetch(keys_only=True):
            t.delete()

    def remove_all_tags(self):
        tags = TagEntry().query(ancestor=self.key).filter().fetch(keys_only=True)
        for t in tags:
            t.delete()

    def add_tag_list(self, tag_list, tag_type):
        for t in tag_list:
            self.add_tag(t, tag_type)

    def pretty_tag_list(self, tag_type):
        return ", ".join(self.get_all_tags(tag_type))

def retrieve_all_unique_tags():
    # Projection query doesn't actually work as doc says
    # i.e. we get an object back not just the field
    # But the distict does seem to work
    q = TagEntry.query(projection=[TagEntry.tag_text], distinct=True).fetch()
    return set(map(lambda r: r.tag_text, q))

def taglist_func(speaker):
    return TagList(speaker)

def split_tag_list(str):
    # this bit shold be tested
    tags = str.split(",")
    stripped_tags = []
    for tag in tags:
        stripped_tags.append(tag.lstrip())

    return stripped_tags

def tag_search(tag):
    r = TagEntry.query().filter(TagEntry.tag_text==tag).fetch(keys_only=True)
    return frozenset(map(lambda k: k.parent(), r))

def search_tags(tag_list):
    tags = split_tag_list(tag_list)
    search_results = tag_search(tags[0])
    for tag in tags:
        search_results = search_results & tag_search(tag)
        if search_results == frozenset():
            break

    return search_results
