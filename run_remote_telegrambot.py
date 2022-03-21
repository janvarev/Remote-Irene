import telebot
import json
import random
import time
import requests

version = "1.1"

# options
with open('options.json', 'r', encoding="utf-8") as f:
    s = f.read(10000000)
    f.close()
saved_options = json.loads(s)

ttsFormat = saved_options["ttsFormat"] # "none" (TTS on server) or "saytxt" (TTS on client)
# or "saywav" (TTS on server to WAV, Wav played on client)
ttsFormatList = ttsFormat.split(",")
if not "saytxt" in ttsFormatList: # saytxt обязателен
    ttsFormatList.append("saytxt")
    ttsFormat += ",saytxt"

baseUrl = saved_options["baseUrl"] # server with Irene WEB api

with open('options_telegrambot.json', 'r', encoding="utf-8") as f:
    s = f.read(10000000)
    f.close()
options_tele = json.loads(s)

def save_options_tele(new_options_tele):
    options_tele = new_options_tele
    str_options = json.dumps(options_tele, sort_keys=True, indent=4, ensure_ascii=False)
    with open('options_telegrambot.json', 'w', encoding="utf-8") as f:
        f.write(str_options)
        f.close()

if options_tele["botKey"] == "":
    print("Не найден ключ бота. Посетите @BotFather и сгенерируйте ключ для вашего бота")
    exit()

print("Текущих чатов с администратором: {0}".format(len(options_tele["adminChats"])))
randKeyAdmin = str(random.randint(100000,999999))
if options_tele["allowAddAdmins"]:
    print("Ключ для подключения администратора (введите в диалоге с ботом): ",randKeyAdmin)
else:
    print("Подключение новых администраторов ЗАБЛОКИРОВАНО. Для добавления других админов отредактируйте options_telegrambot.json")

isVoicePlayingEnabled = False

if options_tele["voiceMsgProcessor"] == "play":
    try:
        import play_wav
        isVoicePlayingEnabled = True
    except ImportError:
        pass

    if isVoicePlayingEnabled:
        print("Озвучка полученных голосовых сообщений РАБОТАЕТ")
    else:
        print("Озвучка полученных голосовых сообщений НЕ работает")

isVoskRecEnabled = False

if options_tele["voiceMsgProcessor"] == "rec_vosk":
    try:
        import play_wav
        import os
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("model"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            raise Exception()

        from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
        model = Model("model")
        isVoskRecEnabled = True
    except Exception:
        pass

    if isVoskRecEnabled:
        print("VOSK-распознавание голосовых сообщений РАБОТАЕТ")
    else:
        print("VOSK-распознавание голосовых сообщений НЕ работает")


bot = telebot.TeleBot(options_tele["botKey"])
latestRec = ""

print("Remote Irene (Telegram client) v{0} started! ttsFormat={1}, baseUrl={2}".format(version,ttsFormat,baseUrl))

def send_cmd_towebapi(cmd,message):
    voice_input_str = cmd
    if voice_input_str != "" and voice_input_str != None:
        print(voice_input_str)
        try:
            r = requests.get(baseUrl+"sendTxtCmd", params={"cmd": voice_input_str, "returnFormat": ttsFormat})
            processed = False
            if r.text != "":
                res = json.loads(r.text)
                if res != "NO_VA_NAME": # some cmd was run
                    if res != None and res != "": # there is some response to play
                        if "saytxt" in ttsFormatList:
                            if "restxt" in res.keys():
                                bot.send_message(message.chat.id, res["restxt"])
                                processed = True

            if not processed:
                bot.send_message(message.chat.id, "Не распознано / нет ответа")

        except requests.ConnectionError as e:
            bot.send_message(message.chat.id, "Ошибка связи с Web api")
        except Exception as e:
            bot.send_message(message.chat.id, "Ошибка обработки сообщения")

    else:
        #print("2",rec.PartialResult())
        pass


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.chat.id in options_tele["adminChats"]:
        if message.text == "/runrecognized":
            send_cmd_towebapi(latestRec,message)
        elif message.text == "/playwav":
            play_wav.play_wav("temp_voice.wav")
            bot.send_message(message.chat.id, "Сообщение проиграно")
        else:
            send_cmd_towebapi(message.text.lower(),message)
    else:
        time.sleep(1)
        if options_tele["allowAddAdmins"]:
            if message.text == randKeyAdmin:
                options_tele["adminChats"].append(message.chat.id)
                options_tele["allowAddAdmins"] = False
                save_options_tele(options_tele)
                bot.send_message(message.chat.id, "Вы добавлены как администратор. Добавление других администраторов заблокировано. Для добавления других админов отредактируйте options_telegrambot.json.")
                bot.send_message(message.chat.id, "Для отправки команды Ирине просто введите команду в чат.")
            else:
                bot.send_message(message.chat.id, "?")
        else:
            bot.send_message(message.chat.id, "Доступ заблокирован")

def use_vosk_recognition(wavfilename):
    import wave  # создание и чтение аудиофайлов формата wav

    recognized_data = ""
    try:
        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open(wavfilename, "rb")

        if wave_audio_file.getnchannels() != 1 or wave_audio_file.getsampwidth() != 2 or wave_audio_file.getcomptype() != "NONE":
            print ("Audio file must be WAV format mono PCM.")

        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())
        #print(wave_audio_file.getframerate())
        data = wave_audio_file.readframes(wave_audio_file.getnframes())

        if len(data) > 0:
            offline_recognizer.AcceptWaveform(data)
            recognized_data = offline_recognizer.Result()

            recognized_data = json.loads(recognized_data)
            recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    if message.chat.id in options_tele["adminChats"]:
        if options_tele["voiceMsgProcessor"] == "none": # формат - проигрывание полученных сообщений
            bot.send_message(message.chat.id, "Обработка голосовых сообщений не установлена (может быть установлена в проигрывание (play) или распознавание команд (rec_vosk)")

        if options_tele["voiceMsgProcessor"] == "play": # формат - проигрывание полученных сообщений
            if isVoicePlayingEnabled:
                file_info = bot.get_file(message.voice.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open('temp_voice.ogg', 'wb') as new_file:
                    new_file.write(downloaded_file)

                import subprocess
                process = subprocess.run(['ffmpeg', '-i', "temp_voice.ogg", "temp_voice.wav", '-y'])
                if process.returncode != 0:
                    bot.send_message(message.chat.id, "Проблемы с перекодированием голосового сообщения")
                else:
                    play_wav.play_wav("temp_voice.wav")
                    bot.send_message(message.chat.id, "Сообщение проиграно")
            else:
                bot.send_message(message.chat.id, "Проигрывание голосовых файлов не работает")

        if options_tele["voiceMsgProcessor"] == "rec_vosk": # формат - распознавание vosk
            if isVoskRecEnabled:
                file_info = bot.get_file(message.voice.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open('temp_voice.ogg', 'wb') as new_file:
                    new_file.write(downloaded_file)

                import subprocess
                process = subprocess.run(['ffmpeg', '-i', "temp_voice.ogg",
                                          #'-ar', '16000',
                                          '-ac', '1',
                                          #'-acodec', 'pcm_s16le',
                                          "temp_voice.wav", '-y'])
                if process.returncode != 0:
                    bot.send_message(message.chat.id, "Проблемы с перекодированием голосового сообщения")
                else:
                    voice_inp_str = use_vosk_recognition("temp_voice.wav")
                    print("Распознанная фраза: ",voice_inp_str)
                    global latestRec
                    latestRec = voice_inp_str
                    #send_cmd_towebapi(voice_inp_str,message)
                    bot.send_message(message.chat.id, "Распознано: "+latestRec+". Нажмите /runrecognized или /playwav")
            else:
                bot.send_message(message.chat.id, "Распознавание голосовых файлов (VOSK) не работает")


bot.infinity_polling()

