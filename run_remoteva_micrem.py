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
                    # or mix of the params, splitted by , = "none,saytxt" as example
ttsFormatList = ttsFormat.split(",")
baseUrl = saved_options["baseUrl"] # server with Irene WEB api

from urllib.parse import urlparse
urlparsed = urlparse(baseUrl)

mic_blocked = False

import json
import os
import sys
import asyncio
import websockets
import logging
import sounddevice as sd
import argparse

# ------------------- vosk ------------------
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

async def run_test():

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 4000, device=args.device, dtype='int16',
                           channels=1, callback=callback) as device:
        conn_url = str(args.uri) + "/wsmic_"+str(args.samplerate)+"_none"
        # conn_url = str(args.uri) + "/wsmic"
        print('WEB SOCKET conn URL:',conn_url)
        async with websockets.connect(conn_url) as websocket:
            # await websocket.send('{ "config" : { "sample_rate" : %d } }' % (device.samplerate))

            while True: # just send data from mic to webapi websocket
                data = await audio_queue.get()
                await websocket.send(data)
                #print (await websocket.recv())
                res = await websocket.recv()


            await websocket.send('{"eof" : 1}')
            #print (await websocket.recv())

async def main():

    global args
    global loop
    global audio_queue

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(description="ASR Server",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     parents=[parser])
    parser.add_argument('-u', '--uri', type=str, metavar='URL',
                        # by default connect to WEBAPI server with PORT+1
                        help='Server URL', default='ws://{0}:{1}'.format(urlparsed.hostname,urlparsed.port))
    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')
    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate', default=22050)
    args = parser.parse_args(remaining)
    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()

    logging.basicConfig(level=logging.INFO)
    print("Remote Irene (VOSK EMBEDDED REMOTE recognizer) v{0} started! ttsFormat={1}, baseUrl={2}, speechRecognizerWebsocketUrl={3}".format(version,ttsFormat,baseUrl,args.uri))

    await run_test()

if __name__ == '__main__':
    asyncio.run(main())


