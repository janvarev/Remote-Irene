"""
Абсолютно минимальный вариант для удаленного управления Ириной через командную строку
Только на нативных функциях Python
(требует файл pysimpleurl.py для GET-запросов, может быть заменен на requests, пример в run_remoteva_cmdline.py)
Может быть собран с помощью auto-py-to-exe в один файл.
"""
import json

from pysimpleurl import request

version="1.3"

# ---------- main options -------------
with open('options.json', 'r', encoding="utf-8") as f:
    s = f.read(10000000)
    f.close()
saved_options = json.loads(s)

ttsFormat = saved_options["ttsFormat"] # "none" (TTS on server) or "saytxt" (text on client)
if ttsFormat == "saywav": ttsFormat = "saytxt" # saywav не поддерживается
baseUrl = saved_options["baseUrl"] # server with Irene WEB api

# ----- main procedure -------
if __name__ == "__main__":
    print("Remote Irene (Command line variation min) v{0} started! ttsFormat={1}, baseUrl={2}".format(version,ttsFormat,baseUrl))
    print("---------------------")
    print("Введите команду для голосового помощника.")
    print("Пример 'привет', 'брось кубик', 'exit'.")
    while True:
        cmd = input("VA CMD> ")
        if cmd == "exit":
            break
        if cmd != "" and cmd != None:
            try:
                r = request(baseUrl+"sendTxtCmd", params={"cmd": cmd, "returnFormat": ttsFormat})
                if r.status == 200:
                    if r.body != "":
                        res = json.loads(r.body)
                        if res != None and res != "": # there is some response to play
                            print("ОТВЕТ: "+res)
                else:
                    print("Ошибка: статус не 200")
            except Exception as e:
                print("Ошибка связи с сервером (вероятно) или обработки результата")


