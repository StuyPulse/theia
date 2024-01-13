"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import time
import cv2
import numpy

from wpimath.geometry import *

from config.Config import Config, LocalConfig, RemoteConfig
from config.ConfigManager import FileConfigManager, NTConfigManager
from output.Annotate import AnnotateFiducials
from output.Stream import MJPGServer
from output.Publisher import NTPublisher
from pipeline.Capture import DefaultCapture
from pipeline.Detector import FiducialDetector
from pipeline.PoseEstimator import FiducialPoseEstimator, CameraPoseEstimator

config = Config(LocalConfig(), RemoteConfig())
file_config_manager = FileConfigManager()
nt_config_manager = NTConfigManager()

file_config_manager.update(config)
nt_config_manager.update(config)

detector = FiducialDetector(config)
pose_estimator = FiducialPoseEstimator(config)
camera_pose_estimator = CameraPoseEstimator()
annotator = AnnotateFiducials()
stream = MJPGServer()
publisher = NTPublisher(config)
capture = DefaultCapture(publisher)

def main():

    publisher.sendMsg(config.local.device_name + " has started")

    stream.start(config)

    start_time = time.time()
    counter = 0

    while True:
        nt_config_manager.update(config)

        fpt_start = time.time()
        counter += 1
        
        frame = capture.getFrame(config)

        if frame is not None:
            corners, ids = detector.detect(frame)
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            rvecs, tvecs, rangs, poses = pose_estimator.process(corners, ids, config)
        else: 
            publisher.sendMsg("Camera not connected")
            print('Camera not connected')
            rvecs, tvecs, rangs, poses = numpy.asarray([0] * 3), numpy.asarray([0] * 3), numpy.asarray([0] * 3), Pose3d(Translation3d(-100, -100, -100), Rotation3d(0, 0, 0))

        pose = camera_pose_estimator.process(config, poses)

        if (time.time() - start_time) > 1:
            fps = counter / (time.time() - start_time)
            start_time = time.time()
            counter = 0
        fpt = time.time() - fpt_start
        frame = annotator.annotate(frame, rvecs, tvecs, fps, fpt, config)

        ids, tvecs = detector.orderIDs(corners, ids, tvecs)
        publisher.send(pose, fps, fpt, tvecs, rangs, ids)
        stream.set_frame(frame)

if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt:
        capture.release()
        publisher.close()
