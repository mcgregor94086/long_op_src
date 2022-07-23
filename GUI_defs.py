# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
file: GUI_defs.py

Purpose:
    Defines a number of variables and constants used by the GUI user interface.
    Some which may be OS dependent.  Some are complex object structures that define
    "layouts" for controlling the appearance of windows and popups.
    This file is imported into other python files that interact with the GUI

Parameters: None

Returns: None

    importing this file creates the predefined variables, constants and layouts used to control the GUI

Description:

    Defines a number of variables and constants used by the GUI user interface.
    Some which may be OS dependent.  Some are complex object structures that define
    "layouts" for controlling the appearance of windows and popups.
    This file is imported into other python files that interact with the GUI

Raises: None

Usage:

    import GUI_defs.py

Dependencies:

    os  -- library used to manipulate file paths
    PySimpleGUI as sg -- Library used to control GUI
    datetime -- Library used to process datetime stamps.
    convert_to_bytes -- function to convert image files to byte format
    sonascan_root_path -- path to parent directory of where sonascan files are
    get_serial_number -- function to retrieve the scanner serial number (scanner_id)

Inheritance:    None

Testing:  TODO: To be determined

Warnings: None

Updates:

        Scott McGregor,  modified 22-Nov-2021, Added check on how many cameras respond to detect USB not connected

Notes:  None

TO DO:   None
"""

__author__ = 'Scott McGregor'

current_release_id = 'v B.0.1.220629A'

import logging
import os
from datetime import datetime

import PySimpleGUI as sg

from get_scanner_id import get_scanner_id
from image_processing import convert_to_bytes
from sonascan_file_paths import sonautics_root_dir_path

# from get_serial_number import get_serial_number
# from image_processing import convert_to_bytes

# First make dictionaries with the required keys for defining a Sonautics GUI "style"
# Use only colors in the format of #RRGGBB
Sonautics = {'BACKGROUND': '#dddddd',
             'TEXT': '#000000',
             'INPUT': '#ffffff',
             'TEXT_INPUT': '#000000',
             'SCROLL': '#505F69',
             'BUTTON': ('#000000', 'orange'),
             'PROGRESS': ('#505F69', 'orange'),
             'BORDER': 1,
             'SLIDER_DEPTH': 0,
             'PROGRESS_DEPTH': 0,
             }

Sonautics2 = {'BACKGROUND': '#bbbbbb',          # The only difference here
              'TEXT': '#000000',
              'INPUT': '#ffffff',
              'TEXT_INPUT': '#000000',
              'SCROLL': '#505F69',
              'BUTTON': ('#000000', 'orange'),
              'PROGRESS': ('#505F69', 'orange'),
              'BORDER': 1,
              'SLIDER_DEPTH': 0,
              'PROGRESS_DEPTH': 0,
              }

# Add our dictionaries to the PySimpleGUI themes
sg.theme_add_new('Sonautics',  Sonautics)  # add this style so it can be used by GUI
sg.theme_add_new('Sonautics2', Sonautics2)  # add this style so it can be used by GUI

sg.theme("Sonautics")
sg.set_options(font=("Raleway", 10))
logging.info(sg)  # save this info for debugging errors
logging.info(sg.version)  # save this info for debugging errors
sg.theme('Sonautics')
screen_width, screen_height = sg.Window.get_screen_size()
logging.info(f"screen width = {screen_width}, screen height = {screen_height}")  # save this info for debugging

# this is a list of predefined file paths and images used by GUI
# short_scan_id, full_scan_id = get_new_scan_id()
scan_start_time = datetime.now()
dt_string = scan_start_time.strftime("%d-%b-%Y %H:%M:%S")
images_dir = os.path.join(sonautics_root_dir_path, "images")
small_logo = os.path.join(images_dir, "Sonautics_Logo_2019_Color_150x63.png")
scan_button = os.path.join(images_dir, "scan-button-small-reg.png")  # sonascan-scan-button.png
disabled_scan_button = os.path.join(images_dir, "scan-button-small-disabled.png")
ialert = os.path.join(images_dir, "ialert.png")
icamera = os.path.join(images_dir, "icamera.png")
igear = os.path.join(images_dir, "igear.png")
iquest = os.path.join(images_dir, "iquest.png")
iquit = os.path.join(images_dir, "iquit.png")
iupload = os.path.join(images_dir, "iupload.png")
iwifi_bad = os.path.join(images_dir, "iwifi-bad,png")
iwifi_good = os.path.join(images_dir, "iwifi-good.png")
iDavid = os.path.join(images_dir, "David.png")
scanner_id_file_path = os.path.join(sonautics_root_dir_path, 'scanner_id.txt')
scanner_id, scanner_dir = get_scanner_id(sonautics_root_dir_path, scanner_id_file_path)
data_dir = os.path.join(sonautics_root_dir_path, "data")
scans_dir = os.path.join(data_dir, "scans")
short_scan_id = datetime.today().strftime('%Y%m%d%H%M%S')
scan_dir = os.path.join(scanner_dir, short_scan_id)
full_scan_id = os.path.join(scanner_id, short_scan_id)
thumbnail = convert_to_bytes(os.path.join(images_dir, "status-ready.png"))

# initial values, variables subject to change:
number_of_scanner_cameras = 18
from_email = "scott@sonautics.com"
to_email = "scott@sonautics.com"
consumer_name = "Happy Consumer"
consumer_id = "consumer@sonautics.com"
order_details = "No order details"
demo_mode = "image_only"


# LAYOUTS FOR MAIN WINDOW ******************************************************************************************
# Column layout (used in Main Window layout)
col1 = [
    [sg.Text(
        'Initializing...                                                                                                       ',
        font=('Raleway', 16, 'bold'), text_color='#fb9004', justification='left',
        key='_ACTION_STATUS_LINE_1_')],
    [sg.Text(
        'Please wait.                                                                                         ',
        font=('Raleway', 14), key='_ACTION_STATUS_LINE_2_')],
    [sg.Image(filename=icamera, size=(32, 32), visible=True),
     sg.ProgressBar(100, orientation='horizontal', bar_color=('#fb9004', "#aaaaaa"),
                    key="_PROGRESS_BAR_", size=(65, 10))],
    [sg.Image(filename=iupload, size=(32, 32), visible=True),
     sg.ProgressBar(100, orientation='horizontal', bar_color=('#fb9004', "#aaaaaa"),
                    key="_UPLOADING_PROGRESS_BAR_", size=(65, 10))],
    [sg.Image(filename=iDavid, size=(32, 32), visible=True),
     sg.ProgressBar(100, orientation='horizontal', bar_color=('#fb9004', "#aaaaaa"),
                    key="_MODELING_PROGRESS_BAR_", size=(65, 10))],
    # [sg.Text('')],  # spacer line
    [sg.Text(
        '                                                                                                            ' +
        '                                                                                                            ',
        font=('Raleway', 10, 'italic'), key='_ACTION_STATUS_LINE_3_')],
    # [sg.Text('')],  # spacer line
    # LINE 14: CALCULATED SCAN SPECIFIC DATA
    [
        sg.Text(dt_string, font=('Raleway', 10),  key='_DATE_', visible=False),
        sg.Text('Scanner:', font=('Raleway', 10, 'bold'), justification='left'),
        sg.Text(scanner_id, font=('Raleway', 10, 'italic'),  key='_SCANNER_ID_'),
        sg.Text('Scan ID:', font=('Raleway', 10, 'bold'), justification='left'),
        sg.Text(full_scan_id, font=('Raleway', 10, 'italic'),  key='_SCAN_ID_'),
    ]
]


# Main window layout
# current_release_id = os.path.basename(os.path.dirname(os.path.dirname(__file__))).split('_')[1]
# print("current_release_id=", current_release_id)

# uploads_waiting = 0
# uploads_waiting = len(os.listdir(scanner_dir))

layout = [

    # LINE 1: HEADING
    [
        sg.Image(filename=small_logo, size=(300, 126)),
        sg.Text('SonaScan', font=('Raleway', 32, 'bold'), text_color='#fb9004', size=(9, 1)),
        # justification='center',
        # sg.Text(number_of_scanner_cameras, font=('Raleway', 15), visible=True, key='_AVAILABLE_CAMERAS_'),
        # sg.Image(filename=icamera, size=(32, 32), visible=True, enable_events=True, key='_CAMERA_ICON_'),
        # sg.Text(uploads_waiting), font=('Raleway', 15), visible=False,  key='_UPLOADS_NUMBER_'),
        # sg.Image(filename=iupload, size=(32, 32), visible=False, enable_events=True, key='_UPLOADS_ICON_'),
        sg.Image(filename=iwifi_good, size=(32, 32), visible=True, enable_events=True, key='_WIFI_ICON_'),
        sg.Image(filename=igear, size=(32, 32), visible=True, enable_events=True, key='_SETTINGS_ICON_'),
        sg.Image(filename=iquest, size=(32, 32), visible=True, enable_events=True, key='_INFO_ICON_'),
        # sg.Image(filename=iquit, size=(32, 32), visible=True, enable_events=True, key='Exit'),
        sg.Text(current_release_id, font=('Raleway', 8), visible=True, key='_RELEASE_ID_'),
    ],

    # INVISIBLE LINE 3: WHO IS SENDING THIS SCAN?
    [
        sg.InputText(from_email, font=('Raleway', 7), size=(25, 1), key='_SENDER_', visible=False)
    ],

    # INVISIBLE LINE 4: WHO WILL THIS SCAN BE SENT TO FOR CAD AND MANUFACTURING STEPS
    [
        sg.InputText(to_email, font=('Raleway', 7, "italic"), size=(25, 1), key='_RECIPIENT_', visible=False)
    ],

    # LINE 5: CONSUMER NAME FOR IMPRESSION  BEING SCANNED (FOR EARS ON FILE RETRIEVAL)
    [
        sg.Text("Consumer's Name:", size=(15, 1), font=('Raleway', 14, 'bold'), justification='right'),
        sg.InputText(consumer_name, font=('Raleway', 14, "italic"), size=(50, 1), key='_CONSUMER_NAME_')
    ],

    # LINE 6: CONSUMER EMAIL FOR IMPRESSION  BEING SCANNED (FOR EARS ON FILE RETRIEVAL)
    [
        sg.Text("Consumer's Email:", size=(15, 1), font=('Raleway', 14, 'bold'), justification='right'),
        sg.InputText(consumer_id, font=('Raleway', 14, "italic"), size=(50, 1), key='_CONSUMER_ID_')
    ],

    # LINE 7: WHAT ADDITIONAL ORDER DETAILS DOES SENDER WANT TO PROVIDE TO RECIPIENT
    [
        sg.Text('Order Details:', size=(15, 1), font=('Raleway', 14, 'bold'), justification='right'),
        sg.Multiline(order_details, font=('Raleway', 14, "italic"), size=(50, 1), key='_ORDER_DETAILS_')
    ],

    # LINE 8: vertical spacer
    # [sg.Text('', font=('Raleway', 14, 'bold'), text_color='#000000')],

    # LINE 10: THE BIG SCAN BUTTON
    [
        sg.Text('', size=(32, 2), font=('Raleway', 7, 'bold')),
        sg.Text('', size=(16, 2), font=('Raleway', 7, 'bold')),
        sg.Button(button_color=('#dddddd', '#dddddd'), mouseover_colors=('#dddddd', '#dddddd'), border_width=0,
                  image_filename=disabled_scan_button, image_size=(300, 86),
                  enable_events=True, key='_SCAN_BUTTON_', focus=False),
        # sg.Button('SCAN', button_color=('#ffffff' ,'#000000'), font=('Raleway', 19), image_filename=scan_button,
        #           image_size=(300, 86))
    ],

    # LINE 13: IMAGE AND PROGRESS
    [
        sg.Text('', size=(3, 1), font=('Raleway', 14, 'bold')),
        sg.Image(data=thumbnail, visible=True, size=(96, 54), key='_IMAGE_ELEMENT_'),
        sg.Column(col1)
    ],


    # LINE 18: Info bar
    # [sg.StatusBar
    #    ('                                                                                                       ',
    #         font=('Raleway', 9), size=(75,1), key='_ACTION_STATUS_BAR_')],
]
# END OF LAYOUT FOR MAIN WINDOW ************************************************************************************

# LAYOUT FOR SETTINGS WINDOW:
settings_layout = [
     [
      #   sg.Image(filename=small_logo, size=(300, 126)),
      sg.Text('Settings', font=('Raleway', 20, 'bold'), text_color='#fb9004', size=(9, 1)),
     ],
     [sg.Text("Demo Mode:", size=(16, 1), font=('Raleway', 15, 'bold'))],
     [
      #   sg.Checkbox('Simulate image captures', default=False),
      sg.Checkbox('Simulate uploading', default=False),
      sg.Checkbox('Simulate modeling',  default=False),
      ],
     [sg.Text("Local Display Modes:", size=(16, 1), font=('Raleway', 12, 'bold'), justification='left')],
     [sg.Checkbox('Show images html', default=True),
      sg.Checkbox('Show 3D model', default=True)],
     [sg.Submit(), sg.Cancel()],
]

# Certain GUI options are OS dependent, this hides them.

if sg.running_linux():
    window = sg.Window('SonaScan', layout, font=('Raleway', 40),
                       location=(0, -5), size=(1024, 600),
                       no_titlebar=False,
                       use_default_focus=True,
                       disable_close=True,
                       grab_anywhere=True,
                       disable_minimize=False,
                       finalize=True,
                       )
    # window.Maximize()
elif sg.running_mac():
    window = sg.Window('SonaScan', layout, font=('Raleway', 40), ttk_theme="default",
                       location=(0, 0), size=(1024, 600),
                       use_ttk_buttons=True,
                       no_titlebar=False,
                       use_default_focus=False,
                       disable_close=False,
                       grab_anywhere=True,
                       disable_minimize=False,
                       finalize=True,
                       )
    # window.Maximize()
else:
    window = None
    quit("This program only runs on Linux and MacOS")
