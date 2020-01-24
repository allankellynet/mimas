#!/usr/bin/env python
#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
import datetime, sys

sys.path.append("lib/python-http-client")
sys.path.append("lib/sendgrid-python")

# App Engine imports
import logging
from google.appengine.api import users
from google.appengine.ext import ndb

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

import webapp2

# Local imports
from talk_lib import talkpage, pubtalkpage
from conference_lib import confadmin, confstatepage, confoptionspage, conflimitspage, confemailrecipients, chooseconf, \
    permissionspage, assigntrackspage, assignvolreviewerspage
from conference_lib import confquestionspage, deletepage
from subreview_lib import rankingdecisionpage, classicreviewlistpage, reviewdetailspage, reviewmain, \
    classicreviewdecisionpage, reviewconfigpage, newscoreconfigpage, votingrecordspage, subsassignmentpage, \
    rankingreviewpage, classicsubscoring, commentreviewpage, deduppage, newscoringlistpage, newscoringpage, \
    assignmentdetailpage, subsreviewerspage
import subreview_lib.newscoringtask
from scaffold import sorrypage, attentionpage, welcomepage, volunteerpage, volunteerreviewerpage, firebase, logoutpage, \
    mimasuser
import basehandler
from speaker_lib import speakerpage, speakermain, cospeakerlistpg, \
    cospeakerpage, dirpage, publicspage
import scaffold.image_handlers
from reports import expensereportpage, showallpage, statuslist, speakrptpage, expenseslistpage, speakercommspage, \
    customexportpage
from submission_lib import subm_thanks, submitpage, singlesubmitpage, flowsubpage, acceptdecline
from mailmsg import createmsgpage, custommsgedit, mailtemplatespage
from scaffold import edittags, masterpage
from extra import extracontrolspage, speakertalkpage, testdatapage

requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class MainHandler(basehandler.BaseHandler):
    def mainpage(self):
        # need to pick user up frm session
        # retrieve
        # do whatever
        if not self.session.has_key("uk"):
            sorrypage.redirect_sorry("MissingUserSessionKey")
            return

        user = ndb.Key(urlsafe=self.session["uk"]).get()

        crrt_conference_key = self.get_crrt_conference_key()

        template_values = {
            'name': user.name(),
            'email': user.email(),
            'logoutlink': users.create_logout_url(self.request.uri),
            'crrt_conference_key': crrt_conference_key,
        }

        self.write_page('scaffold/index.html', template_values)

    def about_page(self):
        template_values = {'google_login': users.create_login_url(self.request.uri + "first"),
                           "firebase_config_variable" : firebase.config_js_params()
                           }
        self.write_page("scaffold/about.html", template_values)

    def get(self):
        if not self.session.has_key("uk"):
            # no user key so show the about page and ask for login
            self.about_page()
        else:
            # user key exists so goto the main page
            self.mainpage()

    def post(self):
        conf_key = self.request.get("conference")
        self.session["crrt_conference"] = conf_key
        self.redirect("/")



# ---------------------------
# Basic Google Login
# Is largely initended for local development server running
# May also be used in live for testing
#
# Accessed via unpubliced URL
# /loginb
#
class BasicGoogleLogin(basehandler.BaseHandler):
    def get(self):
        template_values = {'google_login': users.create_login_url(self.request.uri + "_success")}
        self.write_page('scaffold/loginb.html', template_values)

def complete_login(handler, usr):
    usr.set_last_login(datetime.datetime.now())
    usr.put()
    handler.session["uk"] = usr.key.urlsafe()

    if handler.session.has_key("singlesubmit"):
        handler.redirect('/flowsubmit')
    else:
        handler.redirect('/')

class BasicGoogleLoginSuccess(basehandler.BaseHandler):
    def get(self):
        logging.info("Basic Google Login Success")
        google_user = users.get_current_user()
        if not google_user:
            self.redirect(users.create_login_url(self.request.uri + "loginb"))

        usr = mimasuser.find_user_by_id(google_user.user_id())
        if not usr:
            usr = mimasuser.mk_MimasUser(google_user.nickname(), google_user.email(), google_user.user_id())

        complete_login(self, usr)

# -------------------------
# Firebase login for live running
class FirebaseLoginSuccess(basehandler.BaseHandler):
    def get(self):
        logging.info("Firebase Login Success")
        id_token = self.request.get("user")
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.info("FirebaseLoginSuccess but Claims is None")
            self.redirect('/')

        usr = mimasuser.find_user_by_id(claims["user_id"])
        if not usr:
            logging.info("FirebaseLoginSuccess creating MimasUser")
            usr = mimasuser.mk_MimasUser(claims["name"], claims["email"], claims["user_id"])

        logging.info("FirebaseLoginSuccess storing login time")
        complete_login(self, usr)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/speaker', speakerpage.SpeakerPage),
    ('/speakerfullimg', scaffold.image_handlers.SpeakerImage),
    ('/image', scaffold.image_handlers.Image),
    ('/speakeremail', speakerpage.SpeakerPageByEmail),
    ('/speakerkey', speakerpage.SpeakerPageByKey),
    ('/speakerupdate', speakerpage.SpeakerUpdatePage),
    ('/talk_submission', talkpage.TalkPage),
    ('/pubtalk', pubtalkpage.PublicTalkPage),
    ('/list_submission', statuslist.StatusListPage),
    ('/createconf', confadmin.ConferenceAdminPage),
    ('/classicreview', classicreviewlistpage.ClassicReviewListPage),
    ('/submissionreviewpage', classicsubscoring.ClassicSubScoringPage),
    ('/classic_review_decisions', classicreviewdecisionpage.ClassicReviewDecisionPage),
    ('/scoringreview', newscoringlistpage.NewScoringReviewListPage),
    ('/newscoringpage', newscoringpage.NewScoringReviewPage),
    ('/assigntracks', assigntrackspage.ReviewAdminPage),
    ('/assignvolunteers', assignvolreviewerspage.AssignVolunteerReviewersPage),
    ('/rankingdecision', rankingdecisionpage.RankingDecisionPage),
    ('/rankingreview', rankingreviewpage.RankingReviewPage),
    ('/review_details_page', reviewdetailspage.ReviewDetailsPagePublic),
    ('/review_feedback', reviewdetailspage.ReviewDetailsPageFeedback),
    ('/submit_page', submitpage.SubmitPage),
    ('/submit_talk', submitpage.SubmitPage),
    ('/confstate_page', confstatepage.ConferencePage),
    ('/conference_state', confstatepage.ConferencePage),
    ('/sorry_page', sorrypage.SorryPage),
    ('/attention', attentionpage.AttentionPage),
    ('/extmessage', attentionpage.ExtendedMessage),
    ('/thanks', attentionpage.ThankYouPage),
    ('/showallpage', showallpage.ShowAllPage),
    ('/permissionspage', permissionspage.PermissionsPage),
    ('/speakercomms', speakercommspage.SpeakerCommsPage),
    ('/chooseconf', chooseconf.ChooseConfPage),
    ('/reviewers', reviewmain.ReviewMainPage),
    ('/confoptionspage', confoptionspage.ConferenceOptionsPage),
    ('/welcome', welcomepage.WelcomePage),
    ('/volunteer', volunteerpage.VolunteerPage),
    ('/volunteerreviewer', volunteerreviewerpage.VolunteerReviewerPage),
    ('/speakermain', speakermain.SpeakerMainPage),
    ('/confemailcopy', confemailrecipients.ConferenceEmailsPage),
    ('/confquestionspage', confquestionspage.ConferenceQuestionsPage),
    ('/singlepagesubmission', singlesubmitpage.SingleSubmitPage),
    ('/submit', singlesubmitpage.SingleSubmitPage),
    ('/confconfigpage', conflimitspage.ConferenceConfigPage),
    ('/deduppage', deduppage.DedupPage),
    ('/expensesreportpage', expensereportpage.ExpenseReportPage),
    ('/speakerrptpage', speakrptpage.SpeakerReportPage),
    ('/customexport', customexportpage.CustomExportPage),
    ('/mailmessages', mailtemplatespage.MailTemplatesPage),
    ('/commentreviewpage', commentreviewpage.CommentReviewPage),
    ('/cospeakerpage', cospeakerpage.CoSpeakerPage),
    ('/cospeakerpagerl', cospeakerpage.CoSpeakerPageReturnToList),
    ('/cospeakerlist', cospeakerlistpg.CoSpeakerListPage),
    ('/subthanks', subm_thanks.SubmissionThankYouPage),
    ('/custommsgpage', createmsgpage.CreateMsgPage),
    ('/custommsgedit', custommsgedit.EditCustomMsgPage),
    ('/fireloggedin', FirebaseLoginSuccess),
    ('/loginb', BasicGoogleLogin),
    ('/loginb_success', BasicGoogleLoginSuccess),
    ('/logoutpageb', logoutpage.LogoutBasicGooglePage),
    ('/logoutpagef', logoutpage.LogoutFirebasePage),
    ('/speakerdir', dirpage.SpeakerDirectoryPage),
    ('/publicspage', publicspage.PublicSpeakerPage),
    ('/edittags', edittags.EditTagsPage),
    ('/addtag', edittags.AddTagPost),
    ('/flowsubmit', flowsubpage.FlowSubmitPage1),
    ('/flowsubmit2', flowsubpage.FlowSubmitPage2),
    ('/flowsubmit3', flowsubpage.FlowSubmitPage3),
    ('/flowsubmit4', flowsubpage.FlowSubmitPage4),
    ('/acceptance', acceptdecline.AcceptDeclinePage),
    ('/expenseslist', expenseslistpage.ExpenseListPage),
    ('/reviewconfig', reviewconfigpage.ReviewMainPage),
    ('/newscoreconfigpage', newscoreconfigpage.NewScoreConfigPage),
    ('/more_reviews', subreview_lib.newscoringtask.MoreReviewsTask),
    ('/votingrecordspage', votingrecordspage.VotingRecordsPage),
    ('/subsassignmentspage', subsassignmentpage.SubmissionAssignmentsPage),
    ('/assignementdetailspage', assignmentdetailpage.AssignmentDetailPage),
    ('/subreviewers', subsreviewerspage.SubmissionReviewersPage),
    ('/mastercontrol', masterpage.MasterControlPage),                       # no public link
    ('/testdata', testdatapage.TestDataPage),                               # no public link
    ('/delete_con_page', deletepage.DeletePage),                            # no public link
    ('/extracontrols', extracontrolspage.ExtraControlsPage),                # no public link
    ('/extraspeakertalks', speakertalkpage.SpeakerTalksPage),              # no public link
], config=config, debug=True)
