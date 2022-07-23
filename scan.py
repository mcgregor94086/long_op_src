import glob
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import PySimpleGUI as sg

from GUI_defs import images_dir, scan_button, disabled_scan_button
from demo import demo
from get_linux_cameras import get_linux_cameras_list, linux_capture_scanner_images
from get_mac_cameras import get_mac_cameras_list, mac_capture_scanner_images
from image_processing import convert_to_bytes
from local_mysql_db import default_scan_price, cad_price, mfg_price, shipping_price, amount_paid, email_attachments, \
    photoscene_id, number_of_images, obj_model_path, stl_path, order_form, discounts_and_credits, \
    specials_and_adjustments, create_a_new_scan_record, update_scan_record
from terminate import terminate
from upload_images import upload_images
from dict2xml import dict2xml


def scan(scan_data):
    print(f'\nENTERING scan({scan_data})')
    ################################################################################################################
    #        Create a new scan record in the DB with default values                                                #
    ################################################################################################################
    # ***************** Create a new scan record in the database  *****************************
    now = str(datetime.now())
    when_created = now
    when_last_updated = now
    status = 'scanning'
    scanner_owner = 'test_owner'  # TODO: We need to lookup the Scanner owner (from USB drive?)
    from_email = scan_data['_SENDER_']
    to_emails = scan_data['_RECIPIENT_']
    email_subject = 'test subject'
    email_body = scan_data['_ORDER_DETAILS_']
    consumer_name = scan_data['_CONSUMER_NAME_']
    consumer_id = scan_data['_CONSUMER_ID_']
    scanner_id = scan_data['scanner_id']
    scan_id = scan_data['scan_id']
    long_scan_id = os.path.join(scanner_id, scan_id)
    window = scan_data['window']
    scan_dir = scan_data['scan_dir']
    camera_list = scan_data['cameras_list']

    # The following default values are defined in local_mysql_db
    # so that they can be included in other functions (in main)
    # from local_mysql_db import email_attachments, photoscene_id, number_of_images, \
    #                   obj_model_path,stl_path, order_form, \
    #                   scan_price, cad_price, mfg_price, shipping_price, discounts_and_credits, \
    #                   specials_and_adjustments, amount_paid

    total_price = default_scan_price + cad_price + mfg_price + shipping_price
    remaining_balance = total_price - amount_paid

    scan_job_data_record = {
        'scanner_id': scanner_id,
        'short_scan_id': scan_id,
        'long_scan_id': long_scan_id,
        'when_created': when_created,
        'when_last_updated': when_last_updated,
        'status': status,
        'scanner_owner': scanner_owner,
        'from_email': from_email,
        'to_emails': to_emails,
        'email_subject': email_subject,
        'email_body': email_body,
        'email_attachments': email_attachments,
        'photoscene_id': photoscene_id,
        'number_of_images': number_of_images,
        'obj_model_path': obj_model_path,
        'stl_path': stl_path,
        'order_form': order_form,
        'scan_price': default_scan_price,
        'cad_price': cad_price,
        'mfg_price': mfg_price,
        'shipping_price': shipping_price,
        'discounts_and_credits': discounts_and_credits,
        'specials_and_adjustments': specials_and_adjustments,
        'total_price': total_price,
        'amount_paid': amount_paid,
        'remaining_balance': remaining_balance,
        'consumer_name': consumer_name,
        'consumer_id': consumer_id,
        'mfg_order_info': "none",
        'cad_order_info': "none",
    }

    logging.debug("Creating new scan record")
    db_response = create_a_new_scan_record(scan_job_data_record)
    logging.debug("Creating new scan record COMPLETE")

    ################################################################################################################
    #         BEGIN SCANNING                                                                                       #
    ################################################################################################################
    logging.debug(db_response)
    image_capture_tic = time.perf_counter()
    window['_ACTION_STATUS_LINE_1_'].update("Now Scanning... Please wait...")
    window['_ACTION_STATUS_LINE_3_'].update("Scanning " + long_scan_id)
    window['_SCAN_BUTTON_'].update(image_filename=disabled_scan_button)
    scan_disabled_state = True
    window.refresh()
    print("***************************************** NEW SCAN ***********************************************")

    logging.info(f"scan() creating scan {long_scan_id}")

    Path(scan_dir).mkdir(parents=True, exist_ok=True)
    scanner_dir = os.path.dirname(scan_dir)
    Path(scanner_dir).mkdir(parents=True, exist_ok=True)
    # DEFERRED_SERVER_REQUESTS_PATH = os.path.join(sonascan_file_paths.data_dir, "deferred")
    # Path(DEFERRED_SERVER_REQUESTS_PATH).mkdir(parents=True, exist_ok=True)

    ################################################################################################################
    #          HOW TO CAPTURE IMAGES ON MAC OS OR LINUX                                                            #
    ################################################################################################################
    if sg.running_linux():

        print('CALLING linux_capture_scanner_images()')
        images_list = linux_capture_scanner_images(long_scan_id, camera_list, window)
        print('RETURNING FROM linux_capture_scanner_images()')

    elif sg.running_mac():

        print('CALLING mac_capture_scanner_images()')
        images_list = mac_capture_scanner_images(long_scan_id, camera_list, window)
        print('RETURNING FROM mac_capture_scanner_images()')
    else:
        logging.error("this software only runs on Linux and macOS")
        terminate(-1, "this software only runs on Linux and macOS")
    # now take and save one image for each camera in camera_list

    # note this uses a FUNCTION alias that hides the OS dependencies of macOS vs. Linux camera apps.
    print(f'images_list={images_list}')
    db_variable = "status"
    status_value = "scanning complete"

    print(f'CALLING update_scan_record()')
    return_value = update_scan_record(long_scan_id, db_variable, status_value)
    print(f'RETURNING FROM update_scan_record()')

    # print(f' update_scan_record return_value = {return_value}')
    # find out how many images were captured / saved
    images_actually_written_list = glob.glob(os.path.join(scan_dir, 'SonaCam*.jpg'))
    number_of_scanner_images_captured = len(images_actually_written_list)
    updated_scan_data = scan_data
    ################################################################################################################
    #          WE NOW HAVE A LIST OF IMAGES IN A SCAN_DIR DIRECTORY                                                #
    ################################################################################################################

    minimum_images_for_a_good_scan_model = 12

    if number_of_scanner_images_captured < minimum_images_for_a_good_scan_model:  # minimum number of camera images
        ################################################################################################################
        #          IF THERE ARE NO IMAGES, OR NOT ENOUGH IMAGES WE WILL GO INTO DEMO MODE INSTEAD                      #
        ################################################################################################################
        print(f'number_of_scanner_images_captured = {number_of_scanner_images_captured}')
        print('THIS IS NOT ENOUGH IMAGES, WE WILL USE A DEMO SET OF IMAGES INSTEAD')
        print(f'CALLING demo()')
        updated_scan_data = demo(scan_data)
        print(f'RETURNING FROM scan()')
        sorted_images_list = scan_data['images_list']

        return_value_1 = update_scan_record(long_scan_id, 'status', 'Failed -> DEMO')
        print(return_value_1)
        scan_price = 0.00  # Don't charge for FAILED scans!
        return_value_2 = update_scan_record(long_scan_id, 'scan_price', scan_price)
        print(return_value_2)
        total_price = scan_price + cad_price + mfg_price + shipping_price
        return_value_3 = update_scan_record(long_scan_id, 'total_price', total_price)
        print(return_value_3)

        print(f'UPDATED SCAN_DATA= {updated_scan_data}')
        # if we are in demo mode there isn't any more processing, and so we return for next scan

        if not updated_scan_data['Simulate uploading']:
            window.write_event_value('_UPLOAD_IMAGES_', updated_scan_data)

        print(f'EXITING 1: scan({updated_scan_data})\n')
        return updated_scan_data

    ################################################################################################################
    #          THERE ARE ENOUGH IMAGES! SO WE WILL USE THIS SCAN LIST                                              #
    ################################################################################################################
    image_capture_toc = time.perf_counter()
    scan_duration = image_capture_toc - image_capture_tic
    print(f"captured {number_of_scanner_images_captured} images in: {scan_duration:0.0f} seconds, from {scanner_id}.")

    logging.info("captured {} images in {} seconds, from {}.".format(number_of_scanner_images_captured,
                                                                     scan_duration, scanner_id))
    window['_ACTION_STATUS_LINE_1_'].update("Scanning Completed.")
    window['_ACTION_STATUS_LINE_2_'].update(
        f"{number_of_scanner_images_captured} images in {scan_duration:0.0f} seconds, from {long_scan_id}.")
    thumbnail = convert_to_bytes(os.path.join(images_dir, "status-ready.png"))
    window['_IMAGE_ELEMENT_'].update(data=thumbnail)
    window['_PROGRESS_BAR_'].update(0)
    window['_SCAN_BUTTON_'].update(image_filename=scan_button)
    scan_disabled_state = False
    window.Refresh()

    # NOW START UPLOADING!!!
    ################################################################################################################
    #          LETS UPLOAD THE SCAN IMAGES NOW                                                                     #
    ################################################################################################################
    updated_scan_data['images_list'] = images_actually_written_list
    # window.write_event_value('_UPLOAD_IMAGES_', scan_data)
    window['_ACTION_STATUS_LINE_1_'].update("Ready for next scan.")
    window.Refresh()
    upload_images(scan_data)

    xml = dict2xml(scan_job_data_record, wrap='SonaScan', indent="   ")
    # xml_decode = xml.decode()

    manifest_xml_file = os.path.join(scan_dir, 'manifest.xml')
    xmlfile = open(manifest_xml_file, "w")
    xmlfile.write(xml)
    xmlfile.close()

    print(f'EXITING 2: scan({scan_data})\n')
    return scan_data


if __name__ == '__main__':
    scan('test data')
