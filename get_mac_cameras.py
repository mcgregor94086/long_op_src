# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function: get_mac_camera_list()

Purpose:    Gets the list of camera device addresses when connected to a Linux processor

Parameters: None

Returns:    images_list: list of camera device addresses to request images from.

Description:    Gets the list of camera device addresses when connected to a MacOS processor

Raises: None

Usage: images_list (list) = get_mac_camera_list()

Dependencies:
    subprocess - functions to spawn off shell threads
    os.path -- functions for file path manipulation
    logging -- used to log progress
    hardware_dependencies -- values specific to camera vendors, e.g. camera_name_prefix_list, desired_camera_protocol

Inheritance:    None

Testing: TODO: To be determined

Warnings: None

Updates:    Scott McGregor,  modified 22-Nov-2021, added header documentation

Notes:  None

TO DO:   None

"""
__author__ = 'Scott McGregor'

import logging
import os
import subprocess
import time

from hardware_dependencies import camera_name_prefix_list
from sonascan_file_paths import scans_dir
from demo import update_window_on_scan


path_to_ffmpeg = os.path.abspath('/usr/local/bin/ffmpeg')  # path to the ffmpeg program


def get_mac_cameras_list(window):
    print(f'\n\tENTERING get_mac_cameras_list()')

    camera_list = list()
    usb_map_dict = dict()

    tic = time.perf_counter()
    # print("\tSearching for available cameras")
    # ffmpeg -hide_banner -f avfoundation -list_devices true -i 1
    run_cmd = subprocess.run([path_to_ffmpeg, '-hide_banner',
                              '-f', 'avfoundation', '-list_devices', 'true', '-i', '1'],
                             universal_newlines=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)  # NOTE!!! ffmpeg writes to stderr, not stdout!
    # print("\tAvailable cameras search complete.")
    # note that ffmpeg writes to stderr, not stdout

    stderr_buffer = run_cmd.stderr.splitlines()
    if stderr_buffer == '':
        print("\tWARNING: No Cameras found; Will Use DEMO images instead. ", run_cmd.stderr)

    elif "command not found" in stderr_buffer:
        # This error msg suggests that the ffmpeg shell program wasn't found.  We explain how to install it:
        print("\tWARNING: ffmpeg program was not found; using DEMO images. ")

    else:  # the returned output should include a list of devices that we will need to parse to find
        #    just those devices which are our CAMERA_NAME_PREFIX cameras.

        camera_dict = dict()
        lines = stderr_buffer
        for camera_name_prefix in camera_name_prefix_list:
            # print(f"Identifying just those cameras with camera_name_prefix ='{camera_name_prefix}'")
            number_of_cameras = 1
            for line in lines:
                if camera_name_prefix in line:
                    # parse the line as follows:
                    # [ discarded data ] [cameraID] camera_name
                    if "[" in line:
                        string1 = line.split("[")[2]
                        string2 = line.split("[")[2]
                        camera_id = string2.split("]")[0].strip()
                        camera_name = string1.split("]")[1].strip()
                        camera_list.append(camera_id)
                        camera_dict[camera_id] = camera_name
                        window['_ACTION_STATUS_LINE_1_'].update(f"Testing Cameras, please wait.")
                        window['_PROGRESS_BAR_'].update(100 * number_of_cameras / 18)
                        number_of_cameras = number_of_cameras + 1
                        window['_ACTION_STATUS_LINE_3_'].update(f"{camera_name}")
                        window.refresh()
                # else: case do nothing and just loop again.
                    #  print("\tthis is not a ", camera_name_prefix, " camera")

            number_of_responding_cameras = len(camera_list)
            toc = time.perf_counter()
            duration = toc - tic
            print(f"\tCaptured list of {number_of_responding_cameras}"
                  + f" '{camera_name_prefix}' cameras in: {duration:0.0f} seconds")

    # TODO: we should sort the camera list in order by our camera positions
    #       We want to return a list of /dev/video* devices,
    #       but we want them sorted by device number, not alphabetically
    #       for key in sorted(camera_dict):
    #           sonautics_camera_list.append(camera_dict[key])

    print(f"\tSonautics camera_list ='{camera_list}'" )

    print(f'\tEXITING get_mac_cameras_list()\n')
    return camera_list, usb_map_dict


def mac_capture_scanner_images(full_scan_id, cameras_list, window):
    print(f'\n\t\tENTERING mac_capture_scanner_images()')
    image_capture_tic = time.perf_counter()
    image_counter = 0
    images_list = {}
    to_directory = os.path.join(scans_dir, full_scan_id)
    max_cameras = len(cameras_list)
    for camera_id in cameras_list:
        camera_file_path = avfoundation_capture_photo_and_return_image_path(camera_id, to_directory, image_counter)
        images_list[camera_id] = camera_file_path
        print("\t\t**************************", camera_file_path, "**************************")
        update_window_on_scan(camera_file_path, full_scan_id, image_counter, max_cameras, window)

    image_capture_toc = time.perf_counter()
    duration = image_capture_toc - image_capture_tic
    print(f"\t\t{full_scan_id} captured {image_counter} images in: " + f"{duration:0.0f} seconds.")
    print(f'\t\tEXITING mac_capture_scanner_images()\n')
    return images_list


def avfoundation_capture_photo_and_return_image_path(camera_id, image_dir_path, counter):
    print(f'\n\t\tENTERING avfoundation_capture_photo_and_return_image_path()')
    image_capture_tic = time.perf_counter()
    # print(f'\t\t{counter}')
    # print("\t\tcamera_id=", camera_id)
    image_number = int(camera_id)
    if image_number >= 10:  # for double digit camera numbers, use the two digits
        image_file_name = "SonaCam" + str(image_number) + '.jpg'
    else:  # for single digit camera numbers prepend a leading zero so numeric and alphabetic sorts match
        image_file_name = "SonaCam0" + str(image_number) + '.jpg'
    full_image_file_name = os.path.join(image_dir_path, image_file_name)
    run_cmd = ''
    # ffmpeg -y -hide_banner -f avfoundation -video_size 1920x1080 -pixel_format
    # uyvy422 -framerate 15 -i 0 -frames:v 1 -f image2 img0.jpg
    try:
        run_cmd = subprocess.run(
            [path_to_ffmpeg, '-y', '-hide_banner',
             '-f', 'avfoundation',
             # '-video_size', '1920x1080',
             # '-pixel_format', 'uyvy422',
             '-pixel_format', 'yuv420p',
             '-ss', '6',  # let's wait6 frames so exposure and focus settle down before we capture image
             '-r', '30',  # 30 frame rate = frames per second
             '-i', camera_id,
             '-frames:v', '1',
             '-vf', "scale=in_range=mpeg:out_range=full",
             '-f', 'image2',
             full_image_file_name],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )  # Note, ffmpeg writes to stderr, not stdout!
        # print('\t\t{run_cmd.stderr}')
        logging.info(run_cmd.stderr)
        # camera_number = int(camera_id) + 1
        # image_capture_toc = time.perf_counter()
        # print(f"\t\tCaptured SonaCam {camera_id}  in: {image_capture_toc - image_capture_tic:0.0f} seconds")
        print(f'\t\tEXITING avfoundation_capture_photo_and_return_image_path()\n')
        return os.path.join(image_dir_path, full_image_file_name)

    except Exception as e:
        print("\t\tError", repr(e))
        print("\t\tUnable to capture image for", full_image_file_name)
        if run_cmd != '':
            print(f'\t\t{run_cmd.stdout}')
            print(f'\t\t{run_cmd.stderr}')
        image_capture_toc = time.perf_counter()
        print(f"\t\tError capturing {camera_id} image: {image_capture_toc - image_capture_tic:0.0f} seconds")
        print("\t\tin avfoundation_capture_photo_and_return_image_path(",
              camera_id, ",", image_dir_path, ",", image_number, ")", "returns ''")
        print(f'\t\tEXITING avfoundation_capture_photo_and_return_image_path()\n')
        return ''


if __name__ == '__main__':
    test_camera_list, test_usb_map_dict = get_mac_cameras_list()
    print("camera_list=", test_camera_list)
    print("usb_map_dict=", test_usb_map_dict)
    n = 0
    for the_camera_id in test_camera_list:
        avfoundation_capture_photo_and_return_image_path(the_camera_id, test_camera_list, n)
        n = n + 1
