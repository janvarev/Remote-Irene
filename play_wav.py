import os

from audioplayer import AudioPlayer

def play_wav(wavfile):
    AudioPlayer(wavfile).play(block=True)

def saywav_to_file(saywav_result,wavfile):
    import save_wav
    save_wav.saywav_to_file(saywav_result,wavfile)
