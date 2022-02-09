"""
Абсолютно минимальный вариант для удаленного управления Ириной через командную строку
Требует только ```pip install requests```
Может быть собран с помощью auto-py-to-exe в один файл.
"""
import json

import requests

version="1.2"

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
                r = requests.get(baseUrl+"sendTxtCmd", params={"cmd": cmd, "returnFormat": ttsFormat})
                if r.text != "":
                    res = json.loads(r.text)
                    if res != None and res != "": # there is some response to play
                        print("ОТВЕТ: "+res)

            except requests.ConnectionError as e:
                print("Ошибка связи с сервером")
            except Exception as e:
                print("Ошибка обработка результата")


