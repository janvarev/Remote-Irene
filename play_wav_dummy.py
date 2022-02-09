def play_wav(wavfile):
    print("PLAY_WAV_DUMMY: не могу проиграть {0}. Попробуйте другой режим вызова Ирины.".format(wavfile))

def saywav_to_file(saywav_result,wavfile):
    import save_wav
    save_wav.saywav_to_file(saywav_result,wavfile)
