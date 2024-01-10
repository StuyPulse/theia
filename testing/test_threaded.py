"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import time
import numpy as np
import cv2

from imutils.video import WebcamVideoStream
import matplotlib.pyplot as plt

cap = WebcamVideoStream(src=0).start()

calibrating = False

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16H5) if not calibrating else cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters()

# AprilTag Parameters
# parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
# parameters.aprilTagQuadDecimate = 0
# parameters.aprilTagMinClusterPixels = 250
# parameters.aprilTagCriticalRad = 60 * (3.141592 / 180)
# parameters.aprilTagMaxLineFitMse = 5
# parameters.aprilTagMaxNmaxima = 4

# Aruco Parameters
parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
parameters.useAruco3Detection = True
parameters.adaptiveThreshWinSizeMin = 3
parameters.adaptiveThreshWinSizeMax = 7
parameters.adaptiveThreshWinSizeStep = 2
parameters.adaptiveThreshConstant = 10
parameters.cornerRefinementMaxIterations = 50
parameters.perspectiveRemoveIgnoredMarginPerCell = 0.1
parameters.minMarkerLengthRatioOriginalImg = 0.0000

board = cv2.aruco.CharucoBoard((12, 9), 0.03, 0.023, dictionary)

allCorners = []
allIDs = []

arucoDetector = cv2.aruco.ArucoDetector(dictionary, parameters)
charucoDetector = cv2.aruco.CharucoDetector(board)

cf = 0

config = {
    "camera_matrix": [[1.12369315e+03, 0.00000000e+00, 6.48797373e+02], 
                      [0.00000000e+00, 1.20545225e+03, 3.75301268e+02], 
                      [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]],
    "distortion_coefficients": [[ 1.87344984e-01, 
                                 -1.81555130e+00, 
                                  2.53372901e-03, 
                                  8.18819635e-03, 
                                  4.08703281e+00]]
}

# config = {
#     "camera": "iPhone 11 Pro Max",
#     "camera_matrix": [[1.73465782e+03, 0.00000000e+00, 5.48790591e+02],
#                       [0.00000000e+00, 1.73374563e+03, 9.53893099e+02],
#                       [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]],
#     "distortion_coefficients": [[ 2.57479735e-01, 
#                                  -1.44465221e+00, 
#                                  -1.43476459e-03, 
#                                  -9.18646694e-04, 
#                                   2.49767228e+00]]
# }

tag_poses = {
    0: [[0, 0, 0], [0, 0, 0]],
    1: [[0, 0, 0], [0, 0, 0]],
    2: [[0, 0, 0], [0, 0, 0]],
    3: [[0, 0, 0], [0, 0, 0]],
    4: [[0, 0, 0], [0, 0, 0]],
    5: [[0, 0, 0], [0, 0, 0]],
    6: [[0, 0, 0], [0, 0, 0]],
    7: [[0, 0, 0], [0, 0, 0]],
}

start_time = time.time()
frame_count = 0
display_time = 2
fps = 0

processing_ts = 0

allttvecs = []
# size = 0.03
size = 0.15
camera_matrix = np.asarray(config["camera_matrix"])
distortion_coefficients = np.asarray(config["distortion_coefficients"])

fc = 0
fcm = []
fps_record = []

axis = np.float32([[-size/2,-size/2,0], [size/2,-size/2,0],
                   [size/2,size/2,0], [-size/2,size/2,0],
                   [-size/2,-size/2,size],[size/2,-size/2,size],
                   [size/2,size/2,size],[-size/2,size/2,size]
                  ])

def drawCube(frame, imgpts):
    imgpts = np.int32(imgpts).reshape(-1,2)

    frame = cv2.drawContours(frame, [imgpts[:4]], -1, (0,255,0), 3)

    for i,j in zip(range(4),range(4,8)):
        frame = cv2.line(frame, tuple(imgpts[i]), tuple(imgpts[j]), (255), 3)

    frame = cv2.drawContours(frame, [imgpts[4:]], -1, (0,0,255), 3)

    return frame

while True:
    frame = cap.read()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame_count += 1
    currentTime = time.time() - start_time
    if (currentTime) >= display_time :
        fps = frame_count / (currentTime)
        frame_count = 0
        start_time = time.time()
        fps_record.append(fps)
    
    processing_ts = time.time()

    corners, ids, rejected = arucoDetector.detectMarkers(frame)
    corners = np.asarray(corners)
    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids, (0, 255, 0))

    if len(corners) > 0:

        if calibrating:
            if len(ids) > 10:
                charucoCorners, charucoIDs, markerCorners, markerIDs = charucoDetector.detectBoard(frame, corners, ids)
                frame = cv2.aruco.drawDetectedCornersCharuco(frame, charucoCorners, charucoIDs)
                
                if charucoCorners is not None and charucoIDs is not None and len(charucoCorners) >= 6:
                    allCorners.append(charucoCorners)
                    allIDs.append(charucoIDs.flatten())
            
            if len(allIDs) > 50000:
                print("Starting Calibration Calculations...")
                imsize = (frame.shape[0], frame.shape[1])
                start = time.time()
                retval, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners, allIDs, board, imsize, None, None)
                end = time.time()
                print(camera_matrix)
                print(distortion_coefficients)
                print("Calibration calculation took " + str(end - start) + " seconds")
                calibrating = False;
                break
        else:
            # rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, size, camera_matrix, distortion_coefficients) # DEPRECATED

            objPoints = np.asarray([
                [-size / 2, size / 2, 0],
                [size / 2, size / 2, 0],
                [size / 2, -size / 2, 0],
                [-size / 2, -size / 2, 0]
            ], dtype=np.float32)
            corners = np.asarray(corners, dtype=np.float32)
            
            rvecs = []
            tvecs = []
            for i, id in enumerate(ids):
                # print(corners[i])
                retval, rvec, tvec = cv2.solvePnP(objPoints, corners[i], camera_matrix, distortion_coefficients)
                rvecs.append(rvec)
                tvecs.append(tvec)

            rvecs = np.asarray(rvecs)
            tvecs = np.asarray(tvecs)

            for rvec, tvec in zip(rvecs, tvecs):
                rvec, _ = cv2.Rodrigues(rvec)
                imgpts, jac = cv2.projectPoints(axis, rvec, tvec, camera_matrix, distortion_coefficients)
                frame = drawCube(frame, imgpts)
                # cv2.drawFrameAxes(frame, camera_matrix, distortion_coefficients, rvec, tvec, size);

                ttvec = np.asarray([0, 0, 0], dtype=np.float32)
                if ids is not None:
                    for i, id in enumerate(ids[0]):
                        if id in tag_poses:
                            ttvec[0] = tag_poses[id][0][0] + tvec[0]
                            ttvec[1] = tag_poses[id][0][1] + tvec[1]
                            ttvec[2] = tag_poses[id][0][2] + tvec[2]
                            allttvecs.append(ttvec)
            fc += 1
            fcm.append(fc)

    # print("Processing time: " + str(time.time() - processing_ts) + " seconds")

    # h,  w = frame.shape[:2]
    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w,h), 1, (w,h))
    # frame = cv2.undistort(frame, camera_matrix, distortion_coefficients, None, newcameramtx)

    cv2.putText(frame, "FPS: " + str(round(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "PT: " + str(round((time.time() - processing_ts) * 1000)) + "ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("ARUCO", frame)

    if cv2.waitKey(1) == 27:
        break

print("Average FPS: " + str(round(sum(fps_record) / len(fps_record))))

cap.stop()
cv2.destroyAllWindows()

x = []
y = []
z = []

plt.figure(figsize=(15, 10))
plt.xlim(-0.15, 0.15)
plt.ylim(0, 1)
# plt.xlim(-2, 2)
# plt.ylim(0, 6)
plt.title("Threaded ARUCO Pose (x, z)")
plt.xlabel("X (meters)")
plt.ylabel("Z (meters)")

for tvec in allttvecs:
        x.append(tvec[0])
        y.append(tvec[1])
        z.append(tvec[2])

# plt.plot(fcm, x)
# plt.plot(fcm, y)
# plt.plot(fcm, z)
# plt.legend(['x', 'y', 'z'], loc='upper left')
plt.plot(x, z)
plt.show()
