import cv2
from pipeline.Capture import DefaultCapture
from pipeline.Detector import FiducialDetector
from config.Config import Config, LocalConfig, RemoteConfig
from config.ConfigManager import FileConfigManager, NTConfigManager

config = Config(LocalConfig(), RemoteConfig())
file_config_manager = FileConfigManager()
nt_config_manager = NTConfigManager()

capture = DefaultCapture()
detector = FiducialDetector(config)

file_config_manager.update(config)
nt_config_manager.update(config)

while True:
    capture.getFrame(config)
    cv2.imshow("Capture", capture.frame)