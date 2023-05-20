import time
import cv2
import matplotlib.pyplot as plt

from pipeline.Capture import DefaultCapture
from pipeline.Detector import FiducialDetector
from pipeline.PoseEstimator import FiducialPoseEstimator, CameraPoseEstimator
from config.Config import Config, LocalConfig, RemoteConfig
from config.ConfigManager import FileConfigManager, NTConfigManager
from output.Annotate import AnnotateFiducials
from output.Stream import MJPGServer

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

stream.start(config)

allPoses = []

while True:
    frame = capture.getFrame(config)
    corners, ids = detector.detect(frame)
    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    rvecs, tvecs = pose_estimator.process(corners, ids)
    pose = camera_pose_estimator.process(config, rvecs, tvecs, ids)
    if pose is not None:
        allPoses.append(pose)
    frame = annotator.annotate(frame, rvecs, tvecs, config)
    stream.set_frame(frame)

    # cv2.imshow("Capture", frame)

    if cv2.waitKey(1) == 27:
        break

capture.release()
cv2.destroyAllWindows()

x = []
y = []
z = []

print(allPoses)

for pose in allPoses:
        x.append(pose[0][0])
        y.append(pose[0][1])
        z.append(pose[0][2])

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.axes.set_xlim3d(0, 1) 
ax.axes.set_ylim3d(0, 1) 
ax.axes.set_zlim3d(0, 1) 

ax.set_xlabel('X')
ax.set_ylabel('Z')
ax.set_zlabel('Y')

ax.plot(x, y, z)
plt.show()