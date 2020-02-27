#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------
# schedule_lib/schedexport.py
#

# system imports
import datetime

# framework imports
from google.appengine.ext import ndb
import cloudstorage
import xlsxwriter

# app imports
import schedule
from reports import exportexcel

def worksheet_write_wrapper(wksheet, row, col, text):
    wksheet.write(row, col, text)

def write_title_row(sched, day, worksheet):
    row = 0
    col = 1
    for t in sched.tracks(day):
        worksheet_write_wrapper(row, col, t)
        col += 1

def write_tracks(row, col, day, slot, sched, worksheet):
    for t in sched.tracks(day):
        worksheet_write_wrapper(row, col, sched.get_assignment(day, t, slot))
        col += 1

def write_plenary(row, col, description, worksheet):
    worksheet_write_wrapper(row, col, description)

def write_slots_and_content(sched, day, worksheet):
    row = 1
    for slot in sched.orderd_slot_keys(day):
        col = 0
        worksheet_write_wrapper(row, col, "'"+sched.slots(day)[slot].start_time.strftime("%H:%M"))
        col += 1
        worksheet_write_wrapper(row, col, "'"+sched.slots(day)[slot].end_time.strftime("%H:%M"))
        col += 1

        if sched.slots(day)[slot].slot_type == "Tracks":
            write_tracks(row, col, day, slot, sched, worksheet)
        else:
            write_plenary(sched.get_assignment(row, col, day, "Plenary", slot), worksheet)

        row += 1

def write_days(sched, workbook):
    for day in sched.day_names():
        worksheet = workbook.add_worksheet(name=day)
        write_title_row(sched, day, worksheet)
        write_slots_and_content(sched, day, worksheet)

def schedule_to_excel(sched):
    fullname, url = exportexcel.mk_filename("Schedule", datetime.datetime.now())
    with cloudstorage.open(fullname, "w",
                           content_type="text/plain; charset=utf-8",
                           options={'x-goog-acl': 'public-read'}) as output:
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        write_days(sched, workbook)
        workbook.close()

    output.close()
    return url
