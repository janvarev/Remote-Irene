import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys

import requests
import json

import play_wav

version="1.0"

# main options
with open('options.json', 'r', encoding="utf-8") as f:
    s = f.read(10000000)
    f.close()
saved_options = json.loads(s)

ttsFormat = saved_options["ttsFormat"] # "none" (TTS on server) or "saytxt" (TTS on client)
                    # or "saywav" (TTS on server to WAV, Wav played on client)
baseUrl = saved_options["baseUrl"] # server with Irene WEB api

if os.path.exists("error_connection.wav"):
    pass
else: # первый вызов, давайте получим файлы
    print("Получаем WAV-файлы, которые будут играться в случае ошибок...")

    r = requests.get(baseUrl+"ttsWav", params={"text": "Ошибка: потеряна связь с сервером"})
    res = json.loads(r.text)
    play_wav.saywav_to_file(res,'error_connection.wav')

    r = requests.get(baseUrl+"ttsWav", params={"text": "Ошибка при обработке результата сервера"})
    res = json.loads(r.text)
    play_wav.saywav_to_file(res,'error_processing.wav')

    print("WAV-файлы для ошибок получены!")


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


        print("Remote Irene (VOSK) v{0} started! ttsFormat={1}, baseUrl={2}".format(version,ttsFormat,baseUrl))

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

                        try:
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
                                    play_wav.saywav_to_file(res,'tmpfile.wav')
                                    play_wav.play_wav('tmpfile.wav')
                        except requests.ConnectionError as e:
                            play_wav.play_wav('error_connection.wav')
                        except Exception as e:
                            play_wav.play_wav('error_processing.wav')

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