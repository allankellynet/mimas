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
from speaker_lib import cospeaker
from mailmsg import custommsg, msgtemplate, postmail
from reports.exportcsv import export_submissions
from reports.exportexcel import export_submissions_to_excel
from submission_lib import submissionrecord, submission_ans, submissions_aux
from scaffold import tags
import basehandler
from conference_lib import confquestion

class SpeakerCommsPage(basehandler.BaseHandler):
    def get(self):
        conference_key = self.retrieve_conf_key()

        if self.request.params.has_key("f"):
            submissions, filter_description = self.retrieve_submissions(conference_key, self.request.get("f"))
        else:
            submissions = []
            filter_description = "No filter set"

        if self.request.params.has_key("allfields"):
            all_fields = "ALL"
        else:
            all_fields = ""

        template_values = {
            "crrt_conference": conference_key.get(),
            "submissions": submissions,
            "name": self.get_crrt_user().email(),
            "conf_safe_key": conference_key.urlsafe(),
            "all_fields": all_fields,
            "get_cospeakers_func": cospeaker.get_pretty_list,
            "custom_message": custommsg.retrieve_custom_message(conference_key),
            "taglist": tags.taglist_func,
            "conf_questions": confquestion.retrieve_questions(conference_key),
            "retrieve_answer": submission_ans.retrieve_answer,
            "filter_description": filter_description,
        }

        self.write_page('reports/speakercommspage.html', template_values)

    def retrieve_conf_key(self):
        conference_key = None
        if self.session.has_key("crrt_conference"):
            conference_key = ndb.Key(urlsafe=self.session["crrt_conference"])
        elif self.request.params.has_key("conf"):
            conference_key = ndb.Key(urlsafe=self.request.get("conf"))
            self.session["crrt_conference"] = conference_key.urlsafe()
        return conference_key

    def retrieve_submissions(self, conference_key, filter):
        if (filter == "Declines"):
            return submissions_aux.retrieve_by_final_decision_track_ordered(conference_key, "Decline"), \
                "Declines only"
        if (filter == "AcceptAll"):
            return submissions_aux.retrieve_by_final_decision_track_ordered(conference_key, "Accept"), \
                "Accepts only"
        if (filter=="All"):
            return submissionrecord.retrieve_conference_submissions_orderby_track(conference_key), \
                "All submissions"

    def get_all_checked(self):
        checked = self.request.get_all("chosen")
        submission_keys = []
        for c in checked:
            submission_keys.append(ndb.Key(urlsafe=c))

        return submission_keys

    def get_filtered_by_final_decision(self, keys, decision):
        r = []
        for k in keys:
            if (k.get().final_decision() == decision):
                r.append(k.get())
        return r

    def send_msg(self, msg_type, subs):
        conf_key = self.retrieve_conf_key()
        postmail.Postman().post_many(
                    conf_key.get(),
                    msgtemplate.retrieveTemplate(msg_type, conf_key),
                    subs)
        self.redirect("/speakercomms")

    def send_declines(self):
        self.send_msg(msgtemplate.DeclineMsg,
                      self.get_filtered_by_final_decision(self.get_all_checked(), "Decline"))

    def send_accepts(self):
        logging.info("Sending accepts...")
        self.send_msg(msgtemplate.AcceptMsg,
                      self.get_filtered_by_final_decision(self.get_all_checked(), "Accept"))

    def export_data(self):
        url = export_submissions(self.get_all_checked())
        message = "Data export complete: " + url
        template_values = {
            "msg": message
        }

        # Unconventional use of attentionpage but it works
        # Now attention is in scaffold it looks odd
        # Should add helper function in attentionpage to deal with this scenario
        self.write_page('scaffold/attentionpage.html', template_values)

    def export_excel_data(self):
        pass
        url = export_submissions_to_excel(self.get_all_checked())
        message = "Data export to Excel complete: " + url
        template_values = {
            "msg": message
        }

        self.write_page('scaffold/attentionpage.html', template_values)

    def send_custom_msgs(self):
        msg_selected = self.request.get("custommsglist")
        if msg_selected!="None":
            postmail.Postman().post_many_by_key(
                        self.retrieve_conf_key().get(),
                        ndb.Key(urlsafe=msg_selected).get(),
                        self.get_all_checked())

        self.redirect("/speakercomms")

    def post(self):
        if self.request.get("SendDeclines"):
            self.send_declines()
        if self.request.get("SendAccept"):
            self.send_accepts()
        if self.request.get("Export"):
            self.export_data()
        if self.request.get("ExcelExport"):
            self.export_excel_data()
        if self.request.get("SendCustomMgs"):
            self.send_custom_msgs()
