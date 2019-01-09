import os
from contextlib import suppress
from functools import lru_cache

import grpc
import vlviapb_pb2 as vl
import vlviapb_pb2_grpc as vl_grpc
import speech_recognition as sr


DEBUG = True

HELP = ('\nPlease enter one of the following commands: '
        '\n\tq/quit -> to quit program'
        '\n\th/help -> to print help'
        '\n\tl/listen -> to listen for speech command')


@lru_cache(maxsize=2**16)
def levenshtein_dist(a, b):
    if a == '':
        return len(b)
    elif b == '':
        return len(a)
    else:
        cost = 0 if a[-1] == b[-1] else 1
       
        return min(levenshtein_dist(a[:-1], b) + 1, 
                   levenshtein_dist(a, b[:-1]) + 1, 
                   levenshtein_dist(a[:-1], b[:-1]) + cost)


def recognize(voice_lab, vl_metadata, audio_data):
    wav_data = audio_data.get_wav_data(convert_rate=16000, convert_width=2)

    text = []
    stream = iter([vl.AudioFrames(frames=wav_data)])
    for update in voice_lab.RecognizeStream(stream, metadata=vl_metadata):
        shift = update.shift
        words = update.words

        words_to_rm = len(words) - shift
        text[len(text) - words_to_rm:] = words

        if DEBUG:
            print(shift, words, text)

    return text


def listen(vl_stub, vl_metadata, mic, recognizer):
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

        print('LISTEN')
        audio = recognizer.listen(source)
        print('TRANSLATE')
        text = recognize(vl_stub, vl_metadata, audio)
        print(text)


def loop_forever(vl_stub, vl_metadata, mic, recognizer):
    command = input('\nEnter command: ')
    if command in ('q', 'quit'):
        return

    if command in ('l', 'listen'):
        listen(vl_stub, vl_metadata, mic, recognizer)
    elif command in ('h', 'help'):
        print(HELP)
    else:
        print('\nUnrecognized command: {}'.format(command), HELP)

    loop_forever(vl_stub, vl_metadata, mic, recognizer)


def main():
    password = os.environ.get('VOICE_LAB_PASSWORD')
    if not password:
        print('Missing password required to connect to Voice Lab service.\n'
              'Please provider by setting environment variable "VOICE_LAB_PASSWORD"')
        exit(1)

    channel = grpc.insecure_channel('demo.voicelab.pl:7722')
    vl_stub = vl_grpc.VLVIAStub(channel)
    vl_metadata = [
        ('pid', '8131'),
        ('password', password),
        ('contenttype', 'audio/L16;rate=16000')
    ]

    microphone = sr.Microphone()
    recognizer = sr.Recognizer()

    loop_forever(vl_stub, vl_metadata, microphone, recognizer)


if __name__ == '__main__':
    main()
