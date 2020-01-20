#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler


class SorryPage(basehandler.BaseHandler):
    sorry_messages = {
        "Unknown": "Something went wrong, this isn't good and I should be able to say more but can't",
        "NoneOpen": "There are no conferences currently open for submission. Please try again at a later date.",
        "CannotClose" : "Some submissions are still awaiting a decision. Conference cannot be closed until all submissions are decided on.",
        "CannotCloseR1" : "Some submissions are still awaiting a decision. Round cannot be closed until all submissions are decided.",
        "InternalErrorTalk" : "Internal error: Talk cannot be determined",
        "ConfNameInUse": "That conference name is already in use, please try another",
        "ConfShortnameInUse": "That shortname is already in use, please try another",
        "NoDeleteSelf": "You are not allowed to delete your own permissions.",
        "AlreadySubmitted": "This talk has already been submitted to this conference. Duplicate submissions are not allowed.",
        "NoAccess": "You do not have access rights to this page",
        "NoDeleteRights": "Cannot delete conference: only conference creator or system admin may delete an existing conference",
        "BlankDateField": "Date field cannot be blank",
        "BlankNameField": "Name field cannot be blank",
        "BlankShortnameField": "Shortname cannot be blank",
        "ConfKeyMissing": "Failed to identify conference, please start over",
        "OptionsClosedOnly": "Conference options can only be changed for closed conferences",
        "QuestionsClosedOnly": "Conference questions can only be changed for closed conferences",
        "NoTracksAssigned": "You have not yet been assigned to any tracks to review",
        "NoConfToReview": "There are currently no conferences open for review",
        "ConfNotOpen": "This conference is not currently open for submission",
        "NeedReCaptcha": "Please complete the reCaptcha before submitting",
        "NoSpeakerCommsRights": "Speaker comms permissions required to change these messages",
        "ContactEmailMandatory": "Conference contact email address is mandatory",
        "UnrecognisedCospeakerID": "Failed to recognise co-speaker ID",
        "SpeakerPageAccessDenied": "Speaker access denied",
        "SpeakerPageKeyNotSupplied": "Speaker details invalid",
        "SpeakerPageCredentialsDoNotMatch": "Speaker details do not match",
        "SubsLimitReached": "Conference submission limit reached",
        "MissingUserSessionKey": "User authentication failure",
        "RequiresEmail": "This page is only available to those with confirmed e-mail addresses",
        "DeleteSpeaker": "Delete speaker not currently implemented",
        "NoImage": "No image supplied",
        "ImageTooBig": "Image too big: maximum file size is 1Mb. Please use a smaller image.",
        "AdminRightsReq": "Admin rights required to access this page",
        "AssignTracksReq": "Assign reviews to track persmission required to access this page",
        "MissingParams": "Parameters missing: please contact your system administrator, this shouldn't be happening",
        "IncompleteSetup": "Until conference setup is complete this report cannot be shown",
        "VolunteerFailure": "Something went wrong in the volunteer login",
        "VolunteerReviewerClosed": "The conference is currently not accepting reviewers",
    }

    def get(self):
        if self.request.params.has_key("reason"):
            reason_code = self.request.get("reason")
        else:
            reason_code = "Unknown"

        template_values = {
            "msg": self.sorry_messages[reason_code],
            "loggedin": self.is_logged_in(),
        }

        self.write_page('scaffold/sorrypage.html', template_values)

def redirect_sorry(request_handler, reason):
    request_handler.redirect("/sorry_page?reason="+reason)
