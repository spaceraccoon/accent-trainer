from processor import convert_ogg_to_wav, read_in_audio, filter_audio

convert_ogg_to_wav('test_file.ogg')

filter_audio('test_file.wav', write_wav = True)
