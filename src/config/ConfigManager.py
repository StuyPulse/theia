"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import os
import json
import cv2
import numpy
import sys
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
    
class FileConfigManager:
    config_file_name = "config.json"
    calibration_file_name = "calibration.json"

    def __init__(self):
        pass
    
    def update(self, config: Config) -> None:
        with open("./config/data/" + self.config_file_name, "r") as config_file:
            config_data = json.load(config_file)
        config.local.device_name = config_data["device_name"]
        config.local.team_number = config_data["team_number"]
        
        if len(sys.argv) > 1 and sys.argv[1].strip() == "-l":
            config.local.server_ip = "127.0.0.1"
        else:
            s = str(config.local.team_number)[-4:].zfill(4)
            config.local.server_ip = f"10.{s[:2].lstrip('0')}.{s[2:].lstrip('0')}.2"
        
        config.local.stream_port = config_data["stream_port"]

        config.local.detection_dictionary = cv2.aruco.getPredefinedDictionary(FAMILY_DICTIONARY[config_data["detection_dictionary"]])
        config.local.calibration_dictionary = cv2.aruco.getPredefinedDictionary(FAMILY_DICTIONARY[config_data["calibration_dictionary"]])

        config.local.aruco_parameters = cv2.aruco.DetectorParameters()

        # AprilTag Parameters
        # config.local.aruco_parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
        # config.local.aruco_parameters.aprilTagQuadDecimate = 2
        # config.local.aruco_parameters.aprilTagMinClusterPixels = 250
        # config.local.aruco_parameters.aprilTagCriticalRad = 80 * (3.141592 / 180)

        # Aruco Parameters
        config.local.aruco_parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        config.local.aruco_parameters.useAruco3Detection = True
        # config.local.aruco_parameters.adaptiveThreshWinSizeMin = 141  # default 3
        # config.local.aruco_parameters.adaptiveThreshWinSizeMax = 251  # default 23
        # config.local.aruco_parameters.adaptiveThreshWinSizeStep = 20  # default 10
        # config.local.aruco_parameters.adaptiveThreshConstant = 4      # default 7
        # config.local.aruco_parameters.adaptiveThreshWinSizeMin = 13    # default 3
        # config.local.aruco_parameters.adaptiveThreshWinSizeMax = 53   # default 23
        # config.local.aruco_parameters.adaptiveThreshWinSizeStep = 20  # default 10
        # config.local.aruco_parameters.adaptiveThreshConstant = 7      # default 7
        # config.local.aruco_parameters.cornerRefinementWinSize = 5
        # config.local.aruco_parameters.cornerRefinementMaxIterations = 20
        # config.local.aruco_parameters.cornerRefinementMinAccuracy = 0.1
        # config.local.aruco_parameters.minMarkerPerimeterRate = 0.03
        # config.local.aruco_parameters.maxMarkerPerimeterRate = 4.0
        # config.local.aruco_parameters.polygonalApproxAccuracyRate = 0.05
        # config.local.aruco_parameters.perspectiveRemovePixelPerCell = 4
        # config.local.aruco_parameters.perspectiveRemoveIgnoredMarginPerCell = 0.13

        cbp = config_data["charuco_board"]
        config.local.charuco_board = cv2.aruco.CharucoBoard((int(cbp[0]), int(cbp[1])), cbp[2], cbp[3], config.local.calibration_dictionary)

        if not os.path.isfile(os.getcwd() + "/config/data/" + self.calibration_file_name):
            print("Calibration file not found, please run calibration first.")
            exit(1)
        
        with open(os.getcwd() + "/config/data/" + self.calibration_file_name, "r") as file:
            calibration = json.load(file)
                
        camera_matrix = numpy.asarray(calibration["camera_matrix"])
        distortion_coefficient = numpy.asarray(calibration["distortion_coefficient"])

        if type(camera_matrix) == numpy.ndarray and type(distortion_coefficient) == numpy.ndarray:
            config.local.camera_matrix = camera_matrix
            config.local.distortion_coefficient = distortion_coefficient

        print("""
#############
Configuration
#############
""")
        print("Device Name: " + config.local.device_name)
        print("Server IP: " + config.local.server_ip)
        print("Stream Port: " + str(config.local.stream_port))
        print("Detection Dictionary: " + str(config_data["detection_dictionary"]))
        print("Calibration Dictionary: " + str(config_data["calibration_dictionary"]))
        print("Camera Matrix: \n" + str(config.local.camera_matrix))
        print("Distortion Coefficients: \n" + str(config.local.distortion_coefficient) + "\n")

class NTConfigManager:
    init_complete: bool = False

    camera_id_sub: IntegerSubscriber
    camera_resolution_width_sub: IntegerSubscriber
    camera_resolution_height_sub: IntegerSubscriber
    camera_auto_exposure_sub: IntegerSubscriber
    camera_exposure_sub: IntegerSubscriber
    camera_gain_sub: DoubleSubscriber
    camera_brightness_sub: DoubleSubscriber
    fiducial_size_sub: DoubleSubscriber
    fiducial_layout_sub: DoubleArraySubscriber

    def __init__(self):
        pass

    def update(self, config: Config) -> None:
        if not self.init_complete:
            table = NetworkTableInstance.getDefault().getTable(config.local.device_name)
            table = table.getSubTable("config")

            self.camera_id_sub = table.getIntegerTopic("camera_id").subscribe(RemoteConfig.camera_id)
            self.camera_resolution_width_sub = table.getIntegerTopic("camera_resolution_width").subscribe(RemoteConfig.camera_resolution_width)
            self.camera_resolution_height_sub = table.getIntegerTopic("camera_resolution_height").subscribe(RemoteConfig.camera_resolution_height)
            self.camera_auto_exposure_sub = table.getIntegerTopic("camera_auto_exposure").subscribe(RemoteConfig.camera_auto_exposure)
            self.camera_exposure_sub = table.getIntegerTopic("camera_exposure").subscribe(RemoteConfig.camera_exposure)
            self.camera_gain_sub = table.getDoubleTopic("camera_gain").subscribe(RemoteConfig.camera_gain)
            self.camera_brightness_sub = table.getDoubleTopic("camera_brightness").subscribe(RemoteConfig.camera_brightness)
            self.fiducial_size_sub = table.getDoubleTopic("fiducial_size").subscribe(RemoteConfig.fiducial_size)
            self.fiducial_layout_sub = table.getDoubleArrayTopic("fiducial_layout").subscribe([])
            self.init_complete = True

        config.remote.camera_id = self.camera_id_sub.get()
        config.remote.camera_resolution_width = self.camera_resolution_width_sub.get()
        config.remote.camera_resolution_height = self.camera_resolution_height_sub.get()
        config.remote.camera_auto_exposure = self.camera_auto_exposure_sub.get()
        config.remote.camera_exposure = self.camera_exposure_sub.get()
        config.remote.camera_gain = self.camera_gain_sub.get()
        config.remote.camera_brightness = self.camera_brightness_sub.get()
        config.remote.fiducial_size = self.fiducial_size_sub.get()
        networkLayout = self.fiducial_layout_sub.get()
        
        layout = {}

        for i in range(int(len(networkLayout) / 7)):
            layout[int(networkLayout[i * 7 + 0])] = [
                networkLayout[i * 7 + 1], 
                networkLayout[i * 7 + 2],
                networkLayout[i * 7 + 3],
                networkLayout[i * 7 + 4],
                networkLayout[i * 7 + 5],
                networkLayout[i * 7 + 6]
            ]

        config.remote.fiducial_layout = layout
