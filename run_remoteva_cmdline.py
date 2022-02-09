"""
Минимальный вариант для удаленного управления Ириной через командную строку
Требует только

requests
soundfile
sounddevice

В случае, если установлен режим none (без необходимости проигрывать звук на клиенте),
требования сводятся только к

requests
"""


import os
import json

import requests

import play_wav

version="1.1"

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

if __name__ == "__main__":

        print("Remote Irene (Command line variation) v{0} started! ttsFormat={1}, baseUrl={2}".format(version,ttsFormat,baseUrl))
        print("---------------------")
        print("Введите команду для голосового помощника.")
        print("Пример 'привет', 'брось кубик', 'exit'.")
        while True:
            cmd = input("VA CMD> ")
            if cmd == "exit":
                break

            voice_input_str = cmd
            if voice_input_str != "" and voice_input_str != None:
                try:
                    if ttsFormat == "none":
                        # for TTS on server
                        r = requests.get(baseUrl+"sendTxtCmd", params={"cmd": voice_input_str, "returnFormat": "none"})

                    if ttsFormat == "saytxt":
                        # for TTS on client
                        r = requests.get(baseUrl+"sendTxtCmd", params={"cmd": voice_input_str, "returnFormat": "saytxt"})
                        res = json.loads(r.text)
                        if res != "NO_VA_NAME": # some cmd was run
                            if res != None and res != "": # there is some response to play
                                ttsEngine.say(res)
                                ttsEngine.runAndWait()

                    if ttsFormat == "saywav":
                        # (TTS on server to WAV, Wav played on client)
                        r = requests.get(baseUrl+"sendTxtCmd", params={"cmd": voice_input_str, "returnFormat": "saywav"})
                        res = json.loads(r.text)
                        if res != "NO_VA_NAME": # some cmd was run
                            if res != None and res != "": # there is some response to play
                                play_wav.saywav_to_file(res,'tmpfile.wav')
                                play_wav.play_wav('tmpfile.wav')
                except requests.ConnectionError as e:
                    play_wav.play_wav('error_connection.wav')
                except Exception as e:
                    play_wav.play_wav('error_processing.wav')

            else:
                pass


