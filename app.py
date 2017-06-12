from flask import Flask, render_template, request, jsonify, Response, send_file
from argparse import ArgumentParser
from collections import namedtuple
from contextlib import closing
import os
import sys

if sys.version_info >= (3, 0):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
    from urllib.parse import parse_qs
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn
    from urlparse import parse_qs

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError

ResponseStatus = namedtuple("HTTPStatus",
                            ["code", "message"])

ResponseData = namedtuple("ResponseData",
                          ["status", "content_type", "data_stream"])

# Mapping the output format used in the client to the content type for the
# response
AUDIO_FORMATS = {"ogg_vorbis": "audio/ogg",
                 "mp3": "audio/mpeg",
                 "pcm": "audio/wave; codecs=1"}
CHUNK_SIZE = 1024
HTTP_STATUS = {"OK": ResponseStatus(code=200, message="OK"),
               "BAD_REQUEST": ResponseStatus(code=400, message="Bad request"),
               "NOT_FOUND": ResponseStatus(code=404, message="Not found"),
               "INTERNAL_SERVER_ERROR": ResponseStatus(code=500, message="Internal server error")}

# Create a client using the credentials and region defined in the adminuser
# section of the AWS credentials and configuration files
session = Session(profile_name="adminuser")
polly = session.client("polly")

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/voices', methods=['POST'])
def voices():
    """Handles routing for listing available voices"""
    params = {}
    voices = []

    while True:
        try:
            # Request list of available voices, if a continuation token
            # was returned by the previous call then use it to continue
            # listing
            response = polly.describe_voices(**params)
        except (BotoCoreError, ClientError) as err:
            # The service returned an error
            raise InvalidUsage(str(err), status_code=500)
        
        # Collect all the voices
        voices.extend(response.get("Voices", []))
        
        # If a continuation token was returned continue, stop iterating
        # otherwise
        if "NextToken" in response:
            params = {"NextToken": response["NextToken"]}
        else:
            break
        
    return jsonify(voices)
    
@app.route('/read', methods=['GET'])
def read():
    """Handles routing for reading text (speech synthesis)"""
    # Get the parameters from the query string
    try:
        text = request.args.get('text')
        voiceId = request.args.get('voiceId')
        outputFormat = request.args.get('outputFormat')
    except TypeError:
        raise InvalidUsage("Wrong parameters", status_code=400)

    # Validate the parameters, set error flag in case of unexpected
    # values
    try:
        if len(text) == 0 or len(voiceId) == 0 or \
                outputFormat not in AUDIO_FORMATS:
            raise InvalidUsage("Wrong parameters", status_code=400)
        else:
            try:
                # Request speech synthesis
                response = polly.synthesize_speech(Text=text,
                                                    VoiceId=voiceId,
                                                    OutputFormat=outputFormat)
            except (BotoCoreError, ClientError) as err:
                # The service returned an error
                raise InvalidUsage(str(err), status_code=500)
            
            return send_file(response.get("AudioStream"),AUDIO_FORMATS[outputFormat])
    except:
        raise InvalidUsage("Wrong parameters", status_code=400)
    
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
