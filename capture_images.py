"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

# Captures camera stream and writes image on user request

import cv2
import os
import time

capture = cv2.VideoCapture(1)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
board = cv2.aruco.CharucoBoard((12, 9), 0.03, 0.023, dictionary)
charucoDetector = cv2.aruco.CharucoDetector(board)
images = 0

while True:

    _, image = capture.read()

    charucoCorners, charucoIDs, markerCorners, markerIDs = charucoDetector.detectBoard(image)

    cv2.imshow("Capture", image)
    
    if charucoCorners is not None and charucoIDs is not None and cv2.waitKey(1) == 32: # space
        cv2.imwrite(os.getcwd() + "/captures/" + str(round(time.time())) + "_capture.png", image)
        images += 1
        print("Images Captured: " + str(images))
    else:
        pass

    cv2.aruco.drawDetectedCornersCharuco(image, charucoCorners, charucoIDs)

    if cv2.waitKey(1) == 27: # esc
        break

capture.release()
cv2.destroyAllWindows()