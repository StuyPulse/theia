"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import cv2
import numpy
from wpimath.geometry import *

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

def wpitocv(translation):
    return [translation[2], -translation[0], -translation[1]]

class FiducialPoseEstimator(PoseEstimator):

    fiducial_size = 0.0
    camera_matrix = None
    distortion_coefficient = None

    def __init__(self, config: Config):
        self.camera_matrix = config.local.camera_matrix
        self.distortion_coefficient = config.local.distortion_coefficient
    
    def process(self, corners, ids, config: Config):

        if ids is None or len(ids) is 0: return None, None

        object_points = []
        tag_layout = config.remote.fiducial_layout
        fid_size = config.remote.fiducial_size
        tvec, rvec = [], []

        ids = ids.flatten()

        for id in ids:
            if id in tag_layout:
                tag_pose = Pose3d(
                    Translation3d(
                        tag_layout[id][0],
                        tag_layout[id][1],
                        tag_layout[id][2],
                    ),
                    Rotation3d(
                        tag_layout[id][3],
                        tag_layout[id][4],
                        tag_layout[id][5],
                    ))
                
                corner_0 = tag_pose + Transform3d(Translation3d(0, fid_size / 2.0, -fid_size / 2.0), Rotation3d())
                corner_1 = tag_pose + Transform3d(Translation3d(0, -fid_size / 2.0, -fid_size / 2.0), Rotation3d())
                corner_2 = tag_pose + Transform3d(Translation3d(0, -fid_size / 2.0, fid_size / 2.0), Rotation3d())
                corner_3 = tag_pose + Transform3d(Translation3d(0, fid_size / 2.0, fid_size / 2.0), Rotation3d())
                object_points += [
                    wpitocv(corner_0.translation()),
                    wpitocv(corner_1.translation()),
                    wpitocv(corner_2.translation()),
                    wpitocv(corner_3.translation())
                ]

        if len(object_points):
            _, rvec, tvec = cv2.solvePnP(object_points, corners, self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            rvec, tvec = cv2.solvePnPRefineVVS(object_points, corners, self.camera_matrix, self.distortion_coefficient, rvec, tvec)
            print(tvec)
            print(rvec)

            return tvec, rvec
        
        return None, None
