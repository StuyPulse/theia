"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import time, cv2

from config.Config import Config, LocalConfig, RemoteConfig
from config.ConfigManager import FileConfigManager, NTConfigManager
from output.Annotate import AnnotateFiducials
from output.Stream import MJPGServer
from output.Publisher import NTPublisher
from pipeline.Capture import DefaultCapture
from pipeline.Detector import FiducialDetector
from pipeline.PoseEstimator import FiducialPoseEstimator

config = Config(LocalConfig(), RemoteConfig())
file_config_manager = FileConfigManager()
nt_config_manager = NTConfigManager()

file_config_manager.update(config)
nt_config_manager.update(config)

detector = FiducialDetector(config)
pose_estimator = FiducialPoseEstimator(config)
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

        if frame is None: 
            publisher.sendMsg("Camera not connected")
            publisher.send(0, 0, None, None, [], None)
            capture.release()
            continue

        fiducials, tids, all_corners = detector.detect(frame)

        areas = []
        if tids is not None and all_corners is not None:
            frame = cv2.aruco.drawDetectedMarkers(frame, all_corners, tids)
            tids, areas = detector.orderIDs(all_corners, tids)

        tids, primary_pose, reprojection_error = pose_estimator.process(fiducials, config)

        if (time.time() - start_time) > 1:
            fps = counter / (time.time() - start_time)
            start_time = time.time()
            counter = 0
        
        fpt = time.time() - fpt_start

        publisher.send(fps, fpt, tids, primary_pose, areas, reprojection_error)
        stream.set_frame(frame)

if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt:
        capture.release()
        publisher.close()
