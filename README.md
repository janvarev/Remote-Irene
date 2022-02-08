# Голосовой ассистент Ирина - клиент

Ирина - русский голосовой ассистент для работы оффлайн. Требует Python 3.5+ (зависимость может быть меньше, но в любом случае Python 3)

Это клиент для мультиинсталляции.

Сервер и основной вариант Ирины здесь: https://github.com/janvarev/Irene-Voice-Assistant

### Установка / быстрый старт

1. Для быстрой установки всех требуемых зависимостей можно воспользоваться командой:
```pip install -r requirements.txt```

2. Запустите сервер Ирины

3. Есть несколько клиентов. Самый простой - **run_remoteva_vosk.py**
Сконфигурируйте его (опции в options.json) - надо задать адрес сервера Ирины и режим работы TTS. 

3. После запуска проверить можно простой командой - скажите "Ирина, привет!" в микрофон

### Опции

В файле options.json, отредактируйте их под вас.

```
ttsFormat = "saywav"
``` 
Варианты:
- "none" (TTS реакции будут на сервере) (звук на сервере)
- "saytxt" (сервер вернет текст, TTS будет на клиенте) (звук на клиенте)
- "saywav" (TTS на сервере, сервер отрендерит WAV и вернет клиенту, клиент его проиграет) (звук на клиенте) **наиболее универсальный для клиента**

```
baseUrl = "http://127.0.0.1:5003/" 
``` 

Адрес сервера с Ириной

### Auto-py-to-exe

Клиент **run_remoteva_vosk.py** можно собрать для в виде автономного EXE-файла через auto-py-to-exe.
Версия получается рабочей

Настройки в auto-py-to-exe.json. 
Потребуется отредактировать опцию vosk, настроив источник на вашу Python-установку 
(чтобы скопировать библиотеку, без неё не заработает)

[Скачать собранную версию 1.1 в EXE](https://download.janvarev.ru/vairene/run_remoteva_vosk11.rar)

