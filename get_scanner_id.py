__author__ = 'Scott McGregor'
# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/

import os
# from os import mkdirs


"""
function:  
    get_serial_number()

Purpose:
    Reads the Scanner ID (Serial Number) from the USB stick embedded in the Scanner

Parameters: None

Returns: scanner_serial_number (used as Scanner_ID)       

Description: 

    Searches for a file in the scanner (name defined in path_to_scanner_serial_number_file).
    If found, its contents is the Scanner's unique Serial Number (Scanner_ID)

Raises: 
    If not, this is a fatal error and the Scanner USB and Power must be connected.  
    The program will then reboot (on Linux) or terminate (on MacOS) so that next time
    the program restarts it will search the USB bus for the scanner USB drive again

Usage: scanner_serial_number = get_serial_number()

Dependencies:  Any libraries, devices, etc. that must be present.

    import glob
    import subprocess
    import PySimpleGUI as sg
    from os_dependencies import path_to_scanner_serial_number_file

Inheritance:    None

Testing: TODO: To be determined
 
    Test for no serial number file found on USB bus

Warnings: 

    Location of mounted USB files may vary across OSes.  This is made os_independent

Updates: 
        Scott McGregor,  modified 22-Nov-2021, Added documentation
"""

import logging
import os
import subprocess
import PySimpleGUI as sg

sonautics_root_dir_path = '/sonautics'
sonautics_logs_dir_path = os.path.join(sonautics_root_dir_path, 'logs')

# ############################## SET UP LOGGING #########################
# TURN ON LOGGING TO SONASCAN.LOG

log_file_path = os.path.join(sonautics_logs_dir_path, "sonascan.log")
logging.basicConfig(
    filename = log_file_path,
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s"
    )
    # logging.debug(sg.main_get_debug_data())
    # ############################## SET UP LOGGING #########################


def get_scanner_id(sonautics_scans_dir, scanner_id_file_path):
    """
    This is the function that looks up the scanner_id from the usb_drive
    :param sonautics_scans_dir:
    :param serial_number_file:
    :return: scanner_id, scanner_dir
    """
    logging.debug(f"checking for scanner_id file:{scanner_id_file_path}")
    file = open(scanner_id_file_path, mode='r')
    scanner_id = file.readline().strip()
    file.close()
    if scanner_id != '':
        # logging.info(f"scanner id found={scanner_id}")
        scan_dir = os.path.join(sonautics_scans_dir, scanner_id)
        os.makedirs(scan_dir, mode=770, exist_ok=True)

        sonautics_root_dir = os.path.dirname(sonautics_scans_dir)
        logs_dir = os.path.join(sonautics_root_dir_path, 'logs', scanner_id)
        os.makedirs(logs_dir, mode=770, exist_ok=True)

        return scanner_id, scan_dir  # ************** NORMAL END OF THIS FUNCTION ****************

    # else no scanner_id found
    # ********** ERROR HANDLING WHEN WE CAN'T DETECT SCANNER SERIAL NUMBER FILE ON THE USB STICK **********************
    logging.error('No scanner_id found in ', scanner_id_file_path)
    no_scanner_serial_number_found_window = sg.popup_error('No scanner_id found',
                                                           'Notify devops@sonautics.com for help.',
                                                           'Unable to resume.',
                                                           # no_scanner_serial_number_found_layout,
                                                           location=(250, 220),
                                                           background_color='#bbbbbb',
                                                           # titlebar_background_color='orange',
                                                           # use_custom_titlebar=True,
                                                           )
    print(no_scanner_serial_number_found_window)
    # ************ REBOOT ON LINUX, JUST QUIT ON MACOS *************************************************************
    if sg.running_linux():
        # subprocess.Popen(['shutdown', '-r', 'now',
        #                   '"No scanner found on USB Bus. Please Connect Scanner and then restart"'
        #                   ])
        exit("No scanner found on USB Bus. Please Connect Scanner and then restart")
    else:
        logging.info('No scanner_id found.')
        exit('No scanner_id found.')
        #  cannot return -- return "NO_SCANNER_SERIAL_NUMBER"
        return scanner_id, scanner_dir


if __name__ == '__main__':  # Use this for Unit testing
    print("Testing get_serial_number()")
    serial_number = get_serial_number()
    print('serial_number=', serial_number)
