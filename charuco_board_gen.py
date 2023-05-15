# Generate a charuco board with the specified dictionary and height
# Configuration information is included in the resulting image

import cv2, time, numpy

FAMILY_DICT = {
    "4X4_100": cv2.aruco.DICT_4X4_100,
    "4X4_250": cv2.aruco.DICT_4X4_250,
    "4X4_1000": cv2.aruco.DICT_4X4_1000,
    "5X5_100": cv2.aruco.DICT_5X5_100,
    "5X5_250": cv2.aruco.DICT_5X5_250,
    "5X5_1000": cv2.aruco.DICT_5X5_1000,
    "6X6_100": cv2.aruco.DICT_6X6_100,
    "6X6_250": cv2.aruco.DICT_6X6_250,
    "6X6_1000": cv2.aruco.DICT_6X6_1000,
    "7X7_100": cv2.aruco.DICT_7X7_100,
    "7X7_250": cv2.aruco.DICT_7X7_250,
    "7X7_1000": cv2.aruco.DICT_7X7_1000,
    "ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "APRILTAG_36H10": cv2.aruco.DICT_APRILTAG_36h10,
    "APRILTAG_36H11": cv2.aruco.DICT_APRILTAG_36h11
}

print("Available dictionaries:")
for key in FAMILY_DICT.keys():
    print(key)
print()

dictionary_choice = ""
while dictionary_choice not in FAMILY_DICT.keys():
    dictionary_choice = input("Choose the dictionary: ").upper()
dictionary = cv2.aruco.getPredefinedDictionary(FAMILY_DICT[dictionary_choice])

height = int(input("Height: "))
width = int(height / 1.333333333333333)

squareLength = 0.22 / height
board = cv2.aruco.CharucoBoard((width, height), squareLength, squareLength / 1.25, dictionary)

image = board.generateImage((2550, 3300), numpy.zeros((0, 0)), 128, 1)
image = cv2.putText(image, "Dictionary: " + dictionary_choice + " X: " + str(width) + " Y: " + str(height) + " Square Length: " + str(round(squareLength, 3)) + "m" + " Marker Length: " + str(round(squareLength / 1.25, 3)) + "m", (128, 3252), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 4, cv2.LINE_AA)
cv2.imwrite(str(time.time()).split(".")[1] + "_charuco_board.png", image)