from __future__ import print_function
import random
import string
import time
import boto3
import json
import urllib2
import re

info = "Random Trump Tweets for Alexa. "

intro = "Welcome Trump Tweets for Alexa. Would you like to learn how to use this skill?"

how_to = "Simply say. Alexa, ask trump tweets for a tweet"

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, card_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Standard',
            'title': "Trump Tweets - " + title,
            'text': card_text
            # 'image': {
            #     'smallImageUrl': 'https://s3.eu-west-2.amazonaws.com/shuffskills/MC_720.png',
            #     'largeImageUrl': 'https://s3.eu-west-2.amazonaws.com/shuffskills/MC_1200.png'
            # }
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_no_card(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {
        'START': True
    }
    speech_output = intro
    
    return build_response(session_attributes, build_speechlet_response("Welcome", intro , "Would you like to learn how to use trump tweets?", "", False))

def sign_request():
    from hashlib import sha1
    import hmac

    nonce = ""
    for i in range(11):
        nonce = nonce + random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)

    timestamp = int(time.time())

    # key = CONSUMER_SECRET& #If you dont have a token yet
    key = urllib2.quote("MAHGFksAMniWbyD2lO0a0EILpT1A4M80zQ5Y1Hrr9k2A3TijFn", safe='') + "&" + urllib2.quote("oYvGSW2EiqxptW8E5psGkNAE8MMX1ZpyxaZlTTRPsxNYz", safe='')

    keys = ['oauth_consumer_key',
            'oauth_nonce',
            'oauth_signature_method',
            'oauth_timestamp',
            'oauth_token',
            'oauth_version',
            # 'count',
            'screen_name',
            'tweet_mode',
            'include_rts',
            'exclude_replies']

    values = ['J4jPr12aTGg9kyFTm816ozhaZ',
              nonce,
              'HMAC-SHA1',
              str(timestamp),
              '394949955-30slTLhJwI7Rd7YQt27fvHzdV5YyGpcA1FqeesMb',
              '1.0',
              # '40',
              'realDonaldTrump',
              'extended',
              '1',
              'true']

    param_string = ""

    for i in range(8):
        res = urllib2.quote(keys[i], safe='') + '=' + urllib2.quote(values[i], safe='')
        param_string += res + '&'

    param_string = param_string[:-1]

    print(param_string)

    base_string = "GET&" + urllib2.quote('https://api.twitter.com/1.1/statuses/user_timeline.json', safe='') + "&" + urllib2.quote(param_string, safe='')

    print(base_string)

    hashed = hmac.new(key, base_string, sha1)

    print(hashed)

    # The signature
    return nonce, timestamp, hashed.digest().encode("base64").rstrip('\n')

def get_tweet(intent, session):

    nonce, timestamp, signature = sign_request()

    header = 'OAuth oauth_consumer_key="J4jPr12aTGg9kyFTm816ozhaZ",oauth_token="394949955-30slTLhJwI7Rd7YQt27fvHzdV5YyGpcA1FqeesMb",oauth_signature_method="HMAC-SHA1",oauth_timestamp="STAMP",oauth_nonce="NONCE",oauth_version="1.0",oauth_signature="SIG"'
    header = header.replace('NONCE', str(nonce))
    header = header.replace('STAMP', str(timestamp))
    header = header.replace('SIG', urllib2.quote(str(signature), safe=''))
    print(header)

    req = urllib2.Request("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=realDonaldTrump&tweet_mode=extended")
    req.add_header('Authorization', header)

    response = ""
    try:
        response = str(urllib2.urlopen(req).read())
    except Exception as e:
        print(e)
        return build_response({}, build_speechlet_response_no_card("I am having trouble connecting to the twitter API. Please try again later", "", True))

    d = json.loads(response)

    ideas = []

    ##Get all required values from response
    for obj in d:
        ideas.append(obj["full_text"])

    # print(ideas)

    chosen = random.choice(ideas)

    print(chosen)

    URLless_string = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', chosen)
    URLless_string = URLless_string.replace('&amp;', 'and')
    print(URLless_string)

    return build_response({}, build_speechlet_response("Trump Tweet", URLless_string, "", URLless_string, True))

def dont_recognise(session):
    return build_response(session, build_speechlet_response_no_card("I don't recognise your request, please try again", "I was unable to recognise your last request. Please repeat yourself", False))
    
def how_to_play(question = False):
    res = how_to
    re_prompt = None
    close = True

    if (question):
        res = how_to + ". Do you understand?"
        re_prompt = "Do you understand how to use this skill?"
        close = False

    return build_response({'UNDERSTAND': 'True'}, build_speechlet_response("How to Use, Trump Tweets", res, re_prompt,res, close))

def how_to_instr():
    return build_response({}, build_speechlet_response_no_card("Okay, enjoy using this skill!", None, True))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
    
    return get_welcome_response()


def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    try:
        if session['attributes']['START']:
            if intent_name == "AMAZON.YesIntent":
                return how_to_play(True)
            elif intent_name == "AMAZON.NoIntent":
                return how_to_instr()
    except:
        pass

    try:
        if session['attributes']['UNDERSTAND']:
            if intent_name == "AMAZON.YesIntent":
                return build_response({}, build_speechlet_response_no_card("Okay, enjoy this skill!", None, True))
            elif intent_name == "AMAZON.NoIntent":
                return how_to_play(True)
    except:
        pass

    if intent_name == "AMAZON.HelpIntent":
        return how_to_play(True)
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return build_response({}, build_speechlet_response_no_card("", None, True))
    elif intent_name == "GetTweet":
        return get_tweet(intent, session)
    else:
        return dont_recognise(session)

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Main handler ------------------

def lambda_handler(event, context):
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
