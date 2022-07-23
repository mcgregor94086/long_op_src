You set both main window and message window with same theme, of course, with the same background.
There'll be no window manager when you set use_custom_titlebar=True in sg.Window, and there will be no titlebar and border of window, so that's why the background of main window and that of message window mixed together.

There're some ways for it,

Create your message window with use_custom_titlebar=False, or
Use different theme for your message window by call sg.theme, especially for different 'BACKGROUND', or
Using option background_color in sg.Window may not work well for background color of some elements not also changed.
Example Code here, using different themes for different windows and just 'BACKGROUND' revised from '#dddddd' to '#bbbbbb' in Sonautics2.

import PySimpleGUI as sg

def popup():
    sg.theme("Sonautics2")
    layout = [
        [sg.Image(data=sg.EMOJI_BASE64_HAPPY_LAUGH), sg.Text("Hello !")],
        [sg.Button("OK")],
    ]
    sg.Window('Alarm', layout, background_color='#bbbbbb', use_custom_titlebar=True).read(close=True)
    sg.theme("Sonautics")

sg.theme("Sonautics")
sg.set_options(font=("Courier New", 16))

layout =[
    [sg.Button("Say Hello")],
]
window = sg.Window("Title", layout, size=(500, 500), use_custom_titlebar=True)

while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Say Hello":
        popup()

window.close()