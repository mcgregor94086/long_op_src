# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function: convert_to_bytes(file_or_bytes, resize=None)

Purpose:
    Will convert an image into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter

Parameters:

    file_or_bytes (Union[str, bytes]): either a string filename or a bytes base64 image object
    resize: (Tuple[int, int] or None):  optional new size

Returns:

    return (bytes): a byte-string object

Description:

    Will convert an image into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter

Raises:

    None

Usage: How this class, method, or function is accessed / called.

   return = convert_to_bytes(file_or_bytes, resize=None)


Dependencies:  Any libraries, devices, etc. that must be present.

    import PIL.Image -- used to process Images including resizing
    import io -- used to read bytes from files
    import base64 -- used to create base64 binary strings

Inheritance:    For classes, list what it inherits from here

Testing: TODO: To be determined

Warnings: Anything that might be dangerous, or a source of bugs.

    This function was developed by the creator of PySimpleGUI and is taken from the PySimpleGUI sample code on GitHub

Updates: Document who modified the function, when, why and how.

    Scott McGregor,  modified 22-Nov-2021, added documentation

Notes:

    This function was developed by the creator of PySimpleGUI and is taken from the PySimpleGUI sample code on GitHub

"""

import PIL.Image
import io
import base64

from PIL import Image, ImageTk, ImageSequence
import PySimpleGUI as sg

# This code derived from example at:
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-convert_to_bytes-function-pil-image-viewer

'''
Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
Turns into  PNG format in the process so that can be displayed by tkinter
:param file_or_bytes: either a string filename or a bytes base64 image object
:type file_or_bytes:  (Union[str, bytes])
:param resize:  optional new size
:type resize: (Tuple[int, int] or None)
:return: (bytes) a byte-string object
:rtype: (bytes)
'''


def convert_to_bytes(file_or_bytes, resize=None):
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            data_bytes_io = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(data_bytes_io)
            print(e)
    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()


"""
    Demo_Animated_GIFs_Using_PIL.py
    from: https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Animated_GIFs_Using_PIL.py

    You'll find other animated GIF playback demos for PySimpleGUI that use the tkinter built-in GIF parser.
    That is how the built-in PySimpleGUI Image.update_animation is used.

    If you want to do the GIF file parsing yourself using PIL and update your Image element yourself, then
    this is one possible technique.
    This particular demo will loop playing the GIF file over and over.  To not loop, remove the while True statement.
    Copyright 2020 PySimpleGUI.org
"""


def show_animated_gif():
    gif_filename = r'ExampleGIF.gif'

    layout = [[sg.Text('Happy Thursday!', background_color='#A37A3B', text_color='#FFF000',
                       justification='c', key='-T-', font=("Bodoni MT", 40))], [sg.Image(key='-IMAGE-')]]

    window = sg.Window('Window Title', layout, element_justification='c', margins=(0, 0), element_padding=(0, 0),
                       finalize=True)

    window['-T-'].expand(True, True, True)  # Make the Text element expand to take up all available space

    inter_frame_duration = Image.open(gif_filename).info['duration']  # get how long to delay between frames

    while True:
        for frame in ImageSequence.Iterator(Image.open(gif_filename)):
            event, values = window.read(timeout=inter_frame_duration)
            if event == sg.WIN_CLOSED:
                exit(0)
            window['-IMAGE-'].update(data=ImageTk.PhotoImage(frame))


if __name__ == '__main__':
    my_file_or_bytes = ''
    convert_to_bytes(my_file_or_bytes, resize=None)
    show_animated_gif()
