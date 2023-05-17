# Captures camera stream and writes image on user request

import cv2
import time

capture = cv2.VideoCapture(0)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
board = cv2.aruco.CharucoBoard((12, 9), 0.03, 0.023, dictionary)
charucoDetector = cv2.aruco.CharucoDetector(board)
images = 0

while True:

    image = capture.read()

    charucoCorners, charucoIDs, markerCorners, markerIDs = charucoDetector.detectBoard(image)
    image = cv2.drawDetectedCornersCharuco(image, charucoCorners, charucoIDs)
    cv2.putText(image, "Captured Images: " + str(i), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Capture", image)
    
    if charucoCorners is not None and charucoIDs is not None and cv2.waitKey() == 32: # space
        cv2.imwrite("/captures/" + time.now() + "_capture.png", image)
        images += 1

    if cv2.waitKey() == 27: # esc
        break

capture.release()
cv2.destroyAllWindows()