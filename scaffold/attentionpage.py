#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# System imports

# Google imports

# Local imports
import basehandler


class SingleMessagePage(basehandler.BaseHandler):
    def process_get(self, message_map, page):
        if self.request.params.has_key("reason"):
            reason_code = self.request.get("reason")
        else:
            reason_code = "Unknown"

        if self.request.params.has_key("p1"):
            message = message_map[reason_code] % self.request.get("p1")
        else:
            message = message_map[reason_code]

        template_values = {
            "msg": message
        }

        self.write_page(page, template_values)

class AttentionPage(SingleMessagePage):
    attention_messages = {
        "Unknown": "Sorry, I wanted your attention but I can't rember why!",
        "UnknownCoSpeaker": "Your co-speaker '%s' is unknown to this system. Please have them register their speaker details. Failure to do so may lead to your submission being disallowed.",
        "GeneratingVoteReport": "The duplicate vote report takes a few minutes to generate, please check the duplicate vote page shortly.",
        "DeDuplicateRunning": "Duplicate votes being removed. This might take a few minutes so please check back soon.",
        "DoesNotPayExpenses": "Conference does not pay expenses",
        "ThankYouCoSpeaker": "Thank you for entering your co-speaker details",
        "SpeakerAddressMissing": "Speaker email address not given",
        "UnknownSpeaker": "Unknown speaker",
        "MasterDone": "Master command done",
        "NoCrrtConference": "No current conference selected. Please select a conference and try again",
    }

    def get(self):
        self.process_get(self.attention_messages, 'scaffold/attentionpage.html')

def redirect_attention(request_handler, reason):
    request_handler.redirect("/attention?reason="+reason)

class ThankYouPage(SingleMessagePage):
    thanks_message = {
        "Unknown": "Not quite sure why you are on this page, thanks all the same!",
        "ProtoSpeakerRequest": "Thank you for your request to make a submission, please check your email for a link to continue",
        "CoSpeakersNoted": "The names of your co-cpeakers have been noted, thanks",
    }

    def get(self):
        self.process_get(self.thanks_message, 'scaffold/thankspage.html')

def redirect_thankyou(request_handler, reason):
    request_handler.redirect("/thanks?reason="+reason)

class ExtendedMessage(SingleMessagePage):
    message = {
        "Unknown": "Message lost, sorry, thanks all the same!",
        "RequestMoreReviewers": "Thank your for requesting more reviews. " \
                                "It takes a few moments for review assignment. " \
                                "If you do not see any more submissons for review it may be because " \
                                "you have reviewed everything in this track.",
        "BulkReviewAssignments": "Review assignments can take a couple of minutes. " \
                                "Go make yourself a cup of tea (or coffee) and check back later. ",
        }

    def get(self):
        if self.request.params.has_key("reason"):
            reason_code = self.request.get("reason")
        else:
            reason_code = "Unknown"

        template_values = {
            "msg": self.message[reason_code],
            "url": self.request.get("url", "/")
        }

        self.write_page("scaffold/extmsgpage.html", template_values)

def redirect_extendedmessage(request_handler, reason, url):
    request_handler.redirect("/extmessage?reason="+reason+"&url="+url)
