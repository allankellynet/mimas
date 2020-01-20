#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# Functions to support multiple uses of the talk_fragment.html

# system imports

# library imports

# local imports
import talk

def readAndSave(handler, t):
    t.title = handler.request.get("title")
    t.set_field(talk.SHORT_SYNOPSIS, handler.request.get("shortsynopsis"))
    t.set_field(talk.LONG_SYNOPSIS, handler.request.get("longsynopsis"))
    if handler.request.get("dirlisting") == "listed":
        t.show_listing()
    else:
        t.hide_listing()

    return t.put()
