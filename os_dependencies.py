# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
file:  os_dependencies.py

Purpose:
    Isolates os_dependent code by storing functions and variables appropriate to this OS

Parameters: None (but detects if Linux, MacOS or other

Returns: Paths and functions specific to this OS

Description: Isolates os_dependent code by storing functions and variables appropriate to this OS

Raises: None

Usage: None

Dependencies:

    os.path -- path manipulations
    PySimpleGUI as sg -- GUI functions
    pathlib -- path manipulations
    glob -- file path manipulation

    src.get_linux_camera  -- code for processing lists of cameras on linux
    src.get_mac_camera   -- code for processing lists of cameras on MacOS

Inheritance:    None

Warnings: Isolates os dependent code and variable values.

Testing: TODO: To be determined

Updates:

        Scott McGregor,  modified22-Nov-2021, added header documentation

Notes:  None

TO DO:  None

"""
import os
import PySimpleGUI as sg

# from get_linux_camera import get_linux_cameras_list, linux_capture_scanner_images
# from get_mac_camera import get_mac_cameras_list, mac_capture_scanner_images


__author__ = 'Scott McGregor'

running_os = ""
path_to_ffmpeg = ""
path_to_v4_l2_ctl = ""
path_to_scanner_serial_number_file = ""
path_to_meshconv = ""
sonascan_root_path = ""
path_to_rsync = 'rsync'

if sg.running_linux():
    running_os = "linux"
    sonascan_root_path = "/sonautics/"
    path_to_scanner_serial_number_file = "/sonautics/SonaScan_serial_number"
    path_to_meshconv = "/usr/local/bin/meshconv"
    path_to_meshlab = "/usr/bin/meshlab"
    path_to_rsync = '/usr/bin/rsync'
    path_to_v4_l2_ctl = '/usr/bin/v4l2-ctl'  # path to the v4l2-ctl program
    path_to_ffmpeg = '/usr/bin/ffmpeg'  # path to the ffmpeg program
    sonascan_root_path = "/sonautics/"
    path_to_scanner_serial_number_file = "/sonautics/SonaScan_serial_number"
    # camera_list, usb_map_dict = get_linux_camera_list()
    # get_cameras_list = get_linux_cameras_list  # note this creates a FUNCTION alias
    # capture_scanner_images = linux_capture_scanner_images  # note this creates a FUNCTION alias

elif sg.running_mac():
    running_os = "mac"
    sonascan_root_path = "/sonautics/"
    path_to_scanner_serial_number_file = "/sonautics/SonaScan_serial_number"
    path_to_meshconv = "/sonautics/meshconv-macos-10.10.3/meshconv"
    path_to_meshlab = "/meshlab.app/Contents/MacOS/meshlab"
    path_to_rsync = '/usr/local/bin/rsync'
    path_to_ffmpeg = os.path.abspath('/usr/local/bin/ffmpeg')  # path to the ffmpeg program
    sonascan_root_path = "/sonautics/"
    path_to_scanner_serial_number_file = "/sonautics/SonaScan_serial_number"
    # camera_list, usb_map_dict = get_mac_cameras_list()
    # get_cameras_list = get_mac_cameras_list  # note this creates a FUNCTION alias
    # capture_scanner_images = mac_capture_scanner_images  # note this creates a FUNCTION alias
    path_to_meshlab = '/Applications/meshlab.app/Contents/MacOS/meshlab'
else:  # unsupported OS
    unsupported_os_layout = [
        [sg.Image(filename='../images/ialert.png'),
         sg.Text('This software is running on an unsupported operating system.', font='Raleway 10 bold')],
        [sg.Text('Only MacOS and Linux are supported.  Program will terminate.', font='Raleway 10 bold')],
        [sg.Button('POWER OFF')]
    ]
    unsupported_os_window = sg.Window('Unsupported Operating System', unsupported_os_layout, location=(250, 220),
                                      background_color='#bbbbbb',
                                      titlebar_background_color='orange',
                                      use_custom_titlebar=True,
                                      )
    unsupported_os_event, unsupported_os_values = unsupported_os_window.read()
    exit(-999)

PEM_KEY_FILE = os.path.join(sonascan_root_path, ".ssh/tridi-mpl.pem")


if __name__ == '__main__':  # Use this for Unit testing
    print('running_os=', running_os)
    print('sonascan_root_path=', sonascan_root_path)
    print('path_to_scanner_serial_number_file=', path_to_scanner_serial_number_file)
    print('path_to_rsync=', path_to_rsync)
