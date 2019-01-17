from prompt_toolkit.application.current import get_app
from prompt_toolkit.eventloop import Future, Return
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.widgets import Button, Label, Dialog


class ChoiceDialog:
    def __init__(self, choices, title=''):
        self.future = future = Future()

        text = 'Did you mean one of the following?'
        buttons = []

        for no, cmd in enumerate(choices):
            text += '\n{no}. {cmd}'.format(no=no, cmd=cmd)
            buttons.append(Button(text=str(no), 
                                  handler=lambda i=no: future.set_result(i)))

        buttons.append(Button(text='none', 
                              handler=lambda: future.set_result(None)))

        self.dialog = Dialog(title=title,
                             body=HSplit([
                                 Label(text=text),
                             ]),
                             buttons=buttons,
                             width=D(preferred=80),
                             modal=True)

    def __pt_container__(self):
        return self.dialog


class MessageDialog:
    def __init__(self, text, title):
        self.future = future = Future()

        ok_btn = Button(text='OK', handler=lambda: future.set_result(None))

        self.dialog = Dialog(title=title,
                             body=HSplit([
                                 Label(text=text),
                             ]),
                             buttons=[ok_btn],
                             width=D(preferred=80),
                             modal=True)

    def __pt_container__(self):
        return self.dialog


def show_dialog(dialog):
    "Coroutine."
    app = get_app()
    container = app.layout.container

    float_ = Float(content=dialog)
    container.floats.insert(0, float_)

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = yield dialog.future
    app.layout.focus(focused_before)

    if float_ in container.floats:
        container.floats.remove(float_)

    raise Return(result)
