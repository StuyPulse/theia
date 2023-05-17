import cv2
import numpy
from config.Config import Config

class Detector:
    def __init__(self):
        raise NotImplementedError
    
    def detect(self, image, config: Config):
        raise NotImplementedError
    
class FiducialDetector:
    def __init__(self, config: Config):
        self.detector = cv2.aruco.ArucoDetector(config.local.detection_dictionary, config.local.aruco_parameters)

    def detect(self, image):
        corners, ids, rejected = self.detector.detectMarkers(image)
        if len(corners) > 0:
            return numpy.asarray(corners), numpy.asarray(ids)
        return numpy.asarray([]), numpy.asarray([])