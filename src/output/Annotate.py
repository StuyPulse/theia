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
    def __init__(self, config: Config):
        self.fiducial_size = config.local.fiducial_size
        self.axis = numpy.float32([[-self.fiducial_size/2,-self.fiducial_size/2,0], [self.fiducial_size/2,-self.fiducial_size/2,0],
                   [self.fiducial_size/2,self.fiducial_size/2,0], [-self.fiducial_size/2,self.fiducial_size/2,0],
                   [-self.fiducial_size/2,-self.fiducial_size/2,self.fiducial_size],[self.fiducial_size/2,-self.fiducial_size/2,self.fiducial_size],
                   [self.fiducial_size/2,self.fiducial_size/2,self.fiducial_size],[-self.fiducial_size/2,self.fiducial_size/2,self.fiducial_size]
                  ])

    def annotate(self, image, rvecs, tvecs, config: Config):
        for rvec, tvec in zip(rvecs, tvecs):
            rvec, _ = cv2.Rodrigues(rvec)
            image_points, _ = cv2.projectPoints(self.axis, rvec, tvec, config.local.camera_matrix, config.local.distortion_coefficient)
            image = self.drawCube(image, image_points)
        return image