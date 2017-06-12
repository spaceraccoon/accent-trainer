# From https://github.com/dwww2012/Accent-Classifier

import numpy as np
# import pandas as pd
# from features import mfcc
# from features import logfbank
from scipy.signal import butter, lfilter
from scipy.spatial.distance import euclidean
# import scipy.io.wavfile as wav
# from scipy.io.wavfile import write as wav_write
import librosa
import librosa.display
# import scikits.samplerate
# import os
import os
import matplotlib.pyplot as plt
from python_speech_features import mfcc, delta, logfbank
from fastdtw import fastdtw
from cydtw import dtw
from sklearn.metrics.pairwise import euclidean_distances

def convert_to_wav(file_path):
    y, sr = librosa.load(file_path)
    filename = os.path.splitext(file_path)[0]
    librosa.output.write_wav('{}.wav'.format(filename), y, sr)

# '''
# mfcc(signal, samplerate=16000, winlen=0.025, winstep=0.01, numcep=13, nfilt=26, nfft=512, lowfreq=0, highfreq=None, preemph=0.97, ceplifter=22, appendEnergy=True)
# '''
# read in signal and rate, change sample rate to outrate (samples/sec), use write_wav=True to save wav file to disk
def filter_audio(file_path, write_wav = False):
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
        filename = os.path.splitext(file_path)[0]
        librosa.output.write_wav('{}_processed.wav'.format(filename), yt, sr)
    else:
        return yt, r

def plot_spec(file_path):

    #Loading audio files
    y2, sr2 = librosa.load(file_path)   #y2 is model
    y1, sr1 = librosa.load('model_processed.wav')

    # print(y1)

    # plt.figure()
    # plt.subplot(221)
    # plt.plot(y1)
    # plt.subplot(223)
    # plt.plot(y2)
    # plt.show()

    # normalize clips
    yn1, yn2 = normalize(y1, y2)

    # plt.figure()
    # plt.subplot(221)
    # plt.plot(yn1)
    # plt.subplot(223)
    # plt.plot(yn2)
    # plt.show()

    time_difference = np.absolute(librosa.get_duration(y1) - librosa.get_duration(y2))
    print('Time difference: {}'.format(time_difference))

    # absolute_distance1 = sum(np.absolute(yn1-yn2))
    # print('Absolute difference: {}'.format(absolute_distance1))
    # absolute_distance2 = sum(np.absolute(yn1-yn1))

    # S1 = librosa.feature.melspectrogram(y=y1, sr=sr1, n_mels=128, fmax=8000)
    mfcc1 =  mfcc(y1,sr1, numcep=20)
    # mfcc1 = librosa.feature.mfcc(y=y1,sr=sr1, S=librosa.power_to_db(S1))
    d_mfcc_feat1 = delta(mfcc1, 2)
    # fbank_feat = logfbank(y1,sr1)

    mfcc2 =  mfcc(y2,sr2, numcep=20)
    # S2 = librosa.feature.melspectrogram(y=y2, sr=sr2, n_mels=128, fmax=8000)
    # mfcc2 = librosa.feature.mfcc(y=y2,sr=sr2, S=librosa.power_to_db(S2))
    d_mfcc_feat2 = delta(mfcc2, 2)
    # fbank_feat2 = logfbank(y2,sr2)

    # plt.subplot(221)
    # librosa.display.specshow(mfcc1)
    # plt.subplot(223)
    # librosa.display.specshow(mfcc2)
    # plt.show()

    # distance1 = sum(sum(np.absolute(mfcc1 - mfcc2)))
    # distance2 = sum(sum(np.absolute(mfcc2 - mfcc2)))
    # print('Absolute difference mfcc: {}'.format(distance1))

    dtw_dist = dtw(d_mfcc_feat1, d_mfcc_feat2)
    print('dtw distance mfcc: {}'.format(dtw_dist))

    # librosa.display.specshow(mfcc1)
    # librosa.display.specshow(mfcc2)
    # plt.show()

# # read in signal, take absolute value and slice seconds 1-3 from beginning
# def get_two_secs(filename):
#     sig, rate = read_in_audio(filename)
#     abs_sig = np.abs(sig)
#     two_secs = abs_sig[rate:3*rate]
#     return two_secs

# # calculates moving average for a specified window (number of samples)
# def take_moving_average(sig, window_width):
#     cumsum_vec = np.cumsum(np.insert(sig, 0, 0))
#     ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width])/float(window_width)
#     return ma_vec

# change total number of samps for downsampled file to n_samps by trimming or zero-padding and standardize them
def normalize(y1, y2):
    # normalize duration
    # time_ratio = librosa.get_duration(y1) / librosa.get_duration(y2)
    # y1 = librosa.effects.time_stretch(y1,time_ratio)
    # y1 = librosa.util.fix_length(y1, len(y2))

    # normalize volume
    y1 = librosa.util.normalize(y1)
    y2 = librosa.util.normalize(y2)

    return y1, y2

# # from a folder containing wav files, normalize each, divide into num_splits-1 chunks and write the resulting np.arrays to a single matrix
# def make_split_audio_array(folder, num_splits = 5):
#     lst = []
#     for filename in os.listdir(folder):
#         if filename.endswith('wav'):
#             normed_sig = make_standard_length(filename)
#             chunk = normed_sig.shape[0]/num_splits
#             for i in range(num_splits - 1):
#                 lst.append(normed_sig[i*chunk:(i+2)*chunk])
#     lst = np.array(lst)
#     lst = lst.reshape(lst.shape[0], -1)
#     return lst

# # for input wav file outputs (13, 2999) mfcc np array
# def make_normed_mfcc(filename, outrate=8000):
#     normed_sig = make_standard_length(filename)
#     normed_mfcc_feat = mfcc(normed_sig, outrate)
#     normed_mfcc_feat = normed_mfcc_feat.T
#     return normed_mfcc_feat

# # make mfcc np array from wav file using librosa package
# def make_librosa_mfcc(filename):
#      y, sr = librosa.load(filename)
#      mfcc_feat = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
#      return mfcc_feat

# # make mfcc np array from wav file using speech features package
# def make_mfcc(filename):
#     (rate, sig) = wav.read(filename)
#     mfcc_feat = mfcc(sig, rate)
#     mfcc_feat = mfcc_feat.T
#     return mfcc_feat

# # for folder containing wav files, output numpy array of normed mfcc
# def make_class_array(folder):
#     lst = []
#     for filename in os.listdir(folder):
#         lst.append(make_normed_mfcc(filename))
#     class_array = np.array(lst)
#     class_array = np.reshape(class_array, (class_array.shape[0], class_array.shape[2], class_array.shape[1]))
#     return class_array

# # read in wav file, output (1,13) numpy array of mean mfccs for each of 13 features
# def make_mean_mfcc(filename):
#     try:
#         (rate, sig) = wav.read(filename)
#         mfcc_feat = mfcc(sig, rate)
#         avg_mfcc = np.mean(mfcc_feat, axis = 0)
#         return avg_mfcc
#     except:
#         pass

# # write new csv corresponding to dataframe of given language and gender
# def make_df_language_gender(df, language, gender):
#     newdf = df.query("native_language == @language").query("sex == @gender")
#     newdf.to_csv('df_{}_{}.csv'.format(language, gender))

# # write new directories to disk containing the male and female speakers from the most common languages
# def make_folders_from_csv():
#     top_15_langs = ['english', 'spanish', 'arabic', 'mandarin', 'french', 'german', 'korean', 'russian', 'portuguese', 'dutch', 'turkish', 'italian', 'polish', 'japanese', 'vietnamese']
#     for lang in top_15_langs:
#         os.makedirs('{}/{}_male'.format(lang, lang))
#         os.makedirs('{}/{}_female'.format(lang, lang))

# # copy files to the corresponding directories
# def copy_files_from_csv():
#     top_15_langs = ['english', 'spanish', 'arabic', 'mandarin', 'french', 'german', 'korean', 'russian', 'portuguese', 'dutch', 'turkish', 'italian', 'polish', 'japanese', 'vietnamese']
#     for lang in top_15_langs:
#         df_male = pd.read_csv('df_{}_male.csv'.format(lang))
#         df_female = pd.read_csv('df_{}_female.csv'.format(lang))
#         m_list = df_male['filename'].values
#         f_list = df_female['filename'].values
#         for filename in f_list:
#             shutil.copy2('big_langs/{}/{}.wav'.format(lang, filename), 'big_langs/{}/{}_female/{}.wav'.format(lang, lang, filename))

# # input folder of wav files, output pandas dataframe of mean mfcc values
# def make_mean_mfcc_df(folder):
#     norms = []
#     for filename in os.listdir(folder):
#         (rate, sig) = wav.read(filename)
#         mfcc_feat = mfcc(sig, rate)
#         mean_mfcc = np.mean(mfcc_feat, axis = 0)
#         #mean_mfcc = np.reshape(mean_mfcc, (1,13))
#         norms.append(mean_mfcc)
#     flat = [a.ravel() for a in norms]
#     stacked = np.vstack(flat)
#     df = pd.DataFrame(stacked)
#     return df
