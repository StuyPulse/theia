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
from pipeline.TagData import TagData
from util.Util import opencv_to_wpilib

from wpimath.geometry import *

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

            poses.append(TagData(id, opencv_to_wpilib(tvec, rvec)))
        
        return numpy.asarray(rvecs), numpy.asarray(tvecs), numpy.asarray(rangs), poses

class CameraPoseEstimator(PoseEstimator):
    def __init__(self):
        numpy.set_printoptions(suppress=True)
    
    def process(self, config: Config, poses: list[TagData]):
        if poses is None: return None

        tag_poses = config.remote.fiducial_layout
        cam_poses = []
        

        for pose in poses:
            
            if pose.tid in tag_poses.keys():
                field_to_tag = tag_poses[pose.tid]
                camera_to_tag = Transform3d(pose.cam_to_tag.translation(), pose.cam_to_tag.rotation())
                field_to_cam = field_to_tag.transformBy(camera_to_tag.inverse())
                cam_poses.append(Pose3d(field_to_cam.translation(), field_to_cam.rotation()))

        if len(cam_poses) > 0:
            pose_sum = Pose3d()
            for pose in cam_poses:
                pose_sum += pose
            return pose_sum / len(cam_poses)

        return None