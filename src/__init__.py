import time
import cv2

import matplotlib.pyplot as plt

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

capture = DefaultCapture()
detector = FiducialDetector(config)
pose_estimator = FiducialPoseEstimator(config)
camera_pose_estimator = CameraPoseEstimator()
annotator = AnnotateFiducials()
stream = MJPGServer()
publisher = NTPublisher(config)

poses = []

def main():
    stream.start(config)

    start_time = time.time()
    counter = 0

    while True:
        nt_config_manager.update(config)

        fpt_start = time.time()
        counter += 1
        
        frame = capture.getFrame(config)
        if frame is None: raise Exception("Camera not connected")

        corners, ids = detector.detect(frame)
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        rvecs, tvecs, rangs = pose_estimator.process(corners, ids, config)
        pose = camera_pose_estimator.process(config, rangs, tvecs, ids)

        if (time.time() - start_time) > 1:
            fps = counter / (time.time() - start_time)
            start_time = time.time()
            counter = 0
        fpt = time.time() - fpt_start
        frame = annotator.annotate(frame, rvecs, tvecs, fps, fpt, config)

        publisher.send(pose, fps, fpt)
        stream.set_frame(frame)
        # print(fpt * 1000)
        # print(pose)

        if pose is not None:
            poses.append(pose)

if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt:
        capture.release()
        publisher.close()
        # x = []
        # y = []
        # z = []

        # plt.figure(figsize=(12, 8))
        # plt.xlim(-0.3, 0.3)
        # plt.ylim(0, 5)
        # plt.title("Pose (x, z)")
        # plt.xlabel("X (meters)")
        # plt.ylabel("Z (meters)")

        # for tvec in poses:
        #         x.append(tvec[0])
        #         y.append(tvec[1])
        #         z.append(tvec[2])

        # plt.plot(x, z)
        # plt.show()
