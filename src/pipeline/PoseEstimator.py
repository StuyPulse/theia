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

class CameraPoseEstimator:
    def __init__(self):
        pass
    
    def process(self, config: Config, rvecs, tvecs, ids):
        # tag_poses = config.remote.tag_layout
        tag_poses = {
            0: [[0, 0, 0], [0, 0, 0]],
            1: [[0, 0, 0], [0, 0, 0]],
            2: [[0, 0, 0], [0, 0, 0]],
            3: [[0, 0, 0], [0, 0, 0]],
            4: [[0, 0, 0], [0, 0, 0]],
            5: [[0, 0, 0], [0, 0, 0]],
            6: [[0, 0, 0], [0, 0, 0]],
            7: [[0, 0, 0], [0, 0, 0]],
        }
        alltvecs = []
        allrvecs = []
        for rvec, tvec in zip(rvecs, tvecs):
            for i, id in enumerate(ids[0]):
                if id in tag_poses:
                    alltvecs.append([tag_poses[id][0][0] + tvec[0],
                                      tag_poses[id][0][1] + tvec[1],
                                      tag_poses[id][0][2] + tvec[2]])
                    allrvecs.append([tag_poses[id][1][0] + rvec[0],
                                     tag_poses[id][1][1] + rvec[1],
                                     tag_poses[id][1][2] + rvec[2]])
        
        robot_pose = []
        robot_pose.append(numpy.mean(alltvecs, axis=0))
        robot_pose.append(numpy.mean(allrvecs, axis=0))
        print(robot_pose)

        return robot_pose