"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import os, cv2, numpy

from PIL import Image, ImageDraw, ImageFont

FAMILY_DICT = {
    '4X4_50': cv2.aruco.DICT_4X4_50,
    '4X4_100': cv2.aruco.DICT_4X4_100,
    '4X4_250': cv2.aruco.DICT_4X4_250,
    '4X4_1000': cv2.aruco.DICT_4X4_1000,
    '5X5_50': cv2.aruco.DICT_5X5_50,
    '5X5_100': cv2.aruco.DICT_5X5_100,
    '5X5_250': cv2.aruco.DICT_5X5_250,
    '5X5_1000': cv2.aruco.DICT_5X5_1000,
    '6X6_50': cv2.aruco.DICT_6X6_50,
    '6X6_100': cv2.aruco.DICT_6X6_100,
    '6X6_250': cv2.aruco.DICT_6X6_250,
    '6X6_1000': cv2.aruco.DICT_6X6_1000,
    '7X7_50': cv2.aruco.DICT_7X7_50,
    '7X7_100': cv2.aruco.DICT_7X7_100,
    '7X7_250': cv2.aruco.DICT_7X7_250,
    '7X7_1000': cv2.aruco.DICT_7X7_1000,
    'ARUCO_ORIGINAL': cv2.aruco.DICT_ARUCO_ORIGINAL,
    'APRILTAG_16H5': cv2.aruco.DICT_APRILTAG_16h5,
    'APRILTAG_25H9': cv2.aruco.DICT_APRILTAG_25h9,
    'APRILTAG_36H10': cv2.aruco.DICT_APRILTAG_36h10,
    'APRILTAG_36H11': cv2.aruco.DICT_APRILTAG_36h11
}

print('Available dictionaries:')
for key in FAMILY_DICT.keys():
    print(key)
print()

dictionary_choice = ''
while dictionary_choice not in FAMILY_DICT.keys():
    dictionary_choice = input('Choose the dictionary: ').upper()
dictionary = cv2.aruco.getPredefinedDictionary(FAMILY_DICT[dictionary_choice])

dpi = 300
a4_size = (int(numpy.around((203.2 * dpi) / 25.4)), int(numpy.around((281.051 * dpi) / 25.4)))

marker_in = float(input('Marker size (in): '))
marker_width_pxl = int(marker_in * dpi)

number = int(input('Number of markers: '))

for i in range(number):

    if not os.path.exists('marker_output/'):
        os.mkdir('marker_output/')
    elif os.path.exists('marker_output/' + dictionary_choice + '_' + str(i) + '.pdf'):
        os.remove('marker_output/' + dictionary_choice + '_' + str(i) + '.pdf')

    print('Generating ' + dictionary_choice + '_' + str(i) + '.pdf')

    image = Image.new('RGB',
                 (a4_size[0],a4_size[1]),   # A4 at 300dpi
                 (255, 255, 255))

    marker = Image.fromarray(cv2.aruco.generateImageMarker(dictionary, i, marker_width_pxl))
    offset_tag = ((image.size[0] - marker_width_pxl) // 2, (image.size[1] - marker_width_pxl) // 2)
    image.paste(marker, offset_tag)

    draw = ImageDraw.Draw(image)
    fnt = ImageFont.truetype('Arial', 72)
    text = 'ID: ' + str(i) + '\nFamily: ' + dictionary_choice + '\nSize: ' + str(marker_in) + ' in'
    offset_text = ((image.size[0] - marker_width_pxl) / 2, ((image.size[1] - marker_width_pxl) / 2) + marker_width_pxl + 192)
    draw.text(offset_text, text.upper(), (0,0,0), font=fnt)

    outputfile = 'marker_output/' + dictionary_choice + '_' + str(i) + '.pdf'
    image.save(outputfile, 'PDF', quality=100)

print('Done!')
