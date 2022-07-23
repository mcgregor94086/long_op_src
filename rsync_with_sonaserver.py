# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function:  rsync_to_server(src_dir, dst_dir, scan_id)

Purpose:
    synchronizes contents of directories on client and server

Parameters:

    src_dir (filepath): The local source directory to be uploaded
    dst_dir (filepath): The server side directory to be created and synced
    scan_id (string):  The local scan_id to upload

Returns:

     uploaded_files_in_scan_dir (int), rsync_cmd (string)

Description: synchronizes contents of directories on client and server

Raises: None

Usage: uploaded_files_in_scan_dir, rsync_cmd   = sync_to_server(src_dir, dst_dir, scan_id)

Dependencies:

    logging -- functions for logging program status
    pathlib -- path manipulations functions
    subprocess -- functions for running background shell processes
    paramiko -- functions for remote access on server using SSH
    os_dependencies  -- os_dependent variables and functions.

Inheritance:    None

Warnings: Isolates os dependent code and variable values.

Testing: TODO: To be determined

Updates:

        Scott McGregor,  modified 22-Nov-2021, added header documentation

Notes:  None

TO DO:  None

"""

__author__ = 'Scott McGregor'

import logging
import os
import pathlib
import subprocess

import paramiko
from paramiko.client import SSHClient

from GUI_defs import window
from os_dependencies import path_to_rsync, PEM_KEY_FILE


def rsync_to_server(src_dir, dst_dir, scan_id):
    logging.debug(f"IN rsync_to_server({src_dir}, {dst_dir}, {scan_id}")
    print(f"IN rsync_to_server({src_dir}, {dst_dir}, {scan_id}")
    # message = "Now uploading Scan_id: " + scan_id
    # window['_ACTION_STATUS_LINE_3_'].update(message)
    # window.Refresh()
    # current_dir = pathlib.Path(__file__).parent
    logging.debug("in directory: {current_dir}")
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
        rsync_return = subprocess.run(rsync_options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("stdout:", rsync_return.stdout.decode('ascii'))
        if rsync_return.stderr.decode('ascii') != "":
            print("rsync_to_server  FAILED ", "stderr:", rsync_return.stderr.decode('ascii'))
            # message = "Scan_id: " + scan_id + "FAILED while uploading."
            # window['_ACTION_STATUS_LINE_3_'].update(message)
            # window.Refresh()
            logging.error(f"stderr: {rsync_return.stderr.decode('ascii')}")
            uploaded_flag = False
            logging.debug(f"rsync_to_server RETURNS {uploaded_flag}, {rsync_cmd}")
            return uploaded_flag, rsync_cmd
        else:
            if rsync_return.stdout.decode('ascii') == "":
                print("no stdout or stderr")
                uploaded_flag = False
            else:
                print(f"rsync_to_server stdout:{rsync_return.stdout.decode('ascii')}")
                uploaded_flag = True
    except Exception as e:
        logging.debug(f"could not upload images to Server! Error: {e}")
        uploaded_flag_2 = False
    else:
        logging.debug(f"uploaded scan data:{src_dir}, to server: {dst_dir}")
        uploaded_flag_2 = True
    print('uploaded_flag_2=', uploaded_flag_2)
    window['_PROGRESS_BAR_'].update(0)
    message = "Scan_id: " + scan_id + " has completed uploading."
    window['_ACTION_STATUS_LINE_3_'].update(message)
    window.Refresh()

    print("rsync_to_server is COMPLETE")
    logging.debug(f"rsync_to_server RETURNS {uploaded_flag}, {rsync_cmd}")
    return uploaded_flag, rsync_cmd


"""
function:  rsync_from_server(dst_dir, src_dir, download_id)

Purpose:
    synchronizes contents of directories on client and server

Parameters:

    src_dir (filepath): The server source directory to be downloaded
    dst_dir (filepath): The local side directory to be created and synced
    download_id (string):  The local scan_id to download

Returns:

     downloaded_files_in_scan_dir (int), rsync_cmd (string) 

Description: synchronizes contents of directories on client and server

Raises: None

Usage: downloaded_files_in_scan_dir, rsync_cmd  = sync_to_server(local_dst_dir, server_src_dir, download_id)

Dependencies:

    logging -- functions for logging program status
    pathlib -- path manipulations functions
    subprocess -- functions for running background shell processes
    paramiko -- functions for remote access on server using SSH
    os_dependencies  -- os_dependent variables and functions.

Inheritance:    None

Warnings: Isolates os dependent code and variable values.

Testing: TODO: To be determined

Updates: Scott McGregor,  modified 01-DEC-2021, added download from server capability

Notes:  None

TO DO:  None

"""


def rsync_from_server(dst_dir, src_dir, download_id):
    logging.debug("IN rsync_from_server(", dst_dir, ",", src_dir, ",", download_id, ")")
    print("IN rsync_from_server(", dst_dir, ",", src_dir, ")")
    # message = "Now downloading download_id: " + download_id
    # window['_ACTION_STATUS_LINE_3_'].update(message)
    # window.Refresh()
    current_dir = pathlib.Path(__file__).parent
    logging.debug("in directory:", current_dir)
    key_pair = "ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i " + PEM_KEY_FILE
    rsync_options = [
        path_to_rsync, "-e", key_pair, "-ptLgoD",
        "--recursive",
        # "--progress",
        "--stats",
        "--ignore-existing",
        "--compress",
        #  "--remove-source-files",
        src_dir, dst_dir
        ]

    rsync_cmd = ' '.join(rsync_options)
    logging.debug(rsync_cmd)
    print(rsync_cmd)
    downloaded_flag = False
    try:
        rsync_return = subprocess.run(rsync_options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("stdout:", rsync_return.stdout.decode('ascii'))
        if rsync_return.stderr.decode('ascii') != "":
            print("rsync_from_server  FAILED ", "stderr:", rsync_return.stderr.decode('ascii'))
            # message = "download_id: " + download_id + "FAILED while downloading."
            # window['_ACTION_STATUS_LINE_3_'].update(message)
            # window.Refresh()
            logging.error("stderr:", rsync_return.stderr.decode('ascii'))
            downloaded_flag = False
            logging.debug("rsync_from_server RETURNS", downloaded_flag, ",", rsync_cmd)
            return downloaded_flag, rsync_cmd
        else:
            if rsync_return.stdout.decode('ascii') == "":
                print("no stdout or stderr")
                downloaded_flag = False
            else:
                print("rsync_to_server stdout:", rsync_return.stdout.decode('ascii'))
                downloaded_flag = True
    except Exception as e:
        logging.debug("could not download files from Server! Error:", e)
        downloaded_flag_2 = False
    else:
        logging.debug("downloaded data:", dst_dir,  "from server:", src_dir)
        downloaded_flag_2 = True
    print('downloaded_flag_2=', downloaded_flag_2)

    # message = "download_id: " + download_id + " has completed downloading."
    # window['_ACTION_STATUS_LINE_3_'].update(message)
    # window.Refresh()

    print("rsync_from_server is COMPLETE")
    logging.debug("rsync_from_server RETURNS", downloaded_flag, ",", rsync_cmd)
    return downloaded_flag, rsync_cmd


def list_files_in_a_sonaserver_directory(remote_directory, file_pattern="/*"):
    print(remote_directory)
    try:
        cert = paramiko.RSAKey.from_private_key_file(PEM_KEY_FILE)
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # paramiko.MissingHostKeyPolicy(
        client.connect('cloud1.tri-di.com', username='scansteruser', pkey=cert)
        ssh_cmd = "ls " + remote_directory + file_pattern
        print(ssh_cmd)
        stdin, stdout, stderr = client.exec_command(ssh_cmd)
    except Exception as e:
        logging.debug(f"Could not get list of files in {remote_directory} on  SonaServer! Error:{e}")
        return []
    print("remote files are:")
    uploaded_files_in_scan_dir = stdout.readlines()
    print(uploaded_files_in_scan_dir)
    return uploaded_files_in_scan_dir


if __name__ == '__main__':
    src_dir_x = '/var/Sonautics/data/scans/test_scanner/20211118225930'
    dst_dir_x = 'scansteruser@cloud1.tri-di.com:cloud1.tri-di.com/data/uploaded/test_scanner'
    scan_id_x = 'test_scanner/20211118225930'
    remote_directory_x = '/home/scansteruser/cloud1.tri-di.com/data/uploaded/test_scanner/20211118225930'
    rsync_to_server(src_dir_x, dst_dir_x, scan_id_x)
    list_files_in_a_sonaserver_directory(remote_directory_x)
    print()
