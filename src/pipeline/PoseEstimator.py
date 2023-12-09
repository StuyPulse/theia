import cv2
import numpy

from config.Config import Config

class PoseEstimator:
    def __init__(self, config: Config): 
        raise NotImplementedError
    
    def process(self, corners):
        raise NotImplementedError
    
    @classmethod
    def matToEuler(self, mat):
        sy = numpy.sqrt(mat[0, 0] * mat[0, 0] + mat[1, 0] * mat[1, 0])
        singular = sy < 1e-6
        if not singular:
            pitch = numpy.arctan2(mat[2, 1], mat[2, 2])
            yaw = numpy.arctan2(-mat[2, 0], sy)
            roll = numpy.arctan2(mat[1, 0], mat[0, 0])
        else:
            pitch = numpy.arctan2(-mat[1, 2], mat[1, 1])
            yaw = numpy.arctan2(-mat[2, 0], sy)
            roll = 0
        return numpy.array([numpy.array([numpy.degrees(roll)]), numpy.array([numpy.degrees(pitch)]), numpy.array([numpy.degrees(yaw)])])
    
class FiducialPoseEstimator(PoseEstimator):

    fiducial_size = 0.0
    object_points = numpy.array([])
    camera_matrix = None
    distortion_coefficient = None

    def __init__(self, config: Config):
        self.camera_matrix = config.local.camera_matrix
        self.distortion_coefficient = config.local.distortion_coefficient
    
    def process(self, corners, ids, config: Config):
        if config.remote.fiducial_size != self.fiducial_size: 
            self.fiducial_size = config.remote.fiducial_size
            self.object_points = numpy.asarray([
                [-self.fiducial_size / 2, self.fiducial_size / 2, 0],
                [self.fiducial_size / 2, self.fiducial_size / 2, 0],
                [self.fiducial_size / 2, -self.fiducial_size / 2, 0],
                [-self.fiducial_size / 2, -self.fiducial_size / 2, 0]
            ], dtype=numpy.float32)
        
        rvecs = []
        tvecs = []
        rangs = []

        for i, id in enumerate(ids):
            _, rvec, tvec = cv2.solvePnP(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            rvec, tvec = cv2.solvePnPRefineVVS(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, rvec, tvec)

            rang, _ = cv2.Rodrigues(rvec) # Convert rotation vector [3x1] to rotation matrix [3x3]
            rang = self.matToEuler(rang)

            rvecs.append(rvec)
            tvecs.append(tvec)
            rangs.append(rang)

        return numpy.asarray(rvecs), numpy.asarray(tvecs), numpy.asarray(rangs)

class CameraPoseEstimator(PoseEstimator):
    def __init__(self):
        numpy.set_printoptions(suppress=True)
        pass
    
    def process(self, config: Config, rangs, tvecs, ids):

        if ids is None or rangs is None or tvecs is None: return None

        tag_poses = config.remote.fiducial_layout
        ids = ids.flatten()
        alltvecs = []
        allrangs = []

        for rang, tvec, id in zip(rangs, tvecs, ids):
            if id in tag_poses:
                alltvecs.append([tag_poses[id][0] + tvec[2],
                                tag_poses[id][1] + tvec[0],
                                tag_poses[id][2] + tvec[1]])
                allrangs.append([tag_poses[id][3] + rang[0],
                                tag_poses[id][4] + rang[1],
                                tag_poses[id][5] + rang[2]])

        if len(alltvecs) != 0 and len(allrangs) != 0:
            robot_pose = [] # [x, y, z, roll, pitch, yaw]
            alltvecs = numpy.concatenate(numpy.mean(alltvecs, axis=0))
            allrangs = numpy.concatenate(numpy.mean(allrangs, axis=0))
            robot_pose.append(alltvecs)
            robot_pose.append(allrangs)
            robot_pose = numpy.concatenate(robot_pose)
            return robot_pose
        return None