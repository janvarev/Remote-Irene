import telebot
import json
import random
import time
import requests

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



bot = telebot.TeleBot(options_tele["botKey"])

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.chat.id in options_tele["adminChats"]:
        voice_input_str = message.text.lower()
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

        pass
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

bot.infinity_polling()

