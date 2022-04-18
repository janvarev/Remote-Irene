# Голосовой ассистент Ирина - клиент

Ирина - русский голосовой ассистент для работы оффлайн. Требует Python 3.5+ (зависимость может быть меньше, но в любом случае Python 3)

Это клиент для мультиинсталляции, а также Телеграм-клиент

Сервер и основной вариант Ирины здесь: https://github.com/janvarev/Irene-Voice-Assistant

### Установка / быстрый старт

1. Для быстрой установки всех требуемых зависимостей можно воспользоваться командой:
```pip install -r requirements.txt```
(pyTelegramBotAPI нужен только для телеграм-клиента)
(Для Linux и macOS - предварительно установите пакеты для [audioplayer](https://pypi.org/project/audioplayer/))

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

**Важно:** с версии 4.1 Ирины немного поменялся формат результата вызова (для saytxt), 
но теперь поддерживаются мультиформаты через ",".

Например: "none,saywav" - как вызовет озвучку на сервере, так и передаст WAV-файл на клиент. Можно использовать
любые комбинации none,saytxt,saywav

```
baseUrl = "http://127.0.0.1:5003/" 
``` 

Адрес сервера с Ириной

### run_remoteva_cmdline.py

Минимальный вариант клиента для удаленного управления Ириной через командную строку
Не требует vosk, только

```
requests
soundfile
sounddevice
```
В случае, если установлен режим **none** / **saytxt** (без необходимости проигрывать звук на клиенте),
требования сводятся только к
```
requests
```

Может быть адаптирован, чтобы сделать какой-то другой клиент

### run_remoteva_cmdline_min.py

Абсолютно минимальный вариант для удаленного управления Ириной 
через командную строку (около 50 строк кода)

Только на нативных функциях Python, **без установок библиотек**.
Но требует файл **pysimpleurl.py** для GET-запросов. 
Если есть желание заменить на библиотеку requests, 
смотрите пример в run_remoteva_cmdline.py.

Может быть собран с помощью auto-py-to-exe в один файл.


### Телеграм-клиент

Для запуска Телеграм-клиента:
1. Запустите **run_remote_telegrambot.py**
2. Он скажет, что нужно добавить api key для бота. 
Сгенерируйте API-ключ для бота в телеграм-боте @BotFather
и установите его в **options_telegrambot.json** (далее - конфиг).
3. Запустите **run_remote_telegrambot.py**. На любой ввод бот будет говорить о том, что доступ запрещен.
4. Чтобы управлять Ириной, установите в конфиге ```"allowAddAdmins": true```, и перезапустите **run_remote_telegrambot.py**
5. Вам в консоли выдатся 6-значный цифровой ключ. Введите его в чате с ботом, чтобы получить права админа.
6. Как только вы стали админом, вы можете посылать команды боту - они будут перенаправлены Ирине. Например, "погода"
7. После перезапуска админские права сохраняются (chat.id в конфиге).

Для добавления других администраторов - см. пункт 4.

Для удаления всех администраторов сделайте пустым массив в конфиге ```"adminChats": []```

**Добавлена обработка голосовых сообщений**

Для настройки установите параметр voiceMsgProcessor в конфиге. Варианты:
  * `none` - без обработки
  * `play` - проиграть полученное сообщение (на машине, где Телеграм-клиент)
  * `rec_vosk` - (**рекомендуется**) распознать полученное сообщение, а затем выдать 
  предложение - отправить как команду Ирине, или же проиграть в колонках

(Для владельцев Mac/Linux. Обработка голосовых сообщений
осуществляется с помощью ffmpeg, так что необходимо добавить его в пути или в папку. 
На Windows просто запустится местный файл ffmpeg.exe)

### Auto-py-to-exe

Клиент **run_remoteva_vosk.py** можно собрать для в виде автономного EXE-файла через auto-py-to-exe.
Версия получается рабочей

Настройки в auto-py-to-exe.json. 
Потребуется отредактировать опцию vosk, настроив источник на вашу Python-установку 
(чтобы скопировать библиотеку, без неё не заработает)

## Compiled

[Скачать собранную версию run_remoteva_vosk 1.3 в EXE](https://download.janvarev.ru/vairene/run_remoteva_vosk13.rar) (с фиксом для корректного проигрывания wav-файлов без съедания окончаний)

[Скачать собранную версию run_remoteva_vosk 1.2 в EXE](https://download.janvarev.ru/vairene/run_remoteva_vosk12.rar) (для версий Ирины 4.1 и выше)

[Скачать собранную версию 1.1 в EXE](https://download.janvarev.ru/vairene/run_remoteva_vosk11.rar) 


