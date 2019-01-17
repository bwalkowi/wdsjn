import os
from functools import partial

import grpc
import vlviapb_pb2 as vl
import vlviapb_pb2_grpc as vl_grpc
import speech_recognition as sr

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, FloatContainer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Button, Box, TextArea, Label, Frame
from prompt_toolkit.eventloop import ensure_future, From

from view_utils import show_dialog, ChoiceDialog, MessageDialog


LOGO = r"""
                                                                                                                  []
  _    _  ____  __  __ ______             _____ _____ _____  _____ _______       _   _ _______          /^~^~^~^~^~^~\ 
 | |  | |/ __ \|  \/  |  ____|     /\    / ____/ ____|_   _|/ ____|__   __|/\   | \ | |__   __|        /^ ^ ^  ^ ^ ^ ^\
 | |__| | |  | | \  / | |__       /  \  | (___| (___   | | | (___    | |  /  \  |  \| |  | |          /_^_^_^^_^_^_^_^_\
 |  __  | |  | | |\/| |  __|     / /\ \  \___ \\___ \  | |  \___ \   | | / /\ \ | . ` |  | |           |        .--.  |   
 | |  | | |__| | |  | | |____   / ____ \ ____) |___) |_| |_ ____) |  | |/ ____ \| |\  |  | |       ^^^^|  [}{]  |[]|  |^^^^^ 
 |_|  |_|\____/|_|  |_|______| /_/    \_\_____/_____/|_____|_____/   |_/_/    \_\_| \_|  |_|         88|________|__|__|888 
                                                                                                                ====
"""

HELP = "Welcome to HOME ASSISTANT"


def help_handler():
    def coroutine():
        dialog = MessageDialog(HELP, 'HELP')
        yield From(show_dialog(dialog))

    ensure_future(coroutine())


def recognize(voice_lab, vl_metadata, audio_data):
    wav_data = audio_data.get_wav_data(convert_rate=16000, convert_width=2)

    text = []
    stream = iter([vl.AudioFrames(frames=wav_data)])
    for update in voice_lab.RecognizeStream(stream, metadata=vl_metadata):
        shift = update.shift
        words = update.words

        words_to_rm = len(words) - shift
        text[len(text) - words_to_rm:] = words

    return text


def listen_handler(vl_stub, vl_metadata, mic, recognizer, text_area):

    def handler():

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

            #print('LISTEN')
            audio = recognizer.listen(source)
            #print('TRANSLATE')
            text = recognize(vl_stub, vl_metadata, audio)
            text_area.text = ' '.join(text)

        #def coroutine():
            #dialog = ChoiceDialog(['zxc', 'asd'], 'qwe')
            #choice = yield From(show_dialog(dialog))
            #text_area.text = str(choice)

        #ensure_future(coroutine())

    return handler


def create_app(listen_handler):

    # components
    logo = Label(text=LOGO)
    text_area = TextArea(text='', read_only=True, scrollbar=True)

    listen_btn = Button('Listen', handler=listen_handler(text_area=text_area))
    help_btn = Button('Help', handler=help_handler)
    exit_btn = Button('Exit', handler=lambda: get_app().exit())

    buttons = HSplit(children=[Label(text='     MENU'), 
                               Frame(listen_btn), 
                               Frame(help_btn),
                               Frame(exit_btn)],
                     style='bg:#00aa00 #000000')

    # root container
    root_container = FloatContainer(HSplit([
        Box(body=VSplit([buttons, logo], padding=12),
            padding=0,
            style='bg:#888800 #000000'),
        text_area,
    ]), floats=[])

    # key bindings
    bindings = KeyBindings()
    bindings.add('tab')(focus_next)
    bindings.add('s-tab')(focus_previous)

    @bindings.add('c-c')
    @bindings.add('q')
    def _(event):
        event.app.exit()

    # application
    application = Application(layout=Layout(root_container,
                                            focused_element=listen_btn),
                              key_bindings=bindings,
                              enable_page_navigation_bindings=True,
                              mouse_support=True,
                              full_screen=True)
    return application


def main():
    password = os.environ.get('VL_PASSWD')
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

    app = create_app(partial(listen_handler, vl_stub, vl_metadata, 
                             sr.Microphone(), sr.Recognizer()))
    app.run()


if __name__ == '__main__':
    main()
