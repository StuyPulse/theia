"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import cv2
import numpy

from config.Config import Config

class Annotate:
    def __init__(self):
        raise NotImplementedError
    
    def annotate(self, image, config: Config):
        raise NotImplementedError
    
    @classmethod
    def drawCube(self, frame, image_points):
        image_points = numpy.int32(image_points).reshape(-1,2)

        frame = cv2.drawContours(frame, [image_points[:4]], -1, (0,255,0), 3)

        for i, j in zip(range(4),range(4,8)):
            frame = cv2.line(frame, tuple(image_points[i]), tuple(image_points[j]), (255), 3)

        frame = cv2.drawContours(frame, [image_points[4:]], -1, (0,0,255), 3)

        return frame
    
class AnnotateFiducials(Annotate):

    fiducial_size = 0.0
    axis = numpy.array([])

    def __init__(self):
        pass

    def annotate(self, image, rvecs, tvecs, fps, fpt, config: Config):
        if config.remote.fiducial_size != self.fiducial_size: 
            self.fiducial_size = config.remote.fiducial_size
            self.axis = numpy.float32([[-self.fiducial_size/2,-self.fiducial_size/2,0], [self.fiducial_size/2,-self.fiducial_size/2,0],
                   [self.fiducial_size/2,self.fiducial_size/2,0], [-self.fiducial_size/2,self.fiducial_size/2,0],
                   [-self.fiducial_size/2,-self.fiducial_size/2,self.fiducial_size],[self.fiducial_size/2,-self.fiducial_size/2,self.fiducial_size],
                   [self.fiducial_size/2,self.fiducial_size/2,self.fiducial_size],[-self.fiducial_size/2,self.fiducial_size/2,self.fiducial_size]
                  ])

        for rvec, tvec in zip(rvecs, tvecs):
            rvec, _ = cv2.Rodrigues(rvec)
            image_points, _ = cv2.projectPoints(self.axis, rvec, tvec, config.local.camera_matrix, config.local.distortion_coefficient)
            image = self.drawCube(image, image_points)
        cv2.putText(image, "FPS: " + str(round(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(image, "FPT: " + str(round(fpt * 1000)) + "ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        return image