"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import cv2
import numpy
from config.Config import Config

class Detector:
    def __init__(self):
        raise NotImplementedError
    
    def detect(self, image, config: Config):
        raise NotImplementedError

    def orderIDs(self, corners, ids):
        raise NotImplementedError
    
class FiducialDetector:
    def __init__(self, config: Config):
        self.detector = cv2.aruco.ArucoDetector(config.local.detection_dictionary, config.local.aruco_parameters)

    def detect(self, image):
        all_corners, ids, rejected = self.detector.detectMarkers(image)

        fiducials = []

        if ids is not None:
            for tid, corners in zip(ids, all_corners):
                fiducials += [(tid[0], corners)]
            return fiducials, ids, all_corners
        return None, None, None

    def orderIDs(self, corners, ids): 

        if (numpy.asarray(ids).flatten().tolist() == []): return None
        
        corners = numpy.asarray(corners).flatten().tolist()
        ids = numpy.asarray(ids).flatten().tolist()

        areas = []

        for i in range(len(ids)):
            subX = corners[i * 8 + 0]
            subY = corners[i * 8 + 1]

            corners[i * 8 + 0] -= subX
            corners[i * 8 + 1] -= subY
            corners[i * 8 + 2] -= subX
            corners[i * 8 + 3] -= subY
            corners[i * 8 + 4] -= subX
            corners[i * 8 + 5] -= subY
            corners[i * 8 + 6] -= subX
            corners[i * 8 + 7] -= subY

            s1 = 0
            s2 = 0

            s1 += corners[i * 8 + 0] * corners[i * 8 + 3]
            s1 += corners[i * 8 + 2] * corners[i * 8 + 5]
            s1 += corners[i * 8 + 4] * corners[i * 8 + 7]
            s1 += corners[i * 8 + 6] * corners[i * 8 + 1]

            s2 += corners[i * 8 + 1] * corners[i * 8 + 2]
            s2 += corners[i * 8 + 3] * corners[i * 8 + 3]
            s2 += corners[i * 8 + 5] * corners[i * 8 + 6]
            s2 += corners[i * 8 + 7] * corners[i * 8 + 0]

            areas.append(abs(s1 - s2) / 2)

        outAreas = []
        outIDs = []
        
        while areas:
            smallest = min(areas)
            index = areas.index(smallest)

            outAreas.append(areas.pop(index))
            outIDs.append(ids.pop(index))

        outIDs.reverse()
        outAreas.reverse()
        
        return numpy.asarray(outIDs), outAreas
