from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from flask import Flask, jsonify, redirect, render_template, request,\
    Response, send_file
from functions import compute_dist, process_audio, resample_for_librosa,\
    save_as_wav
from models import PollyForm, TestForm
from werkzeug.utils import secure_filename
import io
import numpy as np
import os
import soundfile as sf
import sys

if sys.version_info >= (3, 0):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
    from urllib.parse import parse_qs
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn
    from urlparse import parse_qs

# Mapping the output format used in the client to the content type for the
# response
AUDIO_FORMATS = {"ogg_vorbis": "audio/ogg",
                 'mp3': 'audio/mpeg',
                 "pcm": "audio/wave; codecs=1"}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create a client using the credentials and region defined in the adminuser
# section of the AWS credentials and configuration files
session = Session(profile_name="default")
polly = session.client("polly")


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


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles routing for Polly form and template"""
    polly_form = PollyForm()
    test_form = TestForm()

    if request.method == 'POST':
        if polly_form.validate_on_submit():
            audio_src = '/read?voiceId=' + polly_form.voiceId.data + '&text='\
            + polly_form.text.data + '&outputFormat=' +\
            polly_form.output_format.data
            return render_template('form.html', polly_form=polly_form,
                                   test_form=test_form, audio_src=audio_src)

    return render_template('form.html', polly_form=polly_form,
                           test_form=test_form, audio_src=None)


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

            return send_file(response.get("AudioStream"),
                             AUDIO_FORMATS[outputFormat])
    except:
        raise InvalidUsage("Wrong parameters", status_code=400)


@app.route('/test', methods=['GET','POST'])
def compare():
    polly_form = PollyForm()
    test_form = TestForm()
    results = None
    if request.method == 'POST':
        if test_form.validate_on_submit():
            text = test_form.test_text.data
            voiceId = test_form.test_voiceId.data
            file = test_form.file.data
            filename = os.path.splitext(secure_filename(file.filename))[0]
            try:
                # Request speech synthesis
                response = polly.synthesize_speech(Text=text,
                                                   VoiceId=voiceId,
                                                   OutputFormat="ogg_vorbis")
            except (BotoCoreError, ClientError) as err:
                # The service returned an error
                raise InvalidUsage(str(err), status_code=500)

            tmp = io.BytesIO(file.read())
            d1, r1 = sf.read(tmp, dtype='float32')
            d1, r1 = resample_for_librosa(d1, r1)
            file_path = save_as_wav(d1, r1, filename)
            d1, r1 = process_audio(d1, r1)

            # Access the audio stream from the response
            output = None
            if "AudioStream" in response:
                with closing(response["AudioStream"]) as stream:
                    try:
                        tmp = io.BytesIO(stream.read())
                    except IOError as error:
                        # Could not write to file, fail gracefully
                        raise InvalidUsage(error, status_code=400)
            else:
                # The response didn't contain audio data, fail gracefully
                raise InvalidUsage("Could not stream audio", status_code=400)

            d2, r2 = sf.read(tmp, dtype='float32')
            d2, r2 = resample_for_librosa(d2, r2)
            d2, r2 = process_audio(d2, r2)

            time_difference, dtw_dist, accuracy = compute_dist(d1, r1, d2, r2,
                                                               file_path, text)

            speed = max((60 - time_difference) / 60 * 100, 0)
            voice = max((1000 - dtw_dist) / 1000 * 100, 0)
            accuracy = accuracy * 100
            average = np.mean([speed, voice, accuracy])

            if average >= 90:
                grade = 'A'
            elif average >= 75:
                grade = 'B'
            elif average >= 60:
                grade = 'C'
            elif average >= 40:
                grade = 'D'
            elif average >= 20:
                grade = 'E'
            else:
                grade = 'F'

            results = {
                        'speed': str(round(speed, 2)),
                        'voice': str(round(voice, 2)),
                        'accuracy': str(round(accuracy, 2)),
                        'grade': grade
                      }

    return render_template('form.html', polly_form=polly_form,
                           test_form=test_form, audio_src=None,
                           results=results)


@app.route('/test/JSON', methods=['POST'])
def compare_json():
    polly_form = PollyForm(csrf_enabled=False)
    test_form = TestForm(csrf_enabled=False)
    if test_form.validate_on_submit():
        text = test_form.test_text.data
        voiceId = test_form.test_voiceId.data
        file = test_form.file.data
        filename = os.path.splitext(secure_filename(file.filename))[0]
        try:
            # Request speech synthesis
            response = polly.synthesize_speech(Text=text,
                                               VoiceId=voiceId,
                                               OutputFormat="ogg_vorbis")
        except (BotoCoreError, ClientError) as err:
            # The service returned an error
            raise InvalidUsage(str(err), status_code=500)

        tmp = io.BytesIO(file.read())
        d1, r1 = sf.read(tmp, dtype='float32')
        d1, r1 = resample_for_librosa(d1, r1)
        file_path = save_as_wav(d1, r1, filename)
        d1, r1 = process_audio(d1, r1)

        # Access the audio stream from the response
        output = None
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                try:
                    tmp = io.BytesIO(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    raise InvalidUsage(error, status_code=400)
        else:
            # The response didn't contain audio data, exit gracefully
            raise InvalidUsage("Could not stream audio", status_code=400)

        d2, r2 = sf.read(tmp, dtype='float32')
        d2, r2 = resample_for_librosa(d2, r2)
        d2, r2 = process_audio(d2, r2)

        time_difference, dtw_dist, accuracy = compute_dist(d1, r1, d2, r2,
                                                           file_path, text)

        speed = max((60 - time_difference) / 60 * 100, 0)
        voice = max((1000 - dtw_dist) / 1000 * 100, 0)
        accuracy = accuracy * 100
        average = np.mean([speed, voice, accuracy])

        if average >= 90:
            grade = 'A'
        elif average >= 75:
            grade = 'B'
        elif average >= 60:
            grade = 'C'
        elif average >= 40:
            grade = 'D'
        elif average >= 20:
            grade = 'E'
        else:
            grade = 'F'

        results = {
                    'speed': str(round(speed, 2)),
                    'voice': str(round(voice, 2)),
                    'accuracy': str(round(accuracy, 2)),
                    'grade': grade
                  }

        return jsonify(results)

    raise InvalidUsage(test_form.errors, status_code=400)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
