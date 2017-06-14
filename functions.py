from cydtw import dtw
from difflib import SequenceMatcher
import librosa
import librosa.display
import numpy as np
import os
from python_speech_features import mfcc, delta, logfbank
import random
from scipy.signal import butter, lfilter
import soundfile as sf
import speech_recognition as sr
import string

BING_KEY = "INSERT BING KEY HERE"
CONVERT_FOLDER = 'converted/'
recognizer = sr.Recognizer()


# Need to transpose and resample soundfile for processing with librosa
def resample_for_librosa(d, r):
    d = d.T
    d = librosa.resample(d, r, 44100)
    sr = 44100
    return d, r


# Save using sf instead of librosa to match pcm subtype for bing
def save_as_wav(d, r, filename):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase +
                              string.digits) for _ in range(24))
    new_path = '{}{}_{}.wav'.format(CONVERT_FOLDER, x, filename)
    d = d.T
    # librosa.output.write_wav(new_path, d, r)
    sf.write(new_path, d, r, 'PCM_24')
    return new_path


def process_audio(d, r):
    # Trim silence at start and end
    dt, index = librosa.effects.trim(d, 15)

    # Apply pre-emphasis filter_audio
    # pre_emphasis = 0.97
    # ye = np.append(yt[0], yt[1:] - pre_emphasis * yt[:-1])

    # Apply butterworth bandpass filter
    b, a = butter(4, [0.05, 0.8], 'bandpass')
    df = lfilter(b, a, dt)

    return dt, r


def compute_dist(y1, r1, y2, r2, file_path, text):

    # normalize clips
    yn1, yn2 = normalize(y1, y2)

    time_difference = np.absolute(librosa.get_duration(y1) -
                                  librosa.get_duration(y2))
    print('Time difference: {}'.format(time_difference))

    mfcc1 = mfcc(y1, r1, numcep=20)
    d_mfcc_feat1 = delta(mfcc1, 2)
    # fbank_feat = logfbank(y1,r1)

    mfcc2 = mfcc(y2, r2, numcep=20)
    d_mfcc_feat2 = delta(mfcc2, 2)
    # fbank_feat2 = logfbank(y2,r2)

    dtw_dist = dtw(d_mfcc_feat1, d_mfcc_feat2)
    print('dtw distance mfcc: {}'.format(dtw_dist))

    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)  # read the entire audio file

    try:
        recognized_text = recognizer.recognize_bing(audio, key=BING_KEY)
        print(recognized_text)
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator).lower()
        accuracy = SequenceMatcher(None, recognized_text, text).ratio()
    except sr.UnknownValueError:
        print("Microsoft Bing Voice Recognition could not understand audio")
        accuracy = 0.0
    except sr.RequestError as e:
        print("Could not request results from Microsoft Bing Voice Recognition\
              service; {0}".format(e))

    return time_difference, dtw_dist, accuracy


# normalize duration and volume of two signals
def normalize(y1, y2):
    # normalize duration
    # time_ratio = librosa.get_duration(y1) / librosa.get_duration(y2)
    # y1 = librosa.effects.time_stretch(y1,time_ratio)
    # y1 = librosa.util.fix_length(y1, len(y2))

    # normalize volume
    y1 = librosa.util.normalize(y1)
    y2 = librosa.util.normalize(y2)

    return y1, y2
