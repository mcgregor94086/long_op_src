# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
module, file, class, method, function or section:
    Specify the TYPE of object being documented (Required by NaturalDocs)
    E.g.
    method: get_jpgs_from_all_cameras

Purpose:
    A one or two line synopsis/explanation of the function.
    E.g.
    Takes a dict of available cameras, and returns a dict of JPG images

Parameters: (Input) Names, types and descriptions of required parameters and globals used as input

    E.g.
    cameras_list (dict): Collection of data used in the test. Requires the following keys:
        - camera_number (int): Unique Camera Number
        - camera_name (str): USB Camera Name

Returns: (Output) Type and description of what is returned, or changed, by the function.

    E.g.
    jpg_files (dict): A dictionary with the camera names as the keys and the filename of the JPG image it took.
                      Requires the following keys:
         - camera_number (int): Unique Camera Number
         - jpg_file_path (str): absolute file path to image JPG file captured by corresponding Camera


Description: A detailed description of the function, including explanations of algorithms, intent, and any tricks.

    E.g.
    This method relies on the FFMPEG library to capture an image from each camera.
    Tricks: Note FFMPEG is OS-dependent,  and specifically the MAC OS X and Linux (Raspberry Pi) systems require
    require different parameters,  so we have to check the OS and use different branches for each.

Raises: Any errors, warnings or exceptions raised, and an explanation of what the exception means

    E.g.
        camera_not_recognized - the named USB camera was not recognized by FFMPEG.
        camera_did_not_return_image  - Camera was recognized but did not return image before timeout
        (may be due busy USB bus?)
        os_not_supported - the controller device is reporting an OS version we don't have code for

Usage: How this class, method, or function is accessed / called.

    E.g.
    <ThisClass>.get_jpgs_from_all_cameras(
        [
            {'camera_number': 0, 'camera_name': 'SonaCam'},
            {'camera_number': 1, 'camera_name': 'SonaCam 1'},
            ...
            {'camera_number': 23, 'camera_name': 'SonaCam 1'},
        ],
    )


Dependencies:  Any libraries, devices, etc. that must be present.

        E.g.
        FFMPEG library

Inheritance:    For classes, list what it inherits from here

Testing: Things to keep in mind while testing the program. Special cases to test for.

E.g.
    Test for NO camera found on USB bus, requested camera not present, camera does not respond (time out),
    zero length image file, image file is not a JPG, image file is not readable, image file not found.

Warnings: Anything that might be dangerous, or a source of bugs.

E.g.
    Note FFMPEG is OS-dependent, and specifically the MAC OS X and Linux (Raspberry Pi) systems require
    require different parameters,  so we have to check the OS and use different branches for each.


Updates: Document who modified the function, when, why and how.

    E.g.
        Scott McGregor,  modified 01-Jan-2021, Added check on how many cameras respond to detect USB not connected

Notes:  Anything else that developers should know about this code.

        autodesk_forge.py contains all the data needed to get autodesk forge tokens and
        run autodesk forge reality capture API jobs

TODO:   Something funny is happening that needs to be debugged further.  The paramiko and request standard libraries
        are not being imported when run from test_scan.py,  but they are when this module is tested separately!!!

scandir_index_maker(scan_dir)

scandir_index_maker(scan_dir) takes a scan_dir directory and
generates a pretty index.php page in HTML and places it in the scan_dir

Copyright (c) Sonautics, Inc 2020.
Author: Scott L. McGregor
"""

import os
from pathlib import Path

from sonascan_file_paths import SERVER_UPLOAD_DIR_ROOT_PATH

PREAMBLE1 = """ 
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>"""

PREAMBLE2 = """</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://cloud1.tri-di.com/css/bootstrap.css" rel="stylesheet" type="text/css" media="all" />
    <link href="http://cloud1.tri-di.com/css/interface-icons.css" rel="stylesheet" type="text/css" media="all" />
    <link href="http://cloud1.tri-di.com/css/theme.css" rel="stylesheet" type="text/css" media="all" />
    <link href="http://cloud1.tri-di.com/css/custom.css" rel="stylesheet" type="text/css" media="all" />
    <link href='https://fonts.googleapis.com/css?family=Lora:400,400italic,700|Montserrat:400,700' 
    rel='stylesheet' type='text/css' />
</head>
<body style="background-color:white">
    <div>
        <img src="http://cloud1.tri-di.com/images/logo-small.png"/>
        <h4 class="text-center">"""

PREAMBLE3 = """</h4>
    </div>
    <div>
        <section>
"""

POSTAMBLE = """     
        </section>
    </div>
    <script src="http://cloud1.tri-di.com/js/jquery-2.1.4.min.js"></script>
    <script src="http://cloud1.tri-di.com/js/isotope.min.js"></script>
    <script src="http://cloud1.tri-di.com/js/scrollreveal.min.js"></script>
    <script src="http://cloud1.tri-di.com/js/parallax.js"></script>
    <script src="http://cloud1.tri-di.com/js/scripts.js"></script>
</body>
</html>
"""


def scandir_index_maker(scan_data):
    print(f'\n\t\tENTERING scandir_index_maker({scan_data})')
    scan_dir_path = os.path.abspath(scan_data['scan_dir'])
    # print(f'CHECKPOINT 1: scandir_index_maker({scan_data})\n')
    full_scan_id = scan_data['long_scan_id']
    # print(f'CHECKPOINT 2: scandir_index_maker({scan_data})\n')
    index_file_name = "index.html"
    # print(f'CHECKPOINT 3: scandir_index_maker({scan_data})\n')
    index_file_path = os.path.join(scan_dir_path, index_file_name)
    # print(f'CHECKPOINT 4: scandir_index_maker({scan_data})\n')
    scandir_link = "<a href='" + SERVER_UPLOAD_DIR_ROOT_PATH + full_scan_id + "/index.html'>" + full_scan_id + "</a>"
    # print(f'CHECKPOINT 5: scandir_index_maker({scan_data})\n')
    with open(index_file_path, 'w') as f:
        # print(f'CHECKPOINT 6: scandir_index_maker({scan_data})\n')
        f.write(PREAMBLE1+full_scan_id+PREAMBLE2+scandir_link+PREAMBLE3)
        # print(f'CHECKPOINT 7: scandir_index_maker({scan_data})\n')

        for (root, dirs, files) in os.walk(scan_dir_path):
            # path = root.split(os.sep)
            for filename in sorted(files):
                if filename != "index.html" and filename != ".DS_Store":  # don't bother to create an entry
                    #                                                       because this file will be index.html
                    if filename[0] != '.':
                        f.write('            <div class ="col-md-3 col-sm-4 col-xs-6" >\n')
                        f.write('                <a href="' + filename + '">\n')
                        ext = Path(filename).suffix
                        if os.path.isdir(filename):
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/folder-icon.png" /><br />'
                                    + filename)
                        elif ext == '.jpg':
                            f.write('                <img height="150px" src="' + filename + '" /><br /><p>'
                                    + filename)
                        elif ext == '.xml':
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/xml_file_icon.png" /><br /><p>'
                                    + filename)
                        elif ext == '.zip':
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/zip_file_icon.png" /><br /><p>'
                                    + filename)
                        elif ext == '.obj':
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/obj_file_icon.png" /><br /><p>'
                                    + filename)
                        elif ext == '.mtl':
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/mtl_file_icon.png" /><br /><p>'
                                    + filename)
                        elif ext == '.stl':
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/stl_file_icon.png" /><br /><p>'
                                    + filename)
                        elif ext == '.html':
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/html_file_icon.png" /><br /><p>'
                                    + filename)
                            # TODO: Need elif's and icons for photoscene-folder, and other file types
                            # TODO: The Photoscene directory is not showing, but files inside it are. We should indicate
                            #       that these files are inside this directory, when laying out this page.
                            # TODO: The files in the Photoscene directory don't have the right URLs when you click.
                            # TODO: Result01.JPG is not showing an image

                        else:
                            f.write('                <img height = "150px" ' +
                                    'src="/sonautics/images/unknown_file_icon.png" /><br /><p>'
                                    + filename)
                        f.write('</p></a>\n')
                        f.write('            </div>\n')
        f.write(POSTAMBLE)
        # print(f'CHECKPOINT 8: scandir_index_maker({scan_data})\n')
    log = open(index_file_path, "r").read()
    print(f'\t\t{index_file_path} saved')
    # print (log)

    print(f'\t\tEXITING scandir_index_maker({scan_data})\n')
    return log


def main():
    the_scan_data = {}
    the_scan_data['long_scan_id'] = 'data/DEMO'
    the_scan_data['scan_dir'] = '/sonautics/data/DEMO'
    print(the_scan_data)
    scandir_index_maker(the_scan_data)


if __name__ == "__main__":
    # execute only if run as a script
    main()
