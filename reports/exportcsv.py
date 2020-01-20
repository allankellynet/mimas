#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
from datetime import datetime

# framework imports
import cloudstorage

# app imports
from scaffold import sysinfo
from speaker_lib import cospeaker
from talk_lib import talk


# Notes:
# 1. attempts to handle commas in fields nicely, i.e. puts text in quotes
# 2. New lines are honoured as they are entered
#
# But:
# 1. Excel starts new row when it encounters a line break
# 2. Google Docs Spreadsheet does the same
# 3. Apple Numbers handles it all fine and has line breaks in cells
#
# Right now preserving the authors intention seems the right thing to do
# But we may need to work on this...

def single_quotes_inside(txt):
    return txt.replace('"', "'")

def add_quotes(txt):
    return '"' + txt + '"'

def write_with_comma(out, txt):
    if txt == None:
        txt = ""

    txt = single_quotes_inside(txt)
    if txt.find(",") > -1:
        txt = add_quotes(txt)
    txt += ", "
    out.write(txt.encode('utf-8'))

def write_sub(out, sub):
    write_with_comma(out, sub.final_decision())
    write_with_comma(out, sub.submitter())
    speaker = sub.talk.parent().get()
    write_with_comma(out, speaker.email)
    write_with_comma(out, speaker.telephone)
    write_with_comma(out, speaker.address)

    cospeaks = cospeaker.get_cospeakers(sub.key)
    for co in range(0, 2):
        if co < len(cospeaks):
            write_with_comma(out, cospeaks[co].name)
        else:
            write_with_comma(out, "")

    write_with_comma(out, speaker.field(speaker.FIELD_AFFILICATION))
    write_with_comma(out, speaker.field(speaker.FIELD_TWITTER))
    write_with_comma(out, speaker.bio)
    write_with_comma(out, speaker.field(speaker.FIELD_EXPERIENCE))
    # Field for URL to speaker photo
    if speaker.fullsize_picture == None:
        write_with_comma(out, "None")
    else:
        write_with_comma(out, sysinfo.home_url() + "/speakerfullimg?img_id=" + speaker.key.urlsafe())

    tlk = sub.talk.get()
    write_with_comma(out, tlk.title)
    write_with_comma(out, tlk.field(talk.SHORT_SYNOPSIS))
    write_with_comma(out, tlk.field(talk.LONG_SYNOPSIS))

    conf = sub.key.parent().get()
    write_with_comma(out, conf.track_options()[sub.track_name])
    write_with_comma(out, conf.delivery_format_options()[sub.delivery_format_text])
    write_with_comma(out, conf.duration_options()[sub.duration])
    write_with_comma(out, conf.expenses_options()[sub.expense_expectations])

def write_sub_list(out, submission_keys):
    for s in submission_keys:
        write_sub(out, s.get())
        out.write("\n")

def write_title_row(out):
    write_with_comma(out, "Latest decision")
    write_with_comma(out, "Speaker name")
    write_with_comma(out, "Speaker email")
    write_with_comma(out, "Speaker telephone")
    write_with_comma(out, "Speaker address")
    write_with_comma(out, "Co-speaker 1")
    write_with_comma(out, "Co-speaker 2")
    write_with_comma(out, "Affiliation")
    write_with_comma(out, "Twitter handle")
    write_with_comma(out, "Bio")
    write_with_comma(out, "Speaking experience")

    write_with_comma(out, "Title of Session")
    write_with_comma(out, "Short synopsis")
    write_with_comma(out, "Long synopsis")

    write_with_comma(out, "Track")
    write_with_comma(out, "Session type")
    write_with_comma(out, "Session duration")
    write_with_comma(out, "Expenses expectations")
    out.write("\n")

def export_submissions(submission_keys):
    now = datetime.now()
    bucketname = "/mimas-aotb.appspot.com"
    filename = bucketname + "/Export" + str(now.month) + str(now.day) + str(now.hour) + ".csv"
    fullname = bucketname + filename
    with cloudstorage.open(fullname, "w",
                           content_type="text/plain; charset=utf-8",
                           options={'x-goog-acl': 'public-read'}) as output:
        write_title_row(output)
        write_sub_list(output, submission_keys)
    output.close()

    return "http://" + bucketname + ".storage.googleapis.com" + filename
