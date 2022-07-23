__author__ = ''

# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
import logging
import webbrowser

from GUI_defs import window
from scandir_index_maker import scandir_index_maker
from show_images import show_images
from upload_images import upload_images

"""
function:  do_local_demo(window)

Purpose:
    When we can't access the sona_server we can provide a way to DEMO the program using stored images

Parameters: 

    window (window_handle): -- the GUI window object to display the DEMO on

Returns: None

Description: 

    When we can't access the sona_server we can provide a way to DEMO the program using stored images

Raises: None


Usage: do_local_demo(window)

Dependencies:  Any libraries, devices, etc. that must be present.

        src.GUI_defs -- library of GUI definitions

Inheritance:    None

Testing: TODO: To be determined

Warnings: None

Updates: 

        Scott McGregor,  modified 22-Nov-2021, Added header documentation

Notes:  None

TO DO:   None

"""


import os

from time import sleep
import glob

import PySimpleGUI as sg

from image_processing import convert_to_bytes
from sonascan_file_paths import demo_dir, demo_stl


def update_window_on_scan(scan_image_name, full_scan_id, image_counter, max_cameras, main_window):
    logging.debug(f'\nENTERING: update_window_on_scan({scan_image_name}, {full_scan_id}, {image_counter}, {max_cameras}, {main_window})')

    image_name = os.path.basename(scan_image_name)
    main_window['_ACTION_STATUS_LINE_3_'].update(full_scan_id + "/" + image_name + " new scan image.")
    main_window['_ACTION_STATUS_LINE_2_'].update(scan_image_name)
    main_window['_PROGRESS_BAR_'].update(100 * image_counter / max_cameras)
    thumbnail = convert_to_bytes(scan_image_name, [96, 54])
    main_window['_IMAGE_ELEMENT_'].update(data=thumbnail)
    # window['_IMAGE_ELEMENT_'].update(data=camera_file_path)
    main_window.Refresh()
    image_counter = image_counter + 1

    logging.debug(f'EXITING: update_window_on_scan() RETURNS: {image_counter}\n')
    logging.debug(
        f'EXITING: update_window_on_scan({scan_image_name}, {full_scan_id}, {image_counter}, {max_cameras}, {main_window})\n')

    return image_counter


def demo(the_scan_data):
    print(f'\n\tENTERING: demo({the_scan_data})')

    main_window = the_scan_data['window']
    # Do this if there are not enough cameras responding:
    full_scan_id = "DEMO"
    the_scan_data['scanner_id'] = 'DEMO'
    the_scan_data['long_scan_id'] = 'DEMO'
    the_scan_data['scan_dir'] = demo_dir
    the_scan_data['scan_id'] = 'DEMO'
    demo_images_list = glob.glob(demo_dir+"/*.jpg")
    max_cameras = len(demo_images_list)
    # print(f'\t{max_cameras}, {demo_images_list}')
    sorted_images_list = sorted(demo_images_list)
    # print(f'\t{max_cameras}, {sorted_images_list}')
    image_counter = 0
    main_window['_ACTION_STATUS_LINE_1_'].update("SCANNING (DEMO MODE)")
    i = 1
    for image_file in sorted_images_list:
        update_window_on_scan(image_file, full_scan_id, image_counter, max_cameras, window)
        main_window['_PROGRESS_BAR_'].update(100 * i / 18)
        sleep(.5)  # delay to simulate actual camera capture time per image
        i = i + 1
        image_counter = image_counter + 1
    sleep(1)
    main_window['_ACTION_STATUS_LINE_1_'].update("SCANNING COMPLETE (DEMO MODE)")
    main_window.Refresh()
    sleep(1)

    # No need to simulate,  We will actually upload it!
    the_scan_data['images_list'] = sorted_images_list
    the_scan_data['scanner_id'] = 'DEMO'
    the_scan_data['long_scan_id'] = 'DEMO'
    the_scan_data['scan_dir'] = demo_dir
    the_scan_data['scan_id'] = 'DEMO'
    print(f'\tCALLING scandir_index_maker()')
    scandir_index_maker(the_scan_data)
    print(f'\tRETURNING FROM scandir_index_maker()')
    # print(f'\t(Demo) scan_dir = {the_scan_data["scan_dir"]}')
    # print(f'\t{the_scan_data}')

    scan_dir = the_scan_data['scan_dir']
    # print(f'\tshow_images(): scan_dir = {scan_dir}')
    # print(f'\tshow_images(): show_images() = {the_scan_data}' )

    if the_scan_data['Show images html']:
        # print(f'\tShow images html = {the_scan_data["scan_dir"]}')
        # print(f'\t{the_scan_data}')

        print(f'\n\t\tENTERING show_images({the_scan_data})')

        url_to_show = 'file://' + os.path.join(os.path.realpath(scan_dir), 'index.html')
        # print(f'\t\tshow_images(): scan_dir = {os.path.realpath(scan_dir)}')
        webbrowser.open(url_to_show)

        print(f'\t\tEXITING show_images({the_scan_data})\n')

        # window.perform_long_operation(lambda: show_images(the_scan_data), '-END SHOW IMAGES-')

    print(f'\tsimulate_unloading_flag = {the_scan_data["Simulate uploading"]}')

    if not the_scan_data['Simulate uploading']:

        # window.write_event_value('_UPLOAD_IMAGES_', the_scan_data)
        print(f'\n\tCALLING upload_images()')
        upload_images(the_scan_data)
        print(f'\tRETURNING FROM upload_images()\n')

    else:

        # If we get here, we aren't going to actually upload the DEMO files, we'll just simulate it.
        main_window['_ACTION_STATUS_LINE_1_'].update("UPLOADING TO SERVER (DEMO MODE)")
        main_window['_ACTION_STATUS_LINE_3_'].update("")
        image_counter = 0
        i = 1
        for image_file in sorted_images_list:
            # scan_image_name = os.path.basename(image_file)
            update_window_on_scan(image_file, full_scan_id, image_counter, max_cameras, window)
            main_window['_PROGRESS_BAR_'].update(100 * i / 18)
            i = i + 1
            sleep(.5)  # delay to simulate file upload time

        sleep(1)
        main_window['_ACTION_STATUS_LINE_1_'].update("UPLOADING COMPLETE (DEMO MODE)")
        main_window.Refresh()
        sleep(1)

    if not the_scan_data['Simulate modeling']:

        print(f'\tEXITING 2: demo() RETURNS: {the_scan_data})\n')
        return the_scan_data

    # If we get here, we aren't going to actually process the DEMO files, we'll just simulate it.
    main_window['_ACTION_STATUS_LINE_1_'].update("PROCESSING MODEL (DEMO MODE)")
    main_window.Refresh()

    for i in range(1, 11):
        main_window['_PROGRESS_BAR_'].update(100 * i / 10)
        sleep(.5)

    # Display a message that model is complete
    sleep(1)
    main_window['_ACTION_STATUS_LINE_1_'].update("PROCESSING COMPLETE (DEMO MODE)")
    main_window.Refresh()
    sleep(1)

    if not the_scan_data['Show 3D model']:
        return the_scan_data
    if sg.running_mac():
        sg.execute_command_subprocess('/Applications/meshlab.app/Contents/MacOS/meshlab', demo_stl,
                                      wait=False, cwd=None, pipe_output=False)
    else:  # sg.running_linux:
        sg.execute_command_subprocess('/usr/bin/meshlab', demo_stl,
                                      wait=False, cwd=None, pipe_output=False)
        sg.execute_command_subprocess('wmctrl', '-r', 'MeshLab v1.3', '-e', '1', '50', '50', '500', '500',
                                      wait=False, cwd=None, pipe_output=False)
    print("\tlaunched meshlab to view 3D model for photoscene:", "photoscene-DEMO")

    print(f'\tEXITING 3: demo() RETURNS: {the_scan_data})\n')
    return the_scan_data


if __name__ == '__main__':  # use for unit testing
    window_x = sg.Window("")
    scan_data = {'window': window_x}
    new_scan_data = demo(scan_data)
