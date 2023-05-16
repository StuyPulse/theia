# Manually calibrate camera using folder of previouly captured images
# Outputs camera matrix and distortion coefficients to json file and command line

import cv2
import numpy
import os
import time
import json
import datetime

images_path = "/captures"
output_file_name = "calibration.json"
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters()
arucoDetector = cv2.aruco.ArucoDetector(dictionary, parameters)
board = cv2.aruco.CharucoBoard((12,9), 0.03, 0.023, dictionary)
charucoDetector = cv2.aruco.CharucoDetector(board)

allCorners = []
allIDs = []
imsize = None
time_start = time.time()
i = 0

print("Starting calibration using images in " + images_path)

for image in os.listdir(os.cwd() + images_path):
    image = cv2.imread(image)
    markers, ids, rejected = arucoDetector.detectMarkers(image)
    charucoCorners, charucoIDs, markerCorners, markerIDs = charucoDetector.detectBoard(image, corners, ids)
    
    if charucoCorners is not None and charucoIDs is not None:
        allCorners.append(charucoCorners)
        allIDs.append(charucoIDs)

    if i == 0: imsize = (image.shape[0], image.shape[1])
    i += 1

retval, camera_matrix, distortion_coefficient, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners, allIDs, board, imsize, None, None)

print("Calibration complete for " str(i) + " images in " + str(time.time() - time_start) + " seconds")
print("Camera Matrix")
print(camera_matrix)
print("Distortion Coefficients")
print(distortion_coefficient)

output = {
    "number_of_images": i
    "timestamp": datetime.datetime.now()
    "camera_matrix": camera_matrix,
    "distortion_coefficient": distortion_coefficient
}

with open(output_file_name, "w") as file:
    file.write(json.dumps(output, indent=4))

print("Wrote calibration data to " + output_file_name)