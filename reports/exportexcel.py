#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
from datetime import datetime

# framework imports
import cloudstorage
import xlsxwriter

# app imports
from scaffold import sysinfo
from speaker_lib import cospeaker
from talk_lib import talk

Col_Email = 0
Col_First_name = Col_Email+1
Col_Last_name = Col_First_name+1
Col_Telephone = Col_Last_name+1
Col_Address = Col_Telephone+1
Col_Sub_Title = Col_Address+1
Col_Decision = Col_Sub_Title+1

def write_title_row(worksheet):
    worksheet.write(0, Col_Email, "Email")
    worksheet.write(0, Col_First_name, "First name")
    worksheet.write(0, Col_Last_name, "Last name")
    worksheet.write(0, Col_Telephone, "Tele")
    worksheet.write(0, Col_Address, "Address")
    worksheet.write(0, Col_Sub_Title, "Submission Title")
    worksheet.write(0, Col_Decision, "Final decision")

def write_submission(worksheet, row, submission, speaker, talk):
    worksheet.write(row, Col_Email, speaker.email)
    worksheet.write(row, Col_First_name, speaker.first_name())
    worksheet.write(row, Col_Last_name, speaker.later_names())
    worksheet.write(row, Col_Telephone, speaker.telephone)
    worksheet.write(row, Col_Address, speaker.address)

    worksheet.write(row, Col_Sub_Title, talk.title)
    worksheet.write(row, Col_Decision, submission.final_decision())


def write_submissions_list(worksheet, subs_keys):
    row = 1
    for key in subs_keys:
        submission = key.get()
        write_submission(worksheet, row, submission, submission.talk.parent().get(), submission.talk.get())
        row = row + 1

def export_submissions_to_excel(submission_keys):
    now = datetime.now()
    bucketname = "/mimas-aotb.appspot.com"
    filename = bucketname + "/Export" + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + ".xlsx"
    fullname = bucketname + filename
    with cloudstorage.open(fullname, "w",
                           content_type="text/plain; charset=utf-8",
                           options={'x-goog-acl': 'public-read'}) as output:
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        write_title_row(worksheet)
        write_submissions_list(worksheet, submission_keys)
        workbook.close()

    output.close()

    return "http://" + bucketname + ".storage.googleapis.com" + filename

