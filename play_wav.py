import os
import soundfile as sound_file
import sounddevice as sound_device

def play_wav(wavfile):


    filename = os.path.dirname(__file__)+"/"+wavfile

    #filename = 'timer/Sounds/Loud beep.wav'
    # now, Extract the data and sampling rate from file
    data_set, fsample = sound_file.read(filename, dtype = 'float32')
    sound_device.play(data_set, fsample)
    # Wait until file is done playing
    status = sound_device.wait()

def saywav_to_file(saywav_result,wavfile):
    import save_wav
    save_wav.saywav_to_file(saywav_result,wavfile)
