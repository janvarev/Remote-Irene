# you need to install:
# pip install PyAudio
# pip install SpeechRecognition

# if you have problems with PyAudio install, check this:
# https://github.com/EnjiRouz/Voice-Assistant-App/blob/master/README.md

import speech_recognition
import os

import json
import requests
import play_wav

# main options
with open('options.json', 'r', encoding="utf-8") as f:
    s = f.read(10000000)
    f.close()
saved_options = json.loads(s)

ttsFormat = saved_options["ttsFormat"] # "none" (TTS on server) or "saytxt" (TTS on client)
                            # or "saywav" (TTS on server to WAV, Wav played on client)
ttsFormatList = ttsFormat.split(",")
baseUrl = saved_options["baseUrl"] # server with Irene WEB api

# pyttsx for saytxt
if "saytxt" in ttsFormatList:
    import pyttsx3
    ttsEngine = pyttsx3.init()
    voices = ttsEngine.getProperty("voices")
    ttsEngine.setProperty("voice", 0)


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


recognizeFormat = "vosk" # "google" or "vosk"

if recognizeFormat == "vosk":
    # проверка наличия модели на нужном языке в каталоге приложения
    if not os.path.exists("model"):
        print("Please download the model from:\n"
              "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1)

    from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
    model = Model("model")




def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        try:
            #print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        # использование online-распознавания через Google
        if recognizeFormat == "google":
            try:
                #print("Started recognition...")
                recognized_data = recognizer.recognize_google(audio, language="ru").lower()

            except speech_recognition.UnknownValueError:
                pass

            # в случае проблем с доступом в Интернет происходит выброс ошибки
            except speech_recognition.RequestError:
                print("Check your Internet Connection, please")

            return recognized_data

        if recognizeFormat == "vosk":
            return use_vosk_recognition()

        return ""

def use_vosk_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """

    import wave  # создание и чтение аудиофайлов формата wav

    recognized_data = ""
    try:
        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())
        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки
                # (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data

# ------------------- vosk ------------------
import json


if __name__ == "__main__":
    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # if saytxt logic, we need to init tts engine
    if ttsFormat == "saytxt":
        import pyttsx3
        ttsEngine = pyttsx3.init()
        voices = ttsEngine.getProperty("voices")
        ttsEngine.setProperty("voice", 0)


    with microphone:
        # регулирование уровня окружающего шума
        print("Adjusting...")
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

    print("Listening!")
    while True:
        # старт записи речи с последующим выводом распознанной речи
        voice_input_str = record_and_recognize_audio()
        if voice_input_str != "" and voice_input_str != None:
            print(voice_input_str)

            try:
                r = requests.get(baseUrl+"sendRawTxt", params={"rawtxt": voice_input_str, "returnFormat": ttsFormat})
                if r.text != "":
                    res = json.loads(r.text)
                    if res != "NO_VA_NAME": # some cmd was run
                        if res != None and res != "": # there is some response to play
                            if "saytxt" in ttsFormatList:
                                if "restxt" in res.keys():
                                    ttsEngine.say(res["restxt"])
                                    ttsEngine.runAndWait()

                            if "saywav" in ttsFormatList:
                                play_wav.saywav_to_file(res,'tmpfile.wav')
                                play_wav.play_wav('tmpfile.wav')

            except requests.ConnectionError as e:
                play_wav.play_wav('error_connection.wav')
            except Exception as e:
                play_wav.play_wav('error_processing.wav')

        else:
            #print("2",rec.PartialResult())
            pass