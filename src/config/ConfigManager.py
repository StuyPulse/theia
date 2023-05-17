import os
import json
import cv2
import numpy
from ntcore import IntegerSubscriber, DoubleSubscriber, DoubleArraySubscriber, NetworkTableInstance

from config.Config import Config, RemoteConfig

FAMILY_DICTIONARY = {
    "4X4_50": cv2.aruco.DICT_4X4_50,
    "4X4_100": cv2.aruco.DICT_4X4_100,
    "4X4_250": cv2.aruco.DICT_4X4_250,
    "4X4_1000": cv2.aruco.DICT_4X4_1000,
    "5X5_50": cv2.aruco.DICT_5X5_50,
    "5X5_100": cv2.aruco.DICT_5X5_100,
    "5X5_250": cv2.aruco.DICT_5X5_250,
    "5X5_1000": cv2.aruco.DICT_5X5_1000,
    "6X6_50": cv2.aruco.DICT_6X6_50,
    "6X6_100": cv2.aruco.DICT_6X6_100,
    "6X6_250": cv2.aruco.DICT_6X6_250,
    "6X6_1000": cv2.aruco.DICT_6X6_1000,
    "7X7_50": cv2.aruco.DICT_7X7_50,
    "7X7_100": cv2.aruco.DICT_7X7_100,
    "7X7_250": cv2.aruco.DICT_7X7_250,
    "7X7_1000": cv2.aruco.DICT_7X7_1000,
    "ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "APRILTAG_16H5": cv2.aruco.DICT_APRILTAG_16h5,
    "APRILTAG_25H9": cv2.aruco.DICT_APRILTAG_25h9,
    "APRILTAG_36H10": cv2.aruco.DICT_APRILTAG_36h10,
    "APRILTAG_36H11": cv2.aruco.DICT_APRILTAG_36h11
}

class ConfigManager:
    def __init__(self):
        raise NotImplementedError
    
    def update(self, config: Config):
        raise NotImplementedError
    
class FileConfigManager(ConfigManager):
    config_file_name = "config.json"
    calibration_file_name = "calibration.json"

    def __init__(self):
        pass
    
    def update(self, config: Config) -> None:
        with open(os.getcwd() + "/config/data" + self.config_file_name, "r") as config_file:
            config_data = json.load(config_file)
            config.local.device_id = config_data["device_id"]
            config.local.server_ip = config_data["server_ip"]
            config.local.stream_port = config_data["stream_port"]

            config.local.calibrated = config_data["calibrated"]
            config.local.fiducial_size = config_data["fiducial_size"]
            config.local.detection_dictionary = cv2.getPredefinedDictionary(FAMILY_DICTIONARY[config_data["detection_dictionary"]])
            config.local.calibration_dictionary = cv2.getPredefinedDictionary(FAMILY_DICTIONARY[config_data["calibration_dictionary"]])

            config.local.aruco_parameters = cv2.aruco.DetectorParameters()

            cbp = config_data["charuco_board"]
            config.local.charuco_board = cv2.aruco.CharucoBoard((int(cbp[0]), int(cbp[1]), cbp[2], cbp[3], config.local.calibration_dictionary))

        with open(os.getcwd() + "/config/data/" + self.calibration_file_name, "r") as file:
            calibration = json.load(file)
            
        camera_matrix = numpy.asarray(calibration["camera_matrix"])
        distortion_coefficients = numpy.asarray(calibration["distortion_coefficients"])

        if type(camera_matrix) == numpy.ndarray and type(distortion_coefficients) == numpy.ndarray:
            config.local.camera_matrix = camera_matrix
            config.local.distortion_coefficients = distortion_coefficients
            config.local.calibrated = True

        print("""
#############
Configuration
#############
""")
        print("Device ID: " + config.local.device_id)
        print("Server IP: " + config.local.server_ip)
        print("Stream Port: " + str(config.local.stream_port))
        print("Fiducial Size: " + str(config.local.fiducial_size_m) + " m")
        print("Detection Dictionary: " + str(config_data["detection_dictionary"]))
        print("Calibration Dictionary: " + str(config_data["calibration_dictionary"]))
        print("Calibrated: " + str(config.local.calibrated))
        print("Camera Matrix: " + str(config.local.camera_matrix))
        print("Distortion Coefficients: " + str(config.local.distortion_coefficients))
        print("")

class NTConfigManager(ConfigManager):
    init_complete: bool = False

    camera_id_sub: IntegerSubscriber
    camera_resolution_width_sub: IntegerSubscriber
    camera_resolution_height_sub: IntegerSubscriber
    camera_auto_exposure_sub: IntegerSubscriber
    camera_exposure_sub: IntegerSubscriber
    camera_gain_sub: DoubleSubscriber
    fiducial_layout_sub: DoubleArraySubscriber

    def update(self, config: Config) -> None:
        if not self.init_complete:
            table = NetworkTableInstance.getDefault().getTable("/" + config.local.device_id + "/config")
            self.camera_id_sub = table.getEntry("camera_id").subscribe(RemoteConfig.camera_id)
            self.camera_resolution_width_sub = table.getEntry("camera_resolution_width").subscribe(RemoteConfig.camera_resolution_width)
            self.camera_resolution_height_sub = table.getEntry("camera_resolution_height").subscribe(RemoteConfig.camera_resolution_height)
            self.camera_auto_exposure_sub = table.getEntry("camera_auto_exposure").subscribe(RemoteConfig.camera_auto_exposure)
            self.camera_exposure_sub = table.getEntry("camera_exposure").subscribe(RemoteConfig.camera_exposure)
            self.camera_gain_sub = table.getEntry("camera_gain").subscribe(RemoteConfig.camera_gain)
            self.fiducial_layout_sub = table.getEntry("fiducial_layout").subscribe(RemoteConfig.fiducial_layout)
            self.init_complete = True

            config.remote.camera_id = self.camera_id_sub.get()
            config.remote.camera_resolution_width = self.camera_resolution_width_sub.get()
            config.remote.camera_resolution_height = self.camera_resolution_height_sub.get()
            config.remote.camera_auto_exposure = self.camera_auto_exposure_sub.get()
            config.remote.camera_exposure = self.camera_exposure_sub.get()
            config.remote.camera_gain = self.camera_gain_sub.get()

            try: 
                config.remote.tag_layout = json.loads(self.tag_layout_sub.get())
            except:
                config.remote.tag_layout = None
                pass
