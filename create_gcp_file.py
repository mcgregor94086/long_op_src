__author__ = 'Scott McGregor'

import glob
import os
import sys

import cv2
import math

from astropy.coordinates import spherical_to_cartesian


#  This program produced a file like the one in example below for Autodesk.
#  It associates known 3D (x, y, z) positions of the colored markers on the floor,
#  with the  2D (h,w) positions where it appears on any image.


FLOOR_Z = -15
NUMBER_OF_GROUND_CONTROL_POINTS = 12
MARKERS_CIRCLE_RADIUS = 35
AZIMUTH_STEP_IN_RADIANS = math.pi / NUMBER_OF_GROUND_CONTROL_POINTS
AZIMUTH_STEP_IN_DEGREES = 360 / NUMBER_OF_GROUND_CONTROL_POINTS

ORANGE = (252, 175, 23),
EMERALD = (47, 181, 106),
PURPLE = (108, 63, 153),
GRASS = (133, 196, 65),
BLUE = (0, 174, 237),
MAGENTA = (198, 61, 150),

marker_color_pairs = {
    # id: (clock_number, color1, color2)
    '0':  ('12', MAGENTA, ORANGE),
    '1':  ('1', ORANGE, ORANGE),
    '2':  ('2', ORANGE, EMERALD),
    '3':  ('3', EMERALD, EMERALD),
    '4':  ('4', EMERALD, PURPLE),
    '5':  ('5', PURPLE, PURPLE),
    '6':  ('6', PURPLE, GRASS),
    '7':  ('7', GRASS, GRASS),
    '8':  ('8', GRASS, BLUE),
    '9':  ('9', BLUE, BLUE),
    '10': ('10', BLUE, MAGENTA),
    '11': ('11', MAGENTA, MAGENTA),
}


def rgb_to_hsv(image_rgb):
    image_hsv = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2HSV)
    return image_hsv


def define_marker_positions():  # return marker_dict: { 'marker_id': ('name', x, y, z), ... }
    marker_dict = {}
    elevation = 0
    r = MARKERS_CIRCLE_RADIUS
    # print("id:  \t(clock\t  x\t\t    y\t\t  z\t\t\t degrees\t\t radians)")
    # print("====:\t======\t======  \t======\t=======\t\t=========\t=========")
    for i in range(1, 13):
        marker_id = i
        marker_name = i
        if i == 12:
            marker_id = 0
        azimuth_in_radians = i * AZIMUTH_STEP_IN_RADIANS
        azimuth_in_degrees = i * AZIMUTH_STEP_IN_DEGREES
        x, y, z = spherical_to_cartesian(r, elevation, azimuth_in_radians)
        z = FLOOR_Z
        marker_dict[marker_name] = (marker_id, marker_name, x, y, z, azimuth_in_degrees, azimuth_in_radians)
        # print(f'{marker_id}:\t({marker_id},\t{marker_name},\t{x:.3f},  \t{y:.3f},\t{z:.3f}, '
        #      + f'\t{azimuth_in_degrees:.3f}º,  \t{azimuth_in_radians:.3f} rad")')
    # print()
    return marker_dict


def find_best_n_markers_in_image_file(image_file):
    markers_found_in_this_file = []
    # Theory of operation:
    # Step 1) Read an image file into opencv (cv2) image structures, ipl, and a gray scale version, src_gray:
    src_gray = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
    ipl = cv2.imread(image_file, 1)

    # Uncomment to see the cv2 image, useful for debugging)
    # cv2.imshow("Example", ipl)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Step 2) Convert an RGB image to an HSV image:
    # HSV will be useful to identify the TRUE colors of circular markers.  The colors allow us to distinguish
    # which marker is in which clock position (and therefore we know its absolute 3D x,y,z position).
    # Pixels might be in bright light, in shadow or in a reflected color of the impressions.
    # Such conditions change the Saturation (S) and the brightness Value (V) of the perceived pixel by a lot,
    # but are only likely to change the Hue (H) by a little. The RGB values will also all change a lot,
    # so using HSV allows us to just try to find the closest match in the Hue (H) space.

    hsv = rgb_to_hsv(ipl)

    # STEP 3: Edge Recognition of Colored Circles.
    # The following operations are used to identify, and emphasize black and white pixel boundaries (Edges).
    # Our circular color markers each have an outer black edge, with an inner white edge, and then a colored interior.
    # This makes it easy for us to distinguish these objects from other images on the floor, sides, or impression.

    # We use the next operations on the src_gray image to create a black and white image
    # of just the edges (in white) and the background becomes black.

    # Open-Close morphology operations
    open_morphology = 2     # reduces noise in background,
    close_morphology = 1    # reduces noise in foreground,
    #  For info on cv2.getStructuringElement, and open_morphology and close_morphology, see:
    #  https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/\
    #  py_morphological_ops/py_morphological_ops.html
    element1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                         (open_morphology * 2 + 1, open_morphology * 2 + 1),
                                         (open_morphology, open_morphology))
    src_gray = cv2.morphologyEx(src_gray, cv2.MORPH_OPEN, element1)

    element2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                         (close_morphology * 2 + 1, close_morphology * 2 + 1),
                                         (close_morphology, close_morphology))
    src_gray = cv2.morphologyEx(src_gray, cv2.MORPH_CLOSE, element2)
    src_gray_rows, src_gray_cols = src_gray.shape

    #  STEP 4: Detect edges using canny algorithm
    #  Canny is an algorithm which identify edges of shapes in the image.
    #  Increasing contrast (darker below a threshold, lighter above the threshold) makes the edges easier to identify
    thresh = 1250 * pow((src_gray_rows * src_gray_cols), -0.25)

    # blurring prevents a single mismatched pixel from looking like a break in a line.
    src_gray = cv2.blur(src_gray, (3, 3))
    canny_output = cv2.Canny(src_gray, thresh, thresh * 3, 3)

    #  STEP 5: Create an array of connected shapes to check
    #  We now go through the canny output to find continuous black or white lines (edges of contours)
    #  We will now decompose each separate figure into a set of connected points, so that we can
    #  analyze each figure individually.

    #  For info on FindContours see https://pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # A call to cv2.findContours returns the set of outlines (i.e., contours) that correspond
    # to each of the white blobs on the image.
    # You can read more about how the return signature of cv2.findContours changed
    # between OpenCV versions in this post:
    # https://pyimagesearch.com/2015/08/10/checking-your-opencv-version-using-python/

    contours_size = len(contours)
    # This is the number of shapes that might be markers (items in list of contours).
    #  We'll then find the (x,y) 2D position of the center of each shape in the image.   This will allow us
    #  to iterate over each shape, to identify which shape is which, and to determine if shapes overlap.
    centers = [None] * len(contours)

    number_of_markers_found = 0
    # Wherever possible, we will want to identify at least 3 points per image,
    # because you need 3 intersecting lines to uniquely identify a (x, y, z) point in 3D space.
    # By recognizing at least 3 markers on the floor, we can see where their light rays intersect the 2D camera sensor.
    # That in turn allows us to calculate in (x, y, z) 3D space exactly where the camera which took
    # this particular image must be located.

    # The photogrammetry algorithm reverses this process, using at least 3 images and identifying a single
    # position visible in all of them. It then calculates how far each point on the target is from the known
    # camera positions. Given the calculated distances between the camera positions and the angle of where the
    # points on the target appear from each camera, photogrammetry draws triangle and uses triangulation to
    # precisely locate where the imaged point on the target must be in 3D space.

    # For each image we will try to recognize as many marker positions as possible,
    # but some shapes found will be low confidence.  THEORETICALLY, including MORE
    # of these marker locations in the information we provide the photogrammetry algorithm should improve
    # its accuracy.

    # HOWEVER, the greater the error in any marker position we provide the photogrammetry algorithm,
    # the more error the photogrammetry may introduce into its estimates.   So more positions, with
    # ever decreasing confidence will actually degrade our accuracy.
    max_number_of_matches_to_output = 3

    for accuracy_diff in range(1, 100, 1):
        # We therefore estimate accuracy (accuracy_diff) for each potential marker position identified, and we order the
        # list of markers by this confidence order,  and we only select the N BESt positions, with N
        # being at least 3 wherever possible, and ignore the rest.
        if number_of_markers_found >= max_number_of_matches_to_output:
            break

        for i in range(0, contours_size, 1):

            # Ignore contours that are too short and only process those whose perimeter length are large enough:
            if cv2.arcLength(contours[i], 1) > math.sqrt(src_gray_rows * src_gray_cols) / 6.0:

                #  STEP 6: Create a list of points that bound the discovered contour shape (convex hull)
                hull = cv2.convexHull(contours[i])
                hull_size = len(hull)  # hull_size is the number of points in this shape.
                # our markers are circle, and viewed from any angle they look like a foreshortened ellipse.
                # The convex hull of such an ellipse is likely to be a polygon of at least 5 sides, so we
                # can ignore those that have fewer sides.
                if hull_size >= 5:

                    # STEP 7: Find the smallest ellipse that can surround the hull
                    box = cv2.fitEllipse(hull)
                    # We find the minimum Rectangle that is NOT rotated which surrounds this shape, so we know the
                    # minimum and maximum x and y positions and the width and height of the shape in pixels
                    # We only need to explore pixels inside this bounding rectangle.
                    bounding_rect = cv2.minAreaRect(hull)
                    (box_x, box_y), (box_size_width, box_size_height), angle = bounding_rect
                    # We also identify the center x and y of our shape.
                    (float_center_x, float_center_y), float_radius = cv2.minEnclosingCircle(hull)
                    box_center_x = int(float_center_x + .5)  # round to integer
                    box_center_y = int(float_center_y + .5)  # round to integer
                    box_radius = int(float_radius + .5)  # round to integer

                    # STEP 8: ignore any candidates that are absurdly large or small, not elliptical, or that overlap
                    # Select only contour areas within reasonable size range
                    if box_size_width * box_size_height > src_gray_rows * src_gray_cols / 200.0:
                        if box_size_width * box_size_height < src_gray_rows * src_gray_cols / 20.0:

                            # check area difference is reasonable for a foreshortened circle.
                            if abs(math.pi * box_size_width * box_size_height / 4
                                   - cv2.contourArea(hull, False)) / cv2.contourArea(hull, False) \
                                    < accuracy_diff / 2000.0:

                                # ignore markers that overlap with others.
                                ff = 0
                                if number_of_markers_found != 0:
                                    for n in range(0, number_of_markers_found, 1):
                                        (contour_center_x, contour_center_y) = centers[n]
                                        if (math.sqrt(pow(contour_center_x - box_center_x, 2)
                                                      + pow(contour_center_y - box_center_y, 2))
                                                < math.sqrt(box_size_width * box_size_height) / 2):
                                            ff = 1

                                #  Record only the best N (3)  markers that passes all constraints.
                                if ff == 0 and number_of_markers_found < max_number_of_matches_to_output:
                                    centers[number_of_markers_found] = (box_center_x, box_center_y)
                                    number_of_markers_found = number_of_markers_found + 1

                                    #  STEP 9: Determine which marker we have found from its color.

                                    #  We want to look at the pixels that surround the center of the shape.
                                    #  the radius of this circle should be the size of the smallest axis
                                    #  of the ellipse.

                                    if box_size_width < box_size_height:
                                        radius_size = box_size_width
                                    else:
                                        radius_size = box_size_height
                                    #  Within that circle, should be our marker colors.
                                    #  Marker colors should either be a circle that is all one Hue,
                                    #  Or they should be a pair of contrasting colors that each compose
                                    #  one half of the circle.

                                    #  The AVERAGE of the hues in a SOLID color spot should be pretty close
                                    #  to the expected hue. And the STANDARD DEVIATION of the pixel hues
                                    #  should be close to zero. so if that's true, we know which spot it is.

                                    # Conversely, if the AVERAGE is NOT near one of the solid colors,  it is likely
                                    # a marker with TWO colors.  We can also check the STANDARD DEVIATION of the hues
                                    # of pixels is appropriate for just two colors, in equally amounts.
                                    # And the specific colors we chose for our markers have been chosen so that
                                    # the AVERAGE hue that is midway between them, is far from the averages of
                                    # the of other color pairs.

                                    radius = radius_size / 4

                                    # define region of interest (roi)
                                    y1 = int(box_center_y - radius + .5)  # round up to next integer
                                    y2 = int(box_center_y + radius + .5)  # round up to next integer
                                    x1 = int(box_center_x - radius + .5)  # round up to next integer
                                    x2 = int(box_center_x + radius + .5)  # round up to next integer
                                    roi1 = hsv[y1:y2, x1:x2]
                                    # cv2.cvSetImageROI(hsv, roi1)

                                    # calculate color average and standard deviation
                                    # cv2.cvAvgSdv(hsv, avg, sdv)
                                    mean, std_dev = cv2.meanStdDev(roi1)
                                    (hue_mean, saturation_mean, value_mean) = mean
                                    (hue_std_dev, saturation_std_dev, value_std_dev) = std_dev

                                    # Find the correct color marker_id
                                    marker_id = 0
                                    if hue_std_dev < 20:
                                        c = int(hue_mean / 64)
                                        if c == 0:
                                            if value_std_dev < 16:
                                                marker_id = 1
                                            else:
                                                marker_id = 5
                                        elif c == 1:
                                            if value_std_dev < 16:
                                                marker_id = 2
                                            else:
                                                marker_id = 6
                                        elif c == 2:
                                            if value_std_dev < 16:
                                                marker_id = 3
                                            else:
                                                marker_id = 7
                                        elif c == 3:
                                            if value_std_dev < 16:
                                                marker_id = 4
                                            else:
                                                marker_id = 8

                                    elif 20 <= hue_std_dev < 64:
                                        c = int((hue_mean + 32) / 64)
                                        if c == 0:
                                            marker_id = 5
                                        elif c == 1:
                                            marker_id = 9
                                        elif c == 2:
                                            marker_id = 10
                                        elif c == 3:
                                            if value_std_dev[2] < 32:
                                                # the extra steps are because our current color scheme for
                                                # ID8 & 5 does not work as assumed.
                                                marker_id = 11
                                            else:
                                                marker_id = 8
                                        elif c == 4:
                                            marker_id = 8
                                    else:
                                        if value_std_dev < 32:
                                            marker_id = 12
                                        else:
                                            marker_id = 8

                                    # print(f' {image_file} contains marker {marker_id} at' +
                                    #       f' (h={box_center_y}, w= {box_center_x})' +
                                    #      f' ({number_of_markers_found})')

                                    markers_found_in_this_file.append((marker_id, image_file,
                                                                       box_center_x, box_center_y))

    if number_of_markers_found < 3:
        # print("Warning: couldn't find 3 markers for the above image.")
        pass
    # print(markers_found_in_this_file)
    # print()
    return markers_found_in_this_file


def write_gcp_xml_file(gcp_file_path_name, image_file_dir_path):
    # returns  file_contents: multi_line_string

    # search all files for the best markers
    image_files = glob.glob(os.path.join(image_file_dir_path, '*.jpg'))
    image_files + glob.glob(os.path.join(image_file_dir_path, '*.JPG'))
    image_files + glob.glob(os.path.join(image_file_dir_path, '*.jpeg'))
    image_files + glob.glob(os.path.join(image_file_dir_path, '*.JPEG'))
    image_files = sorted(image_files)

    marker_image_array = {}
    for marker_name in range(1, 13, 1):
        marker_image_array[marker_name] = []

    all_marker_tuples = []
    for image_file in image_files:
        list_of_marker_tuples_in_this_image = find_best_n_markers_in_image_file(image_file)
        for marker_tuple in list_of_marker_tuples_in_this_image:
            all_marker_tuples.append(marker_tuple)
    sorted_marker_tuples = sorted(all_marker_tuples)

    for sorted_marker_tuple in sorted_marker_tuples:
        marker_name, image_file, x, y = sorted_marker_tuple
        marker_image_array[marker_name].append(sorted_marker_tuple)
        # print(sorted_marker_tuple)

    # for marker_name in range(1, 13, 1):
        # print(marker_image_array[marker_name])

    marker_dict_result = define_marker_positions()

    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>',
                   '<surveydata coordinatesystem="XYZ" description="Local coordinatesystem; millimeters" epsgcode="0">',
                   ' <markers>']

    for marker_name in marker_image_array:
        if marker_image_array[marker_name]:
            marker_id = marker_name
            if marker_name == 12:
                marker_id = 0
            xml_content.append(f'   <marker id="{marker_id}" name="{marker_name}">')
            xml_content.append('     <images>')
            gcp_found = False
            for marker_tuple in marker_image_array[marker_name]:
                (marker_number, image_file, xpixel, ypixel) = marker_tuple
                (_, _, x, y, z, azimuth_in_degrees, azimuth_in_radians) = marker_dict_result[marker_number]
                xml_content.append(f'       <image name="{image_file}" xpixel="{xpixel}" ypixel="{ypixel}"/>')
                gcp_found = True
            xml_content.append('     </images>')
            if gcp_found:
                xml_content.append(f'     <gcp ' + f'x="{x:.3f}" y="{y:.3f}" z="{z:.3f}"' + '/>')
                gcp_found = False
            xml_content.append('   </marker>')

    xml_content.append(' </markers>')
    xml_content.append(' </surveydata>')

    try:
        gcp_file = open(gcp_file_path_name, "w")
    except IOError:
        print(f"Unable to create {gcp_file_path_name}.")
        return xml_content

    for line in xml_content:
        try:
            gcp_file.write(line + '\n')
        except IOError:
            print(f"Unable to write line to {gcp_file_path_name}.")
            return xml_content
        print(line)

    try:
        gcp_file.close()
    except IOError:
        print(f"Unable to close {gcp_file_path_name}.")
    return xml_content


if __name__ == '__main__':

    image_file_dir = sys.argv[1]
    gcp_file_path = os.path.join(image_file_dir, 'gcp.xml')

    write_gcp_xml_file(gcp_file_path, image_file_dir)
    print('Uploaded Ground Control Points file: (gcp.xml)')

#
#
#
# <?xml version="1.0" encoding="UTF-8"?>
# <surveydata coordinatesystem="XYZ" description="Local coordinatesystem; meters" epsgcode="0">
#  <markers>
#    <marker id="0" name="1">
#      <images>
#        <image name="IMG_0138.JPG" xpixel="2051" ypixel="946"/>
#        <image name="IMG_0139.JPG" xpixel="2030" ypixel="1366"/>
#        <image name="IMG_0153.JPG" xpixel="2659" ypixel="57"/>
#      </images>
#      <gcp x="4.897" y="-18.174" z="-1.964" checkpoint="false"/>
#    </marker>
#    <marker id="1" name="10">
#      <images>
#        <image name="IMG_0143.JPG" xpixel="2638" ypixel="1562"/>
#        <image name="IMG_0153.JPG" xpixel="1996" ypixel="1515"/>
#        <image name="IMG_0154.JPG" xpixel="1981" ypixel="1951"/>
#      </images>
#      <gcp x="10.017" y="-43.106" z="-1.121" checkpoint="false"/>
#    </marker>
#    <marker id="2" name="11">
#      <images>
#        <image name="IMG_0127.JPG" xpixel="1774" ypixel="1441"/>
#        <image name="IMG_0130.JPG" xpixel="1753" ypixel="2694"/>
#        <image name="IMG_0132.JPG" xpixel="1288" ypixel="33"/>
#        <image name="IMG_0133.JPG" xpixel="1435" ypixel="415"/>
#      </images>
#      <gcp x="-2.481" y="9.208" z="-1.922" checkpoint="false"/>
#    </marker>
#  </markers>
# </surveydata>
