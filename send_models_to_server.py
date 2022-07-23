# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function:  send_models_to_server

Purpose:
    sends a model directory to the server

Parameters:
    src_dir (file_path): the path to the model directory to upload to SonaServer
    dst_dir (network_file_path): the path to where to put the model directory on the SonaServer
    full_scan_id (string): the scan_id to upload
    photoscene_id (string): the photoscene_id to upload
    window (PySimpleGUI.window) handle for the main GUI window

Returns:
    uploaded_flag (boolean): True if upload succeeds, false otherwise.
    rsync_cmd (string):  the rsync command used to upload the models

Description: A detailed description of the function, including explanations of algorithms, intent, and any tricks.

    E.g.
    This method relies on the FFMPEG library to capture an image from each camera.
    Tricks: Note FFMPEG is OS-dependent,  and specifically the MAC OS X and Linux (Raspberry Pi) systems require
    require different parameters,  so we have to check the OS and use different branches for each.

Raises: None

Usage:
    uploaded_flag, rsync_cmd = send_models_to_server(src_dir,
                                                    dst_dir,
                                                    full_scan_id,
                                                    photoscene_id,
                                                    window)

Dependencies:  Any libraries, devices, etc. that must be present.
    logging -- python library for writing logs
    os  -- python library for os and path functions
    pathlib  -- python library for os and path functions
    subprocess  -- python library for running subprocesses

    from local os_dependencies:
        path_to_rsync -- where the rsync program is in file system
        PEM_KEY_FILE  --  security key file for remote login

Inheritance:   None

Testing: TODO: TBD by QA

Warnings: None

Updates: Scott McGregor,  written 05-Dec-2021, initial code

Notes:  None

TO DO:   None
"""


__author__ = 'Scott McGregor'

import logging
import os
import pathlib
import subprocess

from os_dependencies import path_to_rsync, PEM_KEY_FILE


def send_models_to_server(src_dir, dst_dir, full_scan_id, photoscene_id, window):
    logging.debug(f"send_models_to_server( {src_dir}, {dst_dir}," +
                  f"{full_scan_id}, {photoscene_id},  {window} )")
    print("send_models_to_server(", src_dir, ",", dst_dir, ",",
          full_scan_id, ",", photoscene_id, ",", window, ")")
    message = "Now uploading Scan_id: " + full_scan_id
    window['_ACTION_STATUS_LINE_3_'].update(message)
    window.Refresh()
    current_dir = pathlib.Path(__file__).parent
    logging.debug(f"in directory: {current_dir}")
    key_pair = "ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i " + PEM_KEY_FILE
    parent_dst_dir = os.path.dirname(dst_dir)
    rsync_options = [
        path_to_rsync, "-e", key_pair, "-ptLgoD",
        "--recursive",
        # "--progress",
        "--stats",
        "--ignore-existing",
        "--compress",
        # "--remove-source-files",
        src_dir, parent_dst_dir
    ]

    rsync_cmd = ' '.join(rsync_options)
    logging.debug(rsync_cmd)
    print(rsync_cmd)
    uploaded_flag = False
    try:
        rsync_return = subprocess.run(rsync_options,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        print("stdout:", rsync_return.stdout.decode('ascii'))
        if rsync_return.stderr.decode('ascii') != "":
            print("rsync_to_server  FAILED ", "stderr:", rsync_return.stderr.decode('ascii'))
            # message = "Scan_id: " + scan_id + "FAILED while uploading."
            # window['_ACTION_STATUS_LINE_3_'].update(message)
            # window.Refresh()
            logging.error("stderr:", rsync_return.stderr.decode('ascii'))
            uploaded_flag = False
            logging.debug("rsync_to_server RETURNS", uploaded_flag, ",", rsync_cmd)
            return uploaded_flag, rsync_cmd
        else:
            if rsync_return.stdout.decode('ascii') == "":
                print("no stdout or stderr")
                uploaded_flag = False
            else:
                print("rsync_to_server stdout:", rsync_return.stdout.decode('ascii'))
                uploaded_flag = True
    except Exception as e:
        logging.debug("could not upload images to Server! Error:", e)
        uploaded_flag_2 = False
    else:
        logging.debug(f"uploaded scan data: {src_dir} to server: {dst_dir}")
        uploaded_flag_2 = True
    print('uploaded_flag_2=', uploaded_flag_2)
    # message = "Scan_id: " + scan_id + " has completed uploading."
    # window['_ACTION_STATUS_LINE_3_'].update(message)
    # window.Refresh()

    print("rsync_to_server is COMPLETE")
    logging.debug(f"rsync_to_server RETURNS {uploaded_flag}, {rsync_cmd}")
    return uploaded_flag, rsync_cmd
