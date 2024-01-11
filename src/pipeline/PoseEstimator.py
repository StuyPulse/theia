"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import cv2
import numpy
import math

from config.Config import Config
from util.Pose3d import Pose3d

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
        poses = []

        for i, id in enumerate(ids):
            _, rvec, tvec = cv2.solvePnP(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            rvec, tvec = cv2.solvePnPRefineVVS(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, rvec, tvec)

            rang, _ = cv2.Rodrigues(rvec) # Convert rotation vector [3x1] to rotation matrix [3x3]
            rang = self.matToEuler(rang)

            rvecs.append(rvec)
            tvecs.append(tvec)
            rangs.append(rang)
            poses.append(Pose3d.from_cv2_pose(tvec, rang))

        return numpy.asarray(rvecs), poses

class CameraPoseEstimator(PoseEstimator):
    def __init__(self):
        numpy.set_printoptions(suppress=True)
        pass
    
    def process(self, config: Config, poses, ids):

        if ids is None or poses is None: return None

        tag_poses = config.remote.fiducial_layout
        camera_offset = config.remote.camera_offset
        ids = ids.flatten()
        alltvecs = []
        allrangs = []

        for pose, id in zip(poses, ids):
            if id in tag_poses:
                c = math.cos(tag_poses[id][5] - pose.yaw)
                s = math.sin(tag_poses[id][5] - pose.yaw)

                alltvecs.append([tag_poses[id][0] + (pose.x * c - pose.y * s),
                                tag_poses[id][1] +  (pose.x * s + pose.y * c),
                                tag_poses[id][2] + pose.z])
                allrangs.append([tag_poses[id][3] + pose.pitch,
                                tag_poses[id][4] + pose.roll,
                                tag_poses[id][5] + pose.yaw])

        if len(alltvecs) != 0 and len(allrangs) != 0:
            alltvecs = numpy.concatenate(numpy.mean(alltvecs, axis=0)) + numpy.array(camera_offset[:3])
            allrangs = numpy.concatenate(numpy.mean(allrangs, axis=0)) + numpy.array(list(map(math.degrees, camera_offset[3:])))
            robot_pose = []
            robot_pose.append(alltvecs)
            robot_pose.append(allrangs)
            robot_pose = numpy.concatenate(robot_pose)
            return robot_pose
        return None