# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function: get_linux_camera_list()

Purpose:

    Gets the list of camera device addresses when connected to a Linux processor

Parameters: None

Returns:

    images_list: list of camera device addresses to request images from.

Description:

    Gets the list of camera device addresses when connected to a Linux processor

Raises: None

Usage:

    images_list = get_linux_camera_list()

    Dependencies:  Any libraries, devices, etc. that must be present.

    subprocess - functions to spawn off shell threads
    os.path -- functions for file path manipulation
    logging -- used to log progress
    hardware_dependencies -- values specific to camera vendors, e.g. camera_name_prefix_list, desired_camera_protocol

Inheritance:    None

Testing: TODO: To be determined


Warnings: None


Updates: Scott McGregor,  modified 22-Nov-2021, added header documentation

Notes:  None

TO DO:   None

"""

__author__ = 'Scott McGregor'

import os
import re
import subprocess
import time
from os.path import abspath
import logging
import PySimpleGUI as sg

from hardware_dependencies import camera_name_prefix_list, desired_camera_protocol
from image_processing import convert_to_bytes
from sonascan_file_paths import scans_dir, images_dir

path_to_v4_l2_ctl = abspath('/usr/bin/v4l2-ctl')  # path to the v4l2-ctl program
path_to_ffmpeg = abspath('/usr/bin/ffmpeg')  # path to the ffmpeg program


def get_linux_cameras_list(window):
    # L4V2-CTL call gets a list of ALL video4linux devices, which may include devices other than our cameras.
    # NOTE: Current implementation is not efficient if there is more than one valid camera_name_prefix

    # initializing...
    our_camera = False
    camera_list = list()
    camera_dict = dict()
    usb_map_dict = dict()
    camera_number = 0
    number_of_cameras = 1
    usb_path = ''
    print("Polling available cameras")

    result = subprocess.run([path_to_v4_l2_ctl, '--list-devices'], stdout=subprocess.PIPE)
    lines = result.stdout.splitlines()
    # TODO: This does a loop for every camera name prefix in a list.  If there is more than one
    #       valid camera name prefix this is probably inefficient
    for camera_name_prefix in camera_name_prefix_list:
        dev_video_camera_lines = [x for x in lines if x.decode('ascii').startswith(camera_name_prefix)]

        print(camera_name_prefix, "Camera polling complete.", len(dev_video_camera_lines), "found")
        print(dev_video_camera_lines)
        # Sample output from v4tl2-ctl looks like this:
        #
        #        SonaCam: SonaCam (usb-0000:01:00.0-1.1.1.3.1.1):
        #             /dev/video17
        #             /dev/video18
        #
        #         SonaCam: SonaCam (usb-0000:01:00.0-1.1.1.3.1.2):
        #             /dev/video0
        #             /dev/video1
        #         ...

        # The following code takes the returned list and prunes out the cameras that don't have our
        # CAMERA_NAME_PREFIX in their USB ProductID field
        for line in lines:
            camera_number = camera_number + 1
            line_string = line.decode('UTF-8')
            print(line_string)
            starts_with = line_string[0:len(camera_name_prefix)]
            print(starts_with, camera_name_prefix)
            if starts_with == camera_name_prefix:
                our_camera = True
                usb_path = re.search("\(([^)]+)", line_string).group(1)
                # logging.debug("usb_path =", usb_path)
                # TROUBLESHOOTING: This maybe useful to keep for identifying problem cameras that may need replacement
                # usb_address = line_string.split()[4]

            elif line.startswith(b'\t/dev/video'):
                if our_camera:
                    this_camera = line[1:].decode()

                    # L4V2-CTL reports TWO /dev/video* devices for each of our cameras.
                    # But we only want the ones with we can access with our  DESIRED CAMERA PROTOCOLS

                    # NOTE: See comment blocks above for ideas about how to speed this up!

                    # ffmpeg -hide_banner -f v4l2 -list_formats all -i /dev/video$i 2>&1  | grep yuyv422
                    result = subprocess.run([path_to_ffmpeg, '-hide_banner',
                                             '-f', 'v4l2',
                                             '-list_formats', 'all',
                                             '-i', this_camera],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    #  NOTE: ffmpeg writes to stderr, not stdout, so we read from there. Here is sample output:
                    # [video4linux2,v4l2 @ 0xf5f1c0] Compressed: mjpeg :   Motion-JPEG :
                    #   640x480 1280x720 640x360 320x240 1920x1080
                    # [video4linux2,v4l2 @ 0xf5f1c0] Raw       : yuyv422 : YUYV 4:2:2 :
                    #   640x480 1280x720 640x360 320x240 1920x1080
                    # /dev/video0: Immediate exit requested

                    decoded_output = result.stderr.decode('UTF-8')
                    if desired_camera_protocol in decoded_output:
                        device_number = int(os.path.basename(this_camera)[5:])
                        camera_dict[device_number] = this_camera
                        usb_map_dict[usb_path] = this_camera
                        logging.debug(f"{usb_path} -> {this_camera}")
                        # camera_list.append(this_camera)
                        if (number_of_cameras % 2)==0:
                            thumbnail = convert_to_bytes(os.path.join(images_dir, "open_shutter.jpg"))
                        else:
                            thumbnail = convert_to_bytes(os.path.join(images_dir, "closed_shutter.jpg"))
                        window['_IMAGE_ELEMENT_'].update(data=thumbnail)
                        window['_ACTION_STATUS_LINE_1_'].update(f"Testing Cameras, please wait.")
                        window['_PROGRESS_BAR_'].update(100 * number_of_cameras / 18)
                        number_of_cameras = number_of_cameras + 1
                        window['_ACTION_STATUS_LINE_3_'].update(f"{this_camera}")
                        window.refresh()

                        # TROUBLESHOOTING: The usb_address maybe useful to keep for identifying problem cameras
                        # that may need replacement
                        # logging.debug(usb_path, "->", this_camera)

                    # ELSE, if it is not a SonaCam we ignore it
                else:  # ELSE, if it is not a /dev/video device we ignore it

                    our_camera = False
                    # In terms of taking photos, the /dev/video* names in camera_list
                    # are what we need to return.

        logging.debug("Camera selection complete.")
        print("Camera selection complete.")

        logging.debug("DEBUG: usb_map_dict", usb_map_dict)
        # We want to return a list of /dev/video* devices, but we want them sorted by device number,
        # not alphabetically
        for key in sorted(camera_dict):
            camera_list.append(camera_dict[key])
        logging.debug("get_linux_cameras_list() RETURNS  {camera_list}, {usb_map_dict}")
        thumbnail = convert_to_bytes(os.path.join(images_dir, "status-ready.png"))
        window['_IMAGE_ELEMENT_'].update(data=thumbnail)
        window['_ACTION_STATUS_LINE_1_'].update(f"Testing Complete, Ready to Scan.")
        window.refresh()
        return camera_list, usb_map_dict


def linux_capture_scanner_images(full_scan_id, cameras_list, window):
    image_capture_tic = time.perf_counter()
    image_counter = 0
    images_list = {}
    to_directory = os.path.join(scans_dir, full_scan_id)
    for camera_id in cameras_list:
        camera_file_path = linux_capture_photo_and_return_image_path(camera_id, to_directory, image_counter, window)
        images_list[camera_id] = camera_file_path
        # print(camera_file_path)
        # scan_image_name = os.path.basename(camera_file_path)
        # window['_ACTION_STATUS_LINE_3_'].update(full_scan_id + " new scan image.")
        # window['_ACTION_STATUS_LINE_2_'].update(scan_image_name)
        # window['_PROGRESS_BAR_'].update(100 * image_counter / max_cameras)
        # window.Refresh()
        image_counter = image_counter + 1

    image_capture_toc = time.perf_counter()
    print(f"{full_scan_id} captured {image_counter} images in: "
          + f"{image_capture_toc - image_capture_tic:0.0f} seconds.")
    return images_list


def linux_capture_photo_and_return_image_path(camera_id, image_dir_path, n, window):
    logging.debug(f"IN linux_capture_photo_and_return_image_path({camera_id}, {image_dir_path}, {n})")
    image_number = int(os.path.basename(camera_id)[5:])
    if image_number >= 10:  # for double-digit camera numbers, use the two digits
        image_file_name = "SonaCam" + str(image_number) + '.jpg'
    else:  # for single digit camera numbers prepend a leading zero so numeric and alphabetic sorts match
        image_file_name = "SonaCam0" + str(image_number) + '.jpg'
    full_image_file_name = os.path.join(image_dir_path, image_file_name)
    image_capture_tic = time.perf_counter()

    logging.debug(f"{n} Writing camera image to {full_image_file_name}")
    run_cmd = ''
    # run_cmd = subprocess.run(
    #     ['v4l2-ctl', '-d', camera_id, '-c', 'exposure_auto=1'],
    #     universal_newlines=True,
    #     # shell=True
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE
    # )
    # ffmpeg -hide_banner -f video4linux2 -s 1920x1080 -i /dev/video2 -ss 0:0:2 -frames 1 /tmp/full_image_file_name
    ffmpeg_options = [
                       os.path.abspath('take_a_photo.sh'), camera_id, full_image_file_name
                       # PATH_TO_FFMPEG, '-y', '-hide_banner',
                       # '-f', 'v4l2',
                       # '-i', camera_id,
                       # '-frames', '1',
                       # '-f', 'image2',
                       # full_image_file_name
                      ]
    print(ffmpeg_options)
    logging.debug(ffmpeg_options)
    try:
        run_cmd = subprocess.run(
            ffmpeg_options,
            universal_newlines=True,
            # shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )  # Note, ffmpeg writes to stderr, not stdout!
        # note that typical ffmpeg output looks like this:
        # Input #0, video4linux2,v4l2, from '/dev/video2':
        #   Duration: N/A, start: 53355.628804, bitrate: 165888 kb/s
        #     Stream #0:0: Video: rawvideo (YUY2 / 0x32595559), yuyv422, 1920x1080, 165888 kb/s, 5 fps, 5 tbr,
        #     1000k tbn, 1000k tbc
        # Stream mapping:
        #   Stream #0:0 -> #0:0 (rawvideo (native) -> mjpeg (native))
        # Press [q] to stop, [?] for help
        # [swscaler @ 0x2097e10] deprecated pixel format used, make sure you did set range correctly
        # Output #0, image2, to '/tmp/out.jpg':
        #   Metadata:
        #     encoder         : Lavf58.20.100
        #     Stream #0:0: Video: mjpeg, yuvj422p(pc), 1920x1080, q=2-31, 200 kb/s, 5 fps, 5 tbn, 5 tbc
        #     Metadata:
        #       encoder         : Lavc58.35.100 mjpeg
        #     Side data:
        #       cpb: bitrate max/min/avg: 0/0/200000 buffer size: 0 vbv_delay: -1
        # frame=    1 fps=0.0 q=8.1 Lsize=N/A time=00:00:00.20 bitrate=N/A speed=1.33x
        # video:112 kB audio:0 kB subtitle:0 kB other streams:0 kB global headers:0 kB muxing overhead: unknown

        # also note that the message:
        # [swscaler @ 0x2097e10] deprecated pixel format used, make sure you did set range correctly
        # is a warning that SHOULD be ignored.  For an explanation of WHY ffmpeg displays this warning,
        # and why it is correct for us to ignore it, see
        # https://superuser.com/questions/1273920/deprecated-pixel-format-used-make-sure-you-did-set-range-correctly/1273941#1273941

        logging.debug(run_cmd.stderr)
        print(run_cmd.stderr)
        image_capture_toc = time.perf_counter()
        logging.debug(f"Captured {camera_id} image in: {image_capture_toc - image_capture_tic:0.0f} seconds")
        logging.debug(f"linux_capture_photo_and_return_image_path({camera_id}, {image_dir_path}, {n}" +
                      f") RETURNS {full_image_file_name}")
        print(f"Captured {camera_id} image in: {image_capture_toc - image_capture_tic:0.0f} seconds")

        image = convert_to_bytes(full_image_file_name, resize=(96, 54))

        if window is not None:
            window['_IMAGE_ELEMENT_'].update(data=image)
            window["_PROGRESS_BAR_"].update(100 * (n + 1) / 18)
            window.Refresh()

        print("linux_capture_photo_and_return_image_path(", camera_id, ",", image_dir_path, ",", n,
              ") RETURNS", full_image_file_name)

        return full_image_file_name

    except Exception as e:
        logging.error("Error", repr(e))
        logging.error("Unable to capture image for", full_image_file_name)
        if run_cmd != '':
            logging.error(run_cmd.stdout)
            logging.error(run_cmd.stderr)
        image_capture_toc = time.perf_counter()
        logging.error(f"Error capturing {camera_id} image: {image_capture_toc - image_capture_tic:0.0f} seconds")
        # logging.error("linux_capture_photo_and_return_image_path(", camera_id, ",", image_dir_path, ",", image_number,
        #               ") RETURNS ''"
        #               )
        return ''


def g_uvc_viewer(cameras_list):

    """
        Allows you to "browse" through the list of usb cameras.
        Click on one, and you'll see a live video feed from that camera, and
        be able to change its camera settings.
        It's a simple little program that also demonstrates
        how snappy a GUI can feel if you enable an element's events
        rather than waiting on a button click.
        In this program, as soon as a listbox entry is clicked, the read returns.
    """

    sg.theme('Dark Brown')
    # images_list = linux_capture_scanner_images("TEST/TEST", cameras_list, None)

    layout = [[sg.Text('USB Cameras Settings Panel')],
              [sg.Text('Click a Camera to view')],
              [sg.Listbox(values=cameras_list, size=(20, 18), key='-LIST-', enable_events=True)],
              [sg.Button('Exit')]]

    guvc_window = sg.Window('USB Camera Browser', layout)

    while True:  # Event Loop
        event, values = guvc_window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        device_path = values['-LIST-'][0]
        print(f"/usr/bin/guvcview --device='{device_path}'")
        sg.execute_command_subprocess("/usr/bin/guvcview", f"--device='{device_path}'")
        # sp = sg.execute_command_subprocess(args[0], *args[1:])
        # This will cause the program to wait for the subprocess to finish
        # print(sg.execute_get_results(sp)[0])
        # sg.theme(values['-LIST-'][0])
        # sg.popup_get_text('This is {}'.format(values['-LIST-'][0]))

    guvc_window.close()
    return


if __name__ == '__main__':
    camera_list_x, usb_map_dict_x = get_linux_cameras_list()
    print("sonautics_camera_list=", camera_list_x)
    print("usb_map_dict=", usb_map_dict_x)

    g_uvc_viewer(camera_list_x)
if __name__ == '__main__':
    camera_list_x, usb_map_dict_x = get_linux_cameras_list()
    print("sonautics_camera_list=", camera_list_x)
    print("usb_map_dict=", usb_map_dict_x)
