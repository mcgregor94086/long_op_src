__author__ = ''


def crop_obj(scan_data):
    print('crop_obj()', scan_data)
    return

# obj_3d_crop.py
# (c) Scott L. McGregor, Dec 2019
#  License: free for all non commercial uses.  Contact author for any other uses.
#  Changes and Enhancements must be shared with author, and be subject to same use terms

# TL;DR:  This program uses a bounding box, and "crops" faces and vertices from a
# Wavefront .OBJ format file, created by Autodesk Forge Reality Capture API
# if one of the vertices in a face is not within the bounds of the box.
#
# METHOD
# 1) All lines other than "v" vertex definitions and "f" faces definitions
#    are copied UNCHANGED from the input .OBJ file to an output .OBJ file.
# 2) All "v" vertex definition lines have their (x, y, z) positions tested to see if:
#    min_x < x < max_x and min_y < y < max_y and min_z < z < max_z ?
#    If TRUE, we want to keep this vertex in the new OBJ, so we
#    store its IMPLICIT ORDINAL position in the file in a dictionary called v_keepers.
#    If FALSE, we will use its absence from the v_keepers file as a way to identify
#    faces that contain it and drop them.   All "v" lines are also copied unchanged to the
#    output file.
# 3) All "f" lines (face definitions) are inspected to verify that all 3 vertices in the face
#    are in the v_keepers list.   If they are, the f line is  output unchanged.
# 4) Any "f" line that refers to a vertex that was cropped, is prefixed by "# CROPPED: "
#    in the output file.  Lines beginning # are treated as comments, and ignored in future
#    processing.

# KNOWN LIMITATIONS: This program generates models in which the outside of bound faces
# have been removed. The vertices that were found outside the bounding box, are still in the
# OBJ file, but they are now disconnected and therefore ignored in later processing.
# The "f" lines for faces with vertices outside the bounding box are also still in the
# output file, but now commented out, so they don't process. Because this is non-destructive.
# we can easily change our bounding box later, uncomment cropped lines and reprocess.
#
# This might be an incomplete solution for some potential users.  For such users
# a more complete program would delete unneeded v, vn, vt and vp lines when the v vertex
# that they refer to is dropped. But note that this requires renumbering all references to these
# vertices definitions in the "f" face definition lines.  Such a more complete solution would also
# DISCARD all 'f' lines with any vertices that are out of bounds, instead of making them copies.
# Such a rewritten .OBJ file would be var more compact, but changing the bounding box would require
# saving the pre-cropped original.

# QUIRK: The OBJ file format defines v, vn, vt, vp and f elements by their
# IMPLICIT ordinal occurrence in the file,  with each element type maintaining
# its OWN separate sequence.  It then references those definitions EXPLICITLY in
# f face definitions. So deleting (or commenting out) element references requires
# appropriate rewriting of all the"f"" lines tracking all the new implicit positions.

# Such rewriting is not particularly hard to do, but it is one more place to make
# a mistake, and could  make the algorithm more complicated to understand.
# This program doesn't bother, because all further processing of the output
# OBJ file ignores unreferenced v, vn, vt and vp elements.
#
# Saving all lines rather than deleting them to save space is a tradeoff involving considerations of
# Undo capability, compute cycles, compute space (unreferenced lines) and maintenance complexity choice.
# It is left to the motivated programmer to add this complexity if needed.

# Because the cameras can see beyond the target area, the initial OBJ
# will contain a significant part of the floor, and sometimes parts of the walls.
# We therefore take the OBJ model and then throw out all the points that
# are outside the target area, and which we don't want.

# These are the default cropping values in mm from the 'origin'.
# The Origin should be the dot in the center of the colored circles
# printed on the floor.

max_x = 30
max_y = 30
max_z = 30
min_x = -30
min_y = -30
min_z = 4  # adjust this to a larger number until the floor is no longer visible.

def obj_3d_crop(max_x, max_y, max_z, min_x, min_y, min_z, obj_filename, cropped_obj_filename):

    v_keepers = dict()  # keeps track of which vertices are within the bounding box

    kept_vertices = 0
    discarded_vertices = 0

    kept_faces = 0
    discarded_faces = 0

    discarded_lines = 0
    kept_lines = 0

    obj_file = open(obj_filename, 'r')
    new_obj_file = open(cropped_obj_filename, 'w')

    # the number of the next "v" vertex lines to process.
    original_v_number = 1  # the number of the next "v" vertex lines to process.
    new_v_number = 1  # the new ordinal position of this vertex if out of bounds vertices were discarded.

    for line in obj_file:
        line_elements = line.split()

        # Python doesn't have a SWITCH statement, but we only have 3 cases, so we'll just use cascading if statements
        if line_elements[0] != "f":  # if it isn't an "f" type line (face definition)

            if line_elements[0] != "v":  # and it isn't an "v" type line either (vertex definition)
                # ************************ PROCESS ALL NON V AND NON F LINE TYPES ******************
                # then we just copy it unchanged from the input OBJ to the output OBJ
                new_obj_file.write(line)
                kept_lines = kept_lines + 1

            else:  # then line_elements[0] == "v":
                # ************************ PROCESS VERTICES ****************************************
                #  a "v" line looks like this:
                #  f x y z ...
                x = float(line_elements[1])
                y = float(line_elements[2])
                z = float(line_elements[3])

                if min_x < x < max_x and min_y < y < max_y and min_z < z < max_z:
                    # if vertex is within  the bounding box, we include it in the new OBJ file
                    new_obj_file.write(line)
                    v_keepers[str(original_v_number)] = str(new_v_number)
                    new_v_number = new_v_number + 1
                    kept_vertices = kept_vertices + 1
                    kept_lines = kept_lines + 1
                else:     # if vertex is NOT in the bounding box
                    new_obj_file.write(line)
                    discarded_vertices = discarded_vertices + 1
                    discarded_lines = discarded_lines + 1
                original_v_number = original_v_number + 1

        else:  # line_elements[0] == "f":
            # ************************ PROCESS FACES ****************************************
            #  a "f" line looks like this:
            #  f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...

            #  We need to delete any face lines where ANY of the 3 vertices v1, v2 or v3 are NOT in v_keepers.
            v = ["", "", ""]
            # Note that v1, v2 and v3 are the first "/" separated elements within each line element.
            for i in range(0, 3):
                v[i] = line_elements[i+1].split('/')[0]

            # now we can check if EACH of these 3 vertices are  in v_keepers.
            # for each f line, we need to determine if all 3 vertices are in the v_keepers list
            if v[0] in v_keepers and v[1] in v_keepers and v[2] in v_keepers:
                new_obj_file.write(line)
                kept_lines = kept_lines + 1
                kept_faces = kept_faces + 1
            else:  # at least one of the vertices in this face has been deleted, so we need to delete the face too.
                discarded_lines = discarded_lines + 1
                discarded_faces = discarded_faces + 1
                new_obj_file.write("# CROPPED "+line)

    # end of line processing loop
    obj_file.close()
    new_obj_file.close()

    print("kept vertices:  ", kept_vertices,  "discarded vertices: ", discarded_vertices)
    print("kept faces:     ", kept_faces,     "discarded faces:    ", discarded_faces)
    print("kept lines:     ", kept_lines,     "discarded lines:    ", discarded_lines)

if __name__ == '__main__':
    crop_obj('test data')
