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
        camera_did_not_return_image  - Camera was recognized but did not return image before timeout (may be due busy USB bus?)
        os_not_supported - the controller device is reporting an OS version we don't have code for
 
Usage: How this class, method, or function is accessed / called.

    E.g.
    >>> <ThisClass>.get_jpgs_from_all_cameras(
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

    E.g.
        This function actually iterates over all cameras, using get_an_image (camera_name, jpg_file_path) 
 
TO DO:   Any additional work that needs to be done.

    E.g.
        None
"""
