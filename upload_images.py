# !/usr/bin/python

import os.path
import re
import webbrowser
from math import ceil

import requests
import subprocess
import sys
import time
import zipfile

from contextlib import contextmanager
from glob import glob
from gtts import gTTS
from playsound import playsound
from requests_toolbelt import MultipartEncoder

from GUI_defs import images_dir
from create_gcp_file import write_gcp_xml_file
from crop_obj import max_x, max_y, max_z, min_x, min_y, min_z, obj_3d_crop
from image_processing import convert_to_bytes
from rsync_with_sonaserver import rsync_to_server, list_files_in_a_sonaserver_directory
# from scandir_index_maker import scandir_index_maker
from scandir_index_maker import scandir_index_maker
from sonascan_file_paths import scans_dir
from do_obj_download import do_convert_obj_to_stl

SOUNDS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sounds'))


###################################################################################################################
#        get_forge_token() returns an authentication token for processing scans on Autodesk Forge
###################################################################################################################
def get_forge_token():
    tic = time.perf_counter()
    url = 'https://developer.api.autodesk.com/authentication/v1/authenticate'
    data = {
        'client_id': 'HAqDtKO7VbuRgH0nL0MFJ0B02ElBEK3l',
        'client_secret': 'oHihWQG1XJ1G9aNV',  # UNIQUE TO SONAUTICS
        'grant_type': 'client_credentials',
        'scope': 'data:read data:write'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, data=data, headers=headers)
    content = eval(r.content)

    if 200 != r.status_code:
        print(r.status_code)
        print(r.headers['content-type'])
        print(type(r.content))
        print(content)
        # -- example results --
        # 200
        # application/json
        # {"token_type":"Bearer","expires_in":1799,"access_token":"ESzsFt7OZ90tSUBGh6JrPoBjpdEp"}
        print("Authentication returned status code %s." % r.status_code)
        # raise SystemExit(6)
        toc = time.perf_counter()
        print(f"No Forge token received - in: {toc - tic:0.0f} seconds")
        print("ERROR 13: EXITING get_token() without a token")
        sys.exit(13)
    else:
        access_token = content['access_token']
        return access_token


###################################################################################################################
# is_this_a_valid_email(email) is a function for validating a user entered Email address
###################################################################################################################
def is_this_a_valid_email(email):
    # Make a regular expression for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        # print(f"Valid Email: {email}")
        return True
    else:
        # print(f"Invalid Email: {email}")
        return False


###################################################################################################################
# play_sound(event_name) enables assigning a sound to various events, so that user can monitor long processes
# auditorily, instead of watching screen
###################################################################################################################
def play_sound(event_name):
    sounds = {
        'STARTING': 'miata1.wav',
        'IMAGE_UPLOAD': 'click.wav',
        'FAILED_UPLOAD': 'Ricochet.wav',
        'GCP_UPLOAD': 'BOING6.WAV',
        'GCP_UPLOAD_FAILED': 'cartoon sound 4.wav',
        'ERROR': 'freeze.wav',
        'GET_PHOTOSCENE': 'machine_on.wav',
        'DOWNLOAD_OBJ': 'zoomin.wav',
        'DOWNLOAD_SUCCESS': 'zoomout.wav',
        'UNZIP': 'ZIP-2.WAV',
        'WARNING': 'Boing-spring-01.wav',
        'WAITING': 'Snore.mp3',
        'POLLING': 'msonarsub.wav',
        'SUCCESS': 'successtrumpet.mp3',
        'FAILED': 'foghorn_02.wav',
        'COMPLETE': 'smw_gameover.wav'
    }
    sound_file = os.path.join(SOUNDS_DIR, sounds[event_name])
    playsound(sound_file)
    return


###################################################################################################################
# text_to_speech(msg_to_speak) enables speaking various messages aloud,
# so that user can monitor long processes auditorily, instead of watching screen.
##################################################################################################################
def text_to_speech(msg_to_speak):
    speech = gTTS(text=msg_to_speak)
    speech.save('text_to_speech.mp3')
    playsound('text_to_speech.mp3')
    os.remove('text_to_speech.mp3')
    return


###################################################################################################################
#        cd(new_dir) enables changing directory a process is running in.
###################################################################################################################
@contextmanager
def cd(new_dir):
    prev_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)


###################################################################################################################
#        UNPACK AND PROCESS COMMAND LINE ARGUMENTS
###################################################################################################################

def upload_images(scan_data_dictionary):

    print(f'\nENTERING: upload_images({scan_data_dictionary})')

    input_folder_path = scan_data_dictionary['scan_dir']
    window = scan_data_dictionary['window']
    scan_id = scan_data_dictionary['scan_id']
    scanner_id = scan_data_dictionary['scanner_id']

    window['_ACTION_STATUS_LINE_2_'].update("Fill in details and click SCAN to start a new Scan")
    thumbnail = convert_to_bytes(os.path.join(images_dir, "status-ready.png"))
    window['_IMAGE_ELEMENT_'].update(data=thumbnail)
    window['_ACTION_STATUS_LINE_3_'].update(f"Now Uploading Scan {scanner_id}/{scan_id}.")
    window['_UPLOADING_PROGRESS_BAR_'].update(100 * 1 / 20)
    window.Refresh()

    from_email = scan_data_dictionary['_SENDER_']
    to_email = scan_data_dictionary['_RECIPIENT_']

    images_list = scan_data_dictionary['images_list']
    print('upload_images()', images_list)
    print('scan_data:', scan_data_dictionary)

    # initialize options handling variables
    notify_email = from_email + ', ' + to_email

    verbose_mode = False
    sound_mode = False
    do_not_display_model_after_download = False

    ###################################################################################################################
    #  VALIDATE THE INPUT FOLDER IS A READABLE DIRECTORY CONTAINING JPGs
    ###################################################################################################################

    if input_folder_path == '':
        print(f"ERROR 3: <input_folder_path> was not specified")
        if sound_mode:
            play_sound('ERROR')
        sys.exit(3)

    print(f"scans_dir={scans_dir}, input_folder_path={input_folder_path}")
    abs_path = os.path.join(scans_dir, input_folder_path)
    if not os.path.exists(abs_path):
        print(f"ERROR 4 : argument '{abs_path}' must be an existing readable directory containing JPG scan images")
        sys.exit(4)
    if not os.path.isdir(abs_path):
        print(f"ERROR 5: argument '{abs_path}' must be a readable directory containing JPG scan images")
        sys.exit(5)

    ###################################################################################################################
    # CREATE A GROUND CONTROL POINTS (GCP) FILE FROM THE SET OF IMAGES
    ###################################################################################################################
    print(f'Reading images in "{abs_path}".')
    gcp_file_path = os.path.join(abs_path, 'gcp.xml')

    if verbose_mode:
        print("creating GCP file")

    print(f'scan_data 2: {scan_data_dictionary}')
    print('write_gcp_xml_file()')
    write_gcp_xml_file(gcp_file_path, abs_path)
    window['_ACTION_STATUS_LINE_3_'].update(f"created GCP file {scanner_id}/{scan_id}.")
    window['_UPLOADING_PROGRESS_BAR_'].update(100 * 1 / 20)
    window.Refresh()

    print(f'scan_data 3: {scan_data_dictionary}')
    if verbose_mode:
        print("attaching GCP file")

    ###################################################################################################################
    # CREATE AN INDEX.HTML FOR THE SCAN_DIR
    ###################################################################################################################
    print(f'scan_data 3: {scan_data_dictionary}')
    scandir_index_maker(scan_data_dictionary)
    window['_ACTION_STATUS_LINE_3_'].update(f"created Index file {scanner_id}/{scan_id}.")
    window['_UPLOADING_PROGRESS_BAR_'].update(100 * 2 / 20)
    window.Refresh()

    if sound_mode:
        play_sound('STARTING')

    ###################################################################################################################
    # RSYNC THE SCAN_DIR TO SONASERVER
    ###################################################################################################################
    dst_dir = os.path.join('scansteruser@cloud1.tri-di.com:cloud1.tri-di.com/data/scans/', scanner_id, scan_id)
    long_scan_id = os.path.join(scanner_id, scan_id)
    remote_directory = os.path.join('/home/scansteruser/cloud1.tri-di.com/data/scans', scanner_id)
    window['_UPLOADING_PROGRESS_BAR_'].update(100 * 3 / 18)
    window['_ACTION_STATUS_LINE_3_'].update(f"Uploading to SonaServer {scanner_id}/{scan_id}.")
    window.refresh()
    rsync_to_server(abs_path, dst_dir, long_scan_id)
    list_files_in_a_sonaserver_directory(remote_directory)
    print(f'files in scan_dir on sonaserver = {list_files_in_a_sonaserver_directory(remote_directory)}')

    if scan_data_dictionary['Show images html']:
        print(f'Show images html = {scan_data_dictionary["scan_dir"]}')
        print(scan_data_dictionary)

        scanner_id = scan_data_dictionary['scanner_id']
        scan_id = scan_data_dictionary['scan_id']
        url_to_show = f'http://cloud1.tri-di.com/data/scans/{scanner_id}/{scan_id}/index.html'
        webbrowser.open(url_to_show)

    ###################################################################################################################
    # GO TO INPUT DIRECTORY, FIND ALL JPGS, AND PUT THEM IN A LIST AND ATTACH THESE FILES TO AUTODESK FOR PROCESSING
    ###################################################################################################################

    # AND ATTACH THESE FILES TO AUTODESK FOR PROCESSING
    print(f'abs_path={abs_path}')
    with cd(abs_path):
        list_of_jpgs = glob('*.jpg')
        list_of_jpgs.extend(glob('*.JPG'))
        list_of_jpgs.extend(glob('*.jpeg'))
        list_of_jpgs.extend(glob('*.JPEG'))

        if len(list_of_jpgs) == 0:
            print(f"ERROR 6: No .jpg, .JPG, .jpeg, and .JPEG files in {abs_path}")
            sys.exit(6)

        if verbose_mode:
            print(f"\n{len(list_of_jpgs)} JPGs found in '{abs_path}':")
            print('#  \tfilename              \t\tsize')
            print('-- \t----------------------\t\t----------')

        k = 0  # initialize file counter
        exceeded_size_limit = False
        for file_path in sorted(list_of_jpgs):
            # User can control order of submission of images to Autodesk by assigning file names alphabetically
            file_name = os.path.basename(file_path)
            if file_name in glob('result*.jpg'):
                print(f"WARNING: {file_name} appears to be part of an OBJ model, and will be ignored.")
                list_of_jpgs.remove(file_name)
            else:
                file_size = os.path.getsize(file_path)
                file_size_in_mb = file_size / (1024 * 1024)
                if file_size_in_mb > 128:
                    size_warning = "exceeds 128 MB"
                    exceeded_size_limit = True
                    print(f'{k}:\t{file_name}\t\t{file_size}\t{size_warning}')
                else:
                    size_warning = ""
                    if verbose_mode:
                        print(f'{k}:\t{file_name}\t\t{file_size}\t{size_warning}')
                k = k + 1  # increment file counter

        if exceeded_size_limit:
            if verbose_mode:
                print('WARNING: image files exceeding 128 MB may be rejected for modeling.')
            if sound_mode:
                play_sound('WARNING')
        if sound_mode:
            text_to_speech(f'{k} image files found in input folder')

        ################################################################################################################
        #
        #       SUBMIT THE JPGS IN THE INPUT FOLDER TO AUTODESK FORGE TO CREATE A 3D MODEL
        #
        ################################################################################################################

        ################################################################################################################
        # STEP 1: REQUEST A NEW photoscene_id FROM AUTODESK FORGE
        ################################################################################################################

        client_secret = 'oHihWQG1XJ1G9aNV'
        access_token = get_forge_token()

        forge_url = 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/'
        headers = {'Content-Type': 'text/xml', 'Authorization': 'Bearer ' + access_token}
        if notify_email == '':
            data = {
                'client_secret': client_secret,
                'scenename': input_folder_path,
                'scenetype': 'object',
                'format': 'obj'
            }
        else:
            data = {
                'callback': notify_email,
                'client_secret': client_secret,
                'scenename': input_folder_path,
                'scenetype': 'object',
                'format': 'obj'
            }

        #  POST THE REQUEST TO AUTODESK FORGE API
        api_response = requests.post(forge_url, data=data, headers=headers)
        response_object = eval(api_response.content)

        try:  # RETRIEVE RESULTS OBJECT IF NO ERRORS
            photoscene_object = response_object['Photoscene']
            photoscene_id = photoscene_object['photosceneid']
            if sound_mode:
                text_to_speech('Photo scene assigned.')
                # play_sound('GET_PHOTOSCENE')

        except KeyError:  # RETRIEVE ERRORS MSGS IF THERE ARE ERRORS
            print(f"ERROR: Photoscene {photoscene_id} not returned")
            try:
                response_error = response_object['Error']
                error_msg = response_error['msg']
                error_code = response_error['code']
                print(f'Error {error_code}: {error_msg}')
            except KeyError:
                print("ERROR 8: Request for new Photoscene failed without a message.")
            if sound_mode:
                play_sound('ERROR')
            sys.exit(8)

        ################################################################################################################
        # STEP 2: ATTACH EACH JPG TO PHOTOSCENE ON AUTODESK FORGE
        ################################################################################################################
        forge_url = 'https://developer.api.autodesk.com/photo-to-3d/v1/file'

        i = 0  # initialize file counter
        if verbose_mode:
            print()
            print('Uploading JPG files:')
            print('file #   \tFilename        	     \tSize   \tStatus')
            print('---------\t---------------------- \t-------\t----------')
        if sound_mode:
            text_to_speech(f'Uploading {k} images.')

        for file_name in list_of_jpgs:
            payload = MultipartEncoder(fields={'photosceneid': photoscene_id,
                                               'type': 'image',
                                               'file[0]': (file_name, open(file_name, 'rb'), 'image/jpg')})
            headers = {'Content-Type': payload.content_type, 'Authorization': 'Bearer ' + access_token}

            #  POST THE REQUEST TO AUTODESK FORGE API
            api_response = requests.post(forge_url, headers=headers, data=payload)
            response_object = eval(api_response.content)

            try:  # RETRIEVE RESULTS OBJECT IF NO ERRORS
                photoscene_id = response_object['photosceneid']
                files_items = response_object['Files']
                file_tuple = files_items['file']
                filename = file_tuple['filename']
                filesize = file_tuple['filesize']
                msg = file_tuple['msg']

                if verbose_mode:
                    print(f'file[{i}]:\t{filename}\t{filesize}\t{msg}')
                if sound_mode:
                    play_sound('IMAGE_UPLOAD')

            except KeyError:  # RETRIEVE ERRORS MSGS IF THERE ARE ERRORS
                print(f'WARNING: attaching {file_name} to photoscene_object {photoscene_id} failed.')
                try:
                    response_error = response_object['Error']
                    error_msg = response_error['msg']
                    error_code = response_error['code']
                    print(f'Error {error_code}: {error_msg}')
                    if sound_mode:
                        play_sound('FAILED_UPLOAD')
                except KeyError:
                    print(f"ERROR 8: Request to attach {file_name} to")
                    print(f"photoscene_object {photoscene_id} failed without a message.")
                    if sound_mode:
                        play_sound('ERROR')
                    sys.exit(8)
            window['_UPLOADING_PROGRESS_BAR_'].update(100 * i / len(list_of_jpgs))
            window['_ACTION_STATUS_LINE_3_'].update(f"Attached {file_name} to {scanner_id}/{scan_id}.")
            window.refresh()
            i = i + 1
        print(f"\n{i} images were attached to {photoscene_id}.")

        ################################################################################################################
        # STEP 3B: ATTACH A GROUND CONTROL POINTS FILE
        ###############################################################################################################
        payload = MultipartEncoder(fields={'photosceneid': photoscene_id,
                                           'type': 'survey',
                                           'file[0]': (gcp_file_path, open(gcp_file_path, 'rb'), 'UTF-8')})
        headers = {'Content-Type': payload.content_type, 'Authorization': 'Bearer ' + access_token}

        #  POST THE REQUEST TO AUTODESK FORGE API
        api_response = requests.post(forge_url, headers=headers, data=payload)
        response_object = eval(api_response.content)

        try:  # RETRIEVE RESULTS OBJECT IF NO ERRORS
            photoscene_id = response_object['photosceneid']
            files_items = response_object['Files']
            file_tuple = files_items['file']
            filename = file_tuple['filename']
            filesize = file_tuple['filesize']
            msg = file_tuple['msg']

            if verbose_mode:
                print(f'file[{i}]:\t{filename}\t{filesize}\t{msg}')
            if sound_mode:
                text_to_speech('Control Points File successfully attached.')
                play_sound('GCP_UPLOAD')

        except KeyError:  # RETRIEVE ERRORS MSGS IF THERE ARE ERRORS
            print(f'WARNING: attaching GCP file, {file_name}, to photoscene_object {photoscene_id} failed.')
            try:
                response_error = response_object['Error']
                error_msg = response_error['msg']
                error_code = response_error['code']
                print(f'Error {error_code}: {error_msg}')
                if sound_mode:
                    play_sound('GCP_FAILED_UPLOAD')
            except KeyError:
                print(f"ERROR 8: Request to attach GCP file, {file_name}, to")
                print(f"photoscene_object {photoscene_id} failed without a message.")
                if sound_mode:
                    play_sound('ERROR')
                sys.exit(8)

        ################################################################################################################
        # STEP 3: START PROCESSING THE PHOTOSCENE ON AUTODESK FORGE
        ################################################################################################################
        forge_url = f'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/{photoscene_id}'
        headers = {'Content-Type': 'text/xml', 'Authorization': 'Bearer ' + access_token}
        window['_UPLOADING_PROGRESS_BAR_'].update(0)
        window['_ACTION_STATUS_LINE_3_'].update(f"Uploaded {scanner_id}/{scan_id}.")
        window.refresh()
        #  POST THE REQUEST TO AUTODESK FORGE API
        api_response = requests.post(forge_url, data=data, headers=headers)
        response_object = eval(api_response.content)

        try:  # RETRIEVE RESULTS OBJECT IF NO ERRORS
            photoscene_object = response_object['Photoscene']
            launched_photoscene_id = photoscene_object['photosceneid']
        except KeyError:  # RETRIEVE ERRORS MSGS IF THERE ARE ERRORS
            print(f"ERROR: Photoscene {launched_photoscene_id} not started")
            try:
                response_error = response_object['Error']
                error_msg = response_error['msg']
                error_code = response_error['code']
                print(f'Error {error_code}: {error_msg}')
            except KeyError:
                print(f"ERROR 9: Request to start Photoscene {launched_photoscene_id} failed without a message.")
            if sound_mode:
                play_sound('ERROR')
            sys.exit(9)

        if launched_photoscene_id == '':
            print(f"ERROR: during Modeling {launched_photoscene_id}: Error code {error_code}: {error_msg}")
            if sound_mode:
                play_sound('ERROR')
            sys.exit(9)

        if verbose_mode:
            print(f"\nBeginning Modeling...This may take a while...")

        ################################################################################################################
        # STEP 4: POLL AUTODESK FORGE FOR PROGRESS UPDATES
        ################################################################################################################
        forge_url = f'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/{photoscene_id}/progress'
        headers = {'Authorization': 'Bearer ' + access_token}

        window['_MODELING_PROGRESS_BAR_'].update(0)
        window['_ACTION_STATUS_LINE_3_'].update(f"Beginning Modeling: {scanner_id}/{scan_id}.")
        window.refresh()
        progress_msg = "Created"
        previous_progress = "0"
        tic = time.perf_counter()
        waiting_sound = 'WAITING'
        if sound_mode:
            text_to_speech('Waiting for the Server to respond.')
        if verbose_mode:
            print('Waiting for the Server to respond.\n')
            print('time:\tStatus    \t  % ')
            print('-----\t----------\t----')

        while progress_msg != "DONE" and progress_msg != "ERROR":
            #  POST THE REQUEST TO AUTODESK FORGE API
            api_response = requests.get(forge_url, headers=headers)
            response_object = eval(api_response.content)
            toc = time.perf_counter()
            elapsed_time = int(toc - tic)

            try:  # RETRIEVE RESULTS OBJECT IF NO ERRORS
                photoscene_object = response_object['Photoscene']
                modelling_photoscene_id = photoscene_object['photosceneid']
                progress_msg = photoscene_object['progressmsg']
                progress = photoscene_object['progress']

                if progress_msg == 'Processing':
                    if waiting_sound == 'WAITING':
                        waiting_sound = 'POLLING'
                        if sound_mode:
                            text_to_speech('Server is now processing the model')
                        if verbose_mode:
                            print('\nServer is beginning modeling process. Please be patient...')
                if verbose_mode:
                    print(f'{elapsed_time}s:  \t{progress_msg}    \t{progress}'+'%')
                progress_percentage = int(progress)
                print(progress_percentage)
                window['_MODELING_PROGRESS_BAR_'].update(progress_percentage)
                window['_ACTION_STATUS_LINE_3_'].update(
                    f"Modeling: {scanner_id}/{scan_id}, {progress}% complete. {progress_msg}.")
                window.refresh()

            except KeyError:  # RETRIEVE ERRORS MSGS IF THERE ARE ERRORS
                print(f"ERROR 10: Photoscene {modelling_photoscene_id} failed")
                try:
                    response_error = response_object['Error']
                    error_msg = response_error['msg']
                    error_code = response_error['code']
                    print(f'Error {error_code}: {error_msg}')
                except KeyError:
                    print(f"ERROR 10: Polling of Photoscene {modelling_photoscene_id} failed without a message.")
                if sound_mode:
                    play_sound('ERROR')
                sys.exit(10)
            if int(progress) < 100:
                if sound_mode:
                    if previous_progress < progress:
                        text_to_speech(f'{progress} percent complete')
                    play_sound(waiting_sound)
                else:
                    time.sleep(10)
            previous_progress = progress

        if progress_msg == "ERROR":
            print("ERROR: No model produced with the attached images")
            if sound_mode:
                play_sound('ERROR')
            sys.exit(11)

        ################################################################################################################
        # STEP 5: WHEN MODELING IS COMPLETE, GET THE SCENE_LINK OBJ.ZIP FILE AUTODESK FORGE CREATED
        ################################################################################################################
        if sound_mode:
            play_sound('SUCCESS')
        if verbose_mode:
            print()

        forge_url = f'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/{photoscene_id}?format=obj'
        headers = {'Authorization': 'Bearer ' + access_token}
        data = {'format': 'obj'}

        window['_MODELING_PROGRESS_BAR_'].update(0)
        window['_ACTION_STATUS_LINE_3_'].update(
            f"Modeling: {scanner_id}/{scan_id}, complete. Inspecting OBJ model.")
        window.refresh()

        #  POST THE REQUEST TO AUTODESK FORGE API TO GET AN OBJ FILE
        if sound_mode:
            text_to_speech('Modeling Complete. Downloading the OBJ files.')

        api_response = requests.get(forge_url, headers=headers, data=data)
        response_object = eval(api_response.content)
        json_object = api_response.json()
        # json_string = json.dumps(json_object)

        try:
            obj_file = json_object['Photoscene']['filename']
            obj_file_size = json_object['Photoscene']['filesize']
            result_message = json_object['Photoscene']['resultmsg']
            scene_link = json_object['Photoscene']['scenelink']
            completed_photoscene_id = json_object['Photoscene']['photosceneid']
            progress_msg = json_object['Photoscene']['progressmsg']
            progress = json_object['Photoscene']['progress']
            if verbose_mode:
                # print(json_string)
                print(f'{obj_file}\t{obj_file_size}\t{completed_photoscene_id}\t' +
                      f'{progress_msg}\t{progress}\t{result_message}')
                print(scene_link+'\n')

        except KeyError:  # RETRIEVE ERRORS MSGS IF THERE ARE ERRORS
            print(f"ERROR: Photoscene {modelling_photoscene_id} failed")
            try:
                response_error = response_object['Error']
                error_msg = response_error['msg']
                error_code = response_error['code']
                print(f'Error {error_code}: {error_msg}')
            except KeyError:
                print(f"ERROR 11: Modeling of Photoscene {modelling_photoscene_id} failed without a message.")
                if sound_mode:
                    play_sound('FAILED')
                sys.exit(11)

        #######################################################################################################
        # If scenelink file was created, download OBJ.zip
        #######################################################################################################

        obj_zip = os.path.join(abs_path, "model.obj.zip")
        if verbose_mode:
            print(f'obj.zip={obj_zip}')

        #  POST THE REQUEST TO AUTODESK FORGE API
        api_response = requests.get(scene_link, stream=True)

        window['_ACTION_STATUS_LINE_3_'].update(
            f"Modeling: {scanner_id}/{scan_id} - Retrieving OBJ model.")
        window.refresh()
        obj_file_size_in_mb = ceil(int(obj_file_size) / (1024 * 1024))
        number_of_mb_downloaded = 0
        try:
            with open(obj_zip, 'wb') as fd:
                for chunk in api_response.iter_content(chunk_size=1024 * 1024):
                    fd.write(chunk)
                    number_of_mb_downloaded = number_of_mb_downloaded + 1
                    if sound_mode:
                        play_sound('DOWNLOAD_OBJ')
                    if verbose_mode:
                        print(f'{number_of_mb_downloaded} of of {obj_file_size_in_mb:} MB Downloaded.')
                fd.close()

        except (IOError, OSError, FileNotFoundError, PermissionError):
            print(f'ERROR 13: Unable to download Scene_Link to {abs_path}')
            if sound_mode:
                play_sound('ERROR')
            sys.exit(13)

        try:
            if os.path.exists(obj_zip):
                with zipfile.ZipFile(obj_zip, 'r') as zip_ref:
                    zip_ref.extractall(abs_path)
                    zipfile_members = zip_ref.infolist()
                if sound_mode:
                    play_sound('DOWNLOAD_OBJ')
                if verbose_mode:
                    print(f'extracted {len(zipfile_members)} files from {obj_zip}')
                    print(zipfile_members)
            else:
                print(f"ERROR 12: Unable to unzip results file.")
                if sound_mode:
                    play_sound('FAILED')
                sys.exit(12)

        except (IOError, OSError, FileNotFoundError, PermissionError):
            print(f"ERROR 14: Unable to unzip results file.")
            if sound_mode:
                play_sound('FAILED')
            sys.exit(12)

        #  FUTURE ENHANCEMENT???   CROP OBJ FILE AND USE meshconv TO CREATE AN STL,

        ################################################################################################################
        #  DOWNLOAD OF OBJ FILES IS SUCCESSFUL
        ################################################################################################################
        obj_file = os.path.join(abs_path, 'result.obj')
        if not os.path.exists(obj_file):
            print(f'ERROR 18: {obj_file} does not exist.')
            if sound_mode:
                play_sound('FAILED')
            sys.exit(18)

        if sound_mode:
            play_sound('DOWNLOAD_SUCCESS')

        ################################################################################################################
        #  CROP THE OBJ FILE
        ################################################################################################################

        cropped_obj_file = os.path.join(abs_path, 'cropped-result.obj')
        obj_3d_crop(max_x, max_y, max_z, min_x, min_y, min_z, obj_file, cropped_obj_file)

        ################################################################################################################
        #  CONVERT THE CROPPED OBJ FILE TO AN STL FILE
        ################################################################################################################
        do_convert_obj_to_stl(cropped_obj_file, photoscene_id, window, scan_data_dictionary)
        cropped_stl_file = os.path.join(abs_path, 'cropped-result.stl')
        print(f"\n{i} STL file read from {abs_path}.\n3D Model is at {cropped_stl_file}.\n")
        window['_ACTION_STATUS_LINE_3_'].update(
            f"3D Model is at {cropped_stl_file}.")
        window.refresh()

        ################################################################################################################
        #  OPEN OBJ IN MESHLAB TO VIEW RESULT
        ################################################################################################################
        if do_not_display_model_after_download:
            return

        if sys.platform == 'linux':
            path_to_meshlab = "/usr/bin/meshlab"
        elif sys.platform == 'darwin':
            path_to_meshlab = '/Applications/meshlab.app/Contents/MacOS/meshlab'
        else:
            print('ERROR 16: Unsupported OS, can not start meshlab')
            sys.exit(16)

        response = ''
        try:
            shell_command = [path_to_meshlab, cropped_stl_file]
            response = subprocess.Popen(shell_command, universal_newlines=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"ERROR 15:: {e} meshlab failed to open {cropped_stl_file}")
            print(response)
            sys.exit(15)

        if sound_mode:
            text_to_speech('All done!')
            play_sound('COMPLETE')
        return


if __name__ == '__main__':

    image_file_dir = '/sonautics/data/scans/DEMO'
    test_from_email = 'devops@sonautics.com'
    test_to_email = 'devops@sonautics.com'
    scan_data = {'scan_dir': image_file_dir,
                 '_SENDER_': test_from_email,
                 '_RECIPIENT_': test_from_email,
                 'scan_id': "DEMO",
                 'scanner_id': "DEMO",
                 'images_list': {}
                 }

    upload_images(scan_data)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


if __name__ == '__main__':
    upload_images('test data')
