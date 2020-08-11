import urllib2
import json
from __future__ import print_function

API_BASE="https://api.covid19india.org/state_district_wise.json"

#-----------------Build Responses--------------------------------------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
    
#--------------------Functions that controls skill's behavior------------------------------

def handle_session_end_request():
    session_attributes = {}
    card_title = "Thank you"
    speech_output = "Thank you for using coronavirus updates skill.  See you next time!"
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Coronavirus Updates"
    speech_output = "Welcome to the Coronavirus Updates skill. "
    #                 "You can ask me for the number of active cases in any district in India or " \
    #                 "ask me for number of recovered cases or number of deceased."
    reprompt_text = "Please ask me for updates regarding coronavirus in any district in India" \
                    "for example Chennai."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_district_status(intent):
    session_attributes = {}
    card_title = "COVID 19 India District Status"
    speech_output = "I'm not sure which district you wanted status for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which district you wanted status for. " \
                    "Try asking about Chennai or Coimbatore for example"
    should_end_session = False

    if "District" in intent["slots"]:
        district_name = intent["slots"]["District"]["value"]

        card_title = "Status Updates for " + district_name

        response = urllib2.urlopen(API_BASE)
        status = json.load(response)   

        speech_output = "Status Updates for " + district_name + " are as follows: "
        for stat in status["Tamil Nadu"]["districtData"][district_name]:
            element = status["Tamil Nadu"]["districtData"][district_name]
            if stat == "active":
                speech_output += "The active cases are " + element["active"]
            if stat == "confirmed":
                speech_output += "The total confirmed cases are " + element["confirmed"]
            if stat == "deceased":
                speech_output += "The total number of deaths are " + element["deceased"]
            if stat == "recovered":
                speech_output += "The recovered cases are " + element["recovered"]
                        
            reprompt_text = "I hope you got the required updates. If not please ask me again"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#------------------Events-------------------------------------------------------------
def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()
    
def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # if intent_name == "GetDistrict":
    #     return get_district_status(intent)
    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...




#-------------------Main Handler----------------------------------------------------------
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.bc6240f9-eb67-4ac1-8f1b-b22f199781a7"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])