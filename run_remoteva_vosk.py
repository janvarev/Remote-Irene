import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys

import requests
import json

# main option
ttsFormat = "saywav" # "none" (TTS on server) or "saytxt" (TTS on client)
                    # or "saywav" (TTS on server to WAV, Wav played on client)
baseUrl = "http://127.0.0.1:5003/" # server with Irene WEB api


if ttsFormat == "saytxt":
    import pyttsx3
    ttsEngine = pyttsx3.init()
    voices = ttsEngine.getProperty("voices")
    ttsEngine.setProperty("voice", 0)


mic_blocked = False

# ------------------- vosk ------------------
if __name__ == "__main__":
    q = queue.Queue()



    def int_or_str(text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        if not mic_blocked:
            q.put(bytes(indata))

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-f', '--filename', type=str, metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-m', '--model', type=str, metavar='MODEL_PATH',
        help='Path to the model')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    args = parser.parse_args(remaining)
    #args = {}

    try:
        if args.model is None:
            args.model = "model"
        if not os.path.exists(args.model):
            print ("Please download a model for your language from https://alphacephei.com/vosk/models")
            print ("and unpack as 'model' in the current folder.")
            parser.exit(0)
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])

        model = vosk.Model(args.model)

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None



        with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                               channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)

            while True:
                data = q.get()
                if rec.AcceptWaveform(data):

                    recognized_data = rec.Result()

                    #print("1",recognized_data)

                    #print(recognized_data)
                    recognized_data = json.loads(recognized_data)
                    #print(recognized_data)
                    voice_input_str = recognized_data["text"]


                    if voice_input_str != "" and voice_input_str != None:
                        print(voice_input_str)

                        if ttsFormat == "none":
                            # for TTS on server
                            r = requests.get(baseUrl+"sendRawTxt", params={"rawtxt": voice_input_str, "returnFormat": "none"})

                        if ttsFormat == "saytxt":
                            # for TTS on client
                            r = requests.get(baseUrl+"sendRawTxt", params={"rawtxt": voice_input_str, "returnFormat": "saytxt"})
                            res = json.loads(r.text)
                            if res != "NO_VA_NAME": # some cmd was run
                                ttsEngine.say(res)
                                ttsEngine.runAndWait()

                        if ttsFormat == "saywav":
                            # (TTS on server to WAV, Wav played on client)
                            r = requests.get(baseUrl+"sendRawTxt", params={"rawtxt": voice_input_str, "returnFormat": "saywav"})
                            res = json.loads(r.text)
                            if res != "NO_VA_NAME": # some cmd was run
                                b64 = res["wav_base64"]
                                base64_message = b64.encode('utf-8')

                                import base64

                                with open('tmpfile.wav', 'wb') as file_to_save:
                                    decoded_image_data = base64.decodebytes(base64_message)
                                    file_to_save.write(decoded_image_data)

                                from play_wav import play_wav
                                play_wav('tmpfile.wav')


                    else:
                        #print("2",rec.PartialResult())
                        pass



                if dump_fn is not None:
                    dump_fn.write(data)

    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))