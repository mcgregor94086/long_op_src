# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function:  do_obj_download(full_scan_id, window, image_counter, photoscene_id)

Purpose:    Download the OBJ file

Parameters:

    full_scan_id (string) -- unique scan id in format: scanner_id/scan_id
    window (window handle) -- used to send messages to be displayed in GUI
    image_counter (int) -- number of images used to create model
    photoscene_id (string) -- the id assigned by Autodesk Forge where the OBJ files will be written

Returns: None

Description: Download the OBJ file

Raises: None

Usage: do_obj_download(full_scan_id, window, image_counter, photoscene_id)


Dependencies:  Any libraries, devices, etc. that must be present.

        time -- used to time durations
        logging -- used to write logging messages
        get_obj -- used to get the OBJ file


Inheritance:    None

Testing: TODO: To be determined by QA

Warnings: None

Updates: Scott McGregor,  modified 24-Nov-2021, first implementation

Notes:  None

TODO:   Clean up imports including get_obj
"""

__author__ = 'Scott McGregor'

import logging
import os
import shutil
# import time
from pathlib import Path
import PySimpleGUI as sg
# import xmltodict as xmltodict
from dict2xml import dict2xml

from send_mail import send_mail

from GUI_defs import window
from os_dependencies import path_to_meshconv
from scandir_index_maker import scandir_index_maker
from send_models_to_server import send_models_to_server
from sonascan_file_paths import view_stl_file, SERVER_UPLOAD_DIR_ROOT_PATH, scans_dir, order_pdf_file, \
    SERVER_MODEL_ROOT_PATH, SERVER_WEB_ROOT


def do_convert_obj_to_stl(cropped_obj_file, photoscene_id, main_window, scan_data_dictionary):
    # -------------------- CONVERT OBJ TO STL FORMAT -----------------------------
    #
    # convert the .obj to a .stl format using meshconv and store stl file in photoscene_dir

    stl_filename_base = Path(cropped_obj_file).stem
    stl_filename = stl_filename_base + ".stl"
    shell_command = [path_to_meshconv, cropped_obj_file, "-c", "stl", "-o", stl_filename_base]
    answer = sg.execute_command_subprocess(path_to_meshconv, cropped_obj_file, "-c", "stl", "-o", stl_filename_base,
                                           wait = True)
    # answer = subprocess.run(shell_command,
    #                         universal_newlines=True,
    #                         # shell=True,
    #                         stdout=subprocess.PIPE,
    #                         stderr=subprocess.PIPE)
    print(shell_command)
    print("convert OBJ to STL stdout:", answer.stdout)

    scan_id_path, obj_name = os.path.split(cropped_obj_file)
    short_scan_id = os.path.dirname(cropped_obj_file)
    scanner_id = os.path.dirname(scan_id_path)
    full_scan_id = os.path.join(scanner_id, short_scan_id)

    # if stl file does NOT exist: ERROR message no STL file, send failure email and quit
    if not os.path.exists(stl_filename):
        print("ERROR: 94: no STL file was created. Now Quitting.")
        subject = full_scan_id + "/" + photoscene_id + ": ERROR 94: No STL file was created."
        print(subject)
    else:  # else fall through, STL file exists

        message = f"{full_scan_id}:{photoscene_id} STL model has been created. "
        print(message)
        logging.info(message)
        window['_ACTION_STATUS_LINE_3_'].update(message)
        window.Refresh()

        new_view_stl_file = os.path.join(os.path.dirname(cropped_obj_file), 'view_stl_file.html')
        shutil.copyfile(view_stl_file, new_view_stl_file)
        subject = full_scan_id + "/" + photoscene_id + " (consumer_id): SUCCESS: New 3D model ready for CAD."

        # Update the local version of index.html in the UPLOADS directory
        # scandir_index_maker(SERVER_UPLOAD_DIR_ROOT_PATH, full_scan_id)

        message = f"{full_scan_id}:{photoscene_id} index created. "
        print(message)
        logging.info(message)
        main_window['_ACTION_STATUS_LINE_3_'].update(message)
        main_window.Refresh()

        # scan_job_data_record = xmltodict.parse(xml_content)
        # scan_data_dictionary["scanner_id"] = scanner_id
        # scan_data_dictionary["scan_id"] = scan_id
        # scan_data_dictionary["local_scan_dir"] = os.path.join(scans_dir, scanner_id, short_scan_id)
        scan_data_dictionary["server_scan_dir"] = SERVER_WEB_ROOT + os.path.join(scans_dir, scanner_id, short_scan_id)

        from_email = scan_data_dictionary['_SENDER_']
        to_email = scan_data_dictionary['_RECIPIENT_']
        order_details = scan_data_dictionary['_ORDER_DETAILS_']
        # send_mail = scan_job_data_record['send_mail']
        # send_models_to_server = scan_job_data_record['send_models_to_server']
        scan_job_data_record = scan_data_dictionary
        print(scan_data_dictionary)
        manifest_xml_file = os.path.join(scans_dir, scanner_id, short_scan_id, 'manifest.xml')
        xml = dict2xml(scan_data_dictionary, wrap='sonascan_manifest', indent='    ')
        # xml_decode = xml.decode()
        xml_file = open(manifest_xml_file, 'w')
        xml_file.write(xml)
        xml_file.close()

        # attach order_pdf_file to email
        files_list = [stl_filename,
                      manifest_xml_file,
                      order_pdf_file,
                      view_stl_file,
                      ]

        # We email STL file to SonaCAD recipient
        smtp_server = 'smtp.dreamhost.com'
        smtp_port = 465
        smtp_username = 'orders@sonautics.com'
        smtp_password = 'Use4SonauticsOrderDaemon'
        print(from_email, to_email, subject, order_details, files_list,
              smtp_server, smtp_port, smtp_username, smtp_password, True)

        send_mail(from_email, to_email, subject, order_details, files=files_list,
                  smtp_server=smtp_server, smtp_port=smtp_port,
                  smtp_username=smtp_username, smtp_password=smtp_password,
                  use_tls=True)

        message = f"{full_scan_id}:{photoscene_id} email sent. "
        print(message)
        logging.info(message)
        main_window['_ACTION_STATUS_LINE_3_'].update(message)
        main_window.Refresh()

        # Move local models directory to SERVER MODELS directory
        # server_data_path = 'scansteruser@cloud1.tri-di.com:~/cloud1.tri-di.com/data/uploaded'
        src_dir = os.path.join(scans_dir, full_scan_id)
        dst_dir = os.path.join(SERVER_MODEL_ROOT_PATH, full_scan_id)
        uploaded_flag, rsync_cmd = send_models_to_server(src_dir, dst_dir, full_scan_id, photoscene_id, window)
        print(uploaded_flag, rsync_cmd)

        main_window['_ACTION_STATUS_LINE_1_'].update("Modeling Complete")
        main_window['_ACTION_STATUS_LINE_2_'].update("Ready for next scan")
        main_window['_ACTION_STATUS_LINE_3_'].update("Modeling Complete")
        main_window.Refresh()

    return stl_filename


if __name__ == '__main__':  # use for unit testing
    my_full_scan_id = "test/test"
    my_window = window
    my_photoscene_id = "test"
    # do_obj_download(my_full_scan_id, my_window, my_photoscene_id)
