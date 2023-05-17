import cv2
from pipeline.Capture import DefaultCapture
from pipeline.Detector import FiducialDetector
from pipeline.PoseEstimator import FiducialPoseEstimator, CameraPoseEstimator
from config.Config import Config, LocalConfig, RemoteConfig
from config.ConfigManager import FileConfigManager, NTConfigManager
from output.Annotate import AnnotateFiducials

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

while True:
    frame = capture.getFrame(config)
    corners, ids = detector.detect(frame)
    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    rvecs, tvecs = pose_estimator.process(corners, ids)
    camera_pose = camera_pose_estimator.process(config, rvecs, tvecs, ids)
    frame = annotator.annotate(frame, rvecs, tvecs, config)

    cv2.imshow("Capture", frame)

    if cv2.waitKey(1) == 27:
        break

capture.release()
cv2.destroyAllWindows()