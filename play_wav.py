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
    b64 = saywav_result["wav_base64"]
    base64_message = b64.encode('utf-8')

    import base64

    with open(wavfile, 'wb') as file_to_save:
        decoded_image_data = base64.decodebytes(base64_message)
        file_to_save.write(decoded_image_data)
