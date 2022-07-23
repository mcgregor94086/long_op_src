There're three places to set the focus box.

Option focus of sg.Button: if True, initial focus will be put on this button, default value is False.
Option use_default_focus of sg.Window: If True will use the default focus algorithm to set the focus to the "Correct" element
Method block_focus(block=True) of element: If True, this element will not be given focus by using the keyboard (TAB or ctrl-TAB) to go from one element to another.
To remove focus box in sg.Button,

Set option focus=False in sg.Button, it is default
Set option use_default_focus=False in sg.Window
Call method block_focus() of element sg.Button after window finalized.
Demo code for it,

import PySimpleGUI as sg

sg.theme("DarkBlue3")
sg.set_options(font=("Courier New", 11))

layout = [
    [sg.Input("Image Button")],
    [sg.Input()],
    [sg.Button(
        "SCAN",
        button_color=('#dddddd', '#dddddd'),
        mouseover_colors=('#ffffff', '#ffffff'),
        border_width=0,
        image_data=sg.EMOJI_BASE64_HAPPY_LAUGH,
        image_size=(180, 80),
        enable_events=True,
        focus=False,            # 1. Not necessary for default option value
        key='_SCAN_BUTTON_',
     ),
    ]
]

# 2. Add option `use_default_focus=False`
window = sg.Window("Title", layout, use_default_focus=False, finalize=True)

# 3. Call method `block_focus()
window['_SCAN_BUTTON_'].block_focus()

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

window.close()