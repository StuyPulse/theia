import time
import cv2

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
annotator = AnnotateFiducials(config)
stream = MJPGServer()
# publisher = NTPublisher()

stream.start(config)

start_time = time.time()
counter = 0

while True:
    fpt_start = time.time()
    counter += 1
    
    frame = capture.getFrame(config)
    corners, ids = detector.detect(frame)
    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    rvecs, tvecs = pose_estimator.process(corners, ids)
    pose = camera_pose_estimator.process(config, rvecs, tvecs, ids)

    if (time.time() - start_time) > 1 :
        fps = counter / (time.time() - start_time)
        start_time = time.time()
        counter = 0
    fpt = time.time() - fpt_start

    frame = annotator.annotate(frame, rvecs, tvecs, fps, fpt, config)
    print(fps, fpt, pose)
    # publisher.send(config, time.time(), fps, pose)
    stream.set_frame(frame)
