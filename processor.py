import numpy as np
from scipy.signal import butter, lfilter
import librosa
import librosa.display
import os
import matplotlib.pyplot as plt
from python_speech_features import mfcc, delta, logfbank
from cydtw import dtw

CONVERT_FOLDER = 'converted/'
PROCESS_FOLDER = 'processed/'

def convert_to_wav(file_path):
    y, sr = librosa.load(file_path)
    # TO cleanup
    filename = os.path.split(file_path)[1]
    filename = os.path.splitext(filename)[0]
    new_path = '{}{}.wav'.format(CONVERT_FOLDER, filename)
    librosa.output.write_wav(new_path, y, sr)
    return new_path

def process_audio(file_path, write_wav = False):
    y, sr = librosa.load(file_path)

    # Trim silence at start and end
    yt, index = librosa.effects.trim(y,15)

    # Apply pre-emphasis filter_audio
    # pre_emphasis = 0.97
    # ye = np.append(yt[0], yt[1:] - pre_emphasis * yt[:-1])

    # Apply butterworth bandpass filter
    b, a = butter(4, [0.05,0.8], 'bandpass')
    yf = lfilter(b, a, yt)


    if write_wav:
        filename = os.path.split(file_path)[1]
        filename = os.path.splitext(filename)[0]
        new_path = '{}{}.wav'.format(PROCESS_FOLDER, filename)
        librosa.output.write_wav(new_path, yt, sr)
    else:
        return yt, sr

def compute_dist(y2,sr2):

    #Loading audio files
    # y2, sr2 = librosa.load(file_path)
    y1, sr1 = librosa.load('model_processed.wav')

    # normalize clips
    yn1, yn2 = normalize(y1, y2)

    time_difference = np.absolute(librosa.get_duration(y1) - librosa.get_duration(y2))
    print('Time difference: {}'.format(time_difference))

    mfcc1 =  mfcc(y1,sr1, numcep=20)
    d_mfcc_feat1 = delta(mfcc1, 2)
    # fbank_feat = logfbank(y1,sr1)

    mfcc2 =  mfcc(y2,sr2, numcep=20)
    d_mfcc_feat2 = delta(mfcc2, 2)
    # fbank_feat2 = logfbank(y2,sr2)

    dtw_dist = dtw(d_mfcc_feat1, d_mfcc_feat2)
    print('dtw distance mfcc: {}'.format(dtw_dist))

    # librosa.display.specshow(mfcc1)
    # librosa.display.specshow(mfcc2)
    # plt.show()
    return time_difference, dtw_dist

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
