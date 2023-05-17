import cv2
import numpy

from config.Config import Config

class PoseEstimator:
    def __init__(self, config: Config): 
        raise NotImplementedError
    
    def process(self, corners):
        raise NotImplementedError
    
class FiducialPoseEstimator(PoseEstimator):

    fiducial_size = 0.0
    object_points = numpy.array([])
    camera_matrix = None
    distortion_coefficient = None

    def __init__(self, config: Config):
        self.fiducial_size = config.local.fiducial_size
        self.object_points = numpy.asarray([
                [-self.fiducial_size / 2, self.fiducial_size / 2, 0],
                [self.fiducial_size / 2, self.fiducial_size / 2, 0],
                [self.fiducial_size / 2, -self.fiducial_size / 2, 0],
                [-self.fiducial_size / 2, -self.fiducial_size / 2, 0]
            ], dtype=numpy.float32)
        self.camera_matrix = config.local.camera_matrix
        self.distortion_coefficient = config.local.distortion_coefficient
    
    def process(self, corners, ids):
        rvecs = []
        tvecs = []

        for i, id in enumerate(ids):
            retval, rvec, tvec = cv2.solvePnP(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_SQPNP)
            rvecs.append(rvec)
            tvecs.append(tvec)

        return numpy.asarray(rvecs), numpy.asarray(tvecs)
