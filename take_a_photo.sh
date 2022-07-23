#!/bin/bash

# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
#
# file:  take_a_photo.sh
# Purpose: sets camera properties to desired values before capturing images (LINUX specific)
# Parameters:   camera_id=$1
#               full_image_file_name=$2
# Returns: None
# Description: sets camera properties to desired values before capturing images (LINUX specific)
# Raises: none
# Usage: take_a_photo.sh camera_id full_image_file_name
# Dependencies:
#   v4l2-ctl -- function to get and set camera parameters
#   ffmpeg -- function used to capture images
# Inheritance:    None
# Testing:
#       Test for: v4l2  not installed
# Warnings: This is Linux Specific code.
# Updates: Scott McGregor,  modified 22-Nov-2021, added header doc
# Notes:  Anything else that developers should know about this code.
# TO DO:  None

camera_id=$1
full_image_file_name=$2

# cam_props = {'brightness': 128, 'contrast': 128, 'saturation': 180,
#              # 'gain': 0,
#              'sharpness': 128, 'exposure_auto': 1,
#              'exposure_absolute': 150, 'exposure_auto_priority': 0,
#              # 'focus_auto': 0,
#              # 'focus_absolute': 30,
#              # 'zoom_absolute': 250,
#              'white_balance_temperature_auto': 0, 'white_balance_temperature': 3300}

v4l2-ctl -d $camera_id -c brightness=64
v4l2-ctl -d $camera_id -c contrast=100
v4l2-ctl -d $camera_id -c saturation=66
v4l2-ctl -d $camera_id -c hue=0
v4l2-ctl -d $camera_id -c white_balance_temperature_auto=0
v4l2-ctl -d $camera_id -c gamma=500
v4l2-ctl -d $camera_id -c white_balance_temperature=4600
v4l2-ctl -d $camera_id -c sharpness=66
v4l2-ctl -d $camera_id -c backlight_compensation=1
v4l2-ctl -d $camera_id -c exposure_auto=1
v4l2-ctl -d $camera_id -c exposure_absolute=233
v4l2-ctl -d $camera_id -c exposure_auto_priority=0

# ffmpeg -hide_banner -f video4linux2 -s 1920x1080 -i /dev/video2 -ss 0:0:2 -frames 1 /tmp/full_image_file_name
# ffmpeg -y -hide_banner  -f video4linux2 -input_format mjpeg   -framerate 30 -i $camera_id -ss 0:0:2 -frames 1 -f image2 $full_image_file_name
# v4l2-ctl -d $camera_id --stream-mmap --stream-count=1 --stream-to=- | convert - $full_image_file_name &
v4l2-ctl -d $camera_id --stream-mmap --stream-count=1 --stream-to=$full_image_file_name &