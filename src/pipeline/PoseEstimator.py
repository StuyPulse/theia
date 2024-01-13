"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import cv2
import numpy
import math
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

        return rvecs, tvecs, rangs
    
def cv2wpi(tvec, rvec):
    return Pose3d(Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]), 
                  Rotation3d(rvec[2][0], -rvec[0][0], -rvec[1][0]))

class CameraPoseEstimator(PoseEstimator):
    def __init__(self):
        numpy.set_printoptions(suppress=True)
        pass

    def process(self, config: Config, rangs, rvecs, tvecs, ids):

        if ids is None or rangs is None or tvecs is None: return None

        tag_layout = config.remote.fiducial_layout
        ids = ids.flatten()
        field_to_camera_ps, field_to_camera_translate, field_to_camera_rotation = [], [], []

        for rvec, tvec, id in zip(rvecs, tvecs, ids):

            field_to_tag, camera_to_tag_p, camera_to_tag, field_to_camera, field_to_camera_p = None, None, None, None, None

            if id in tag_layout:
                field_to_tag = Pose3d(Translation3d(tag_layout[id][0], tag_layout[id][1], tag_layout[id][2]),
                                   Rotation3d(tag_layout[id][3], tag_layout[id][4], tag_layout[id][5]))
                
                camera_to_tag_p =   cv2wpi(tvec, rvec)
                camera_to_tag =     Transform3d(camera_to_tag_p.translation(), camera_to_tag_p.rotation())
                field_to_camera =   field_to_tag.transformBy(camera_to_tag.inverse())
                field_to_camera_p = Pose3d(field_to_camera.translation(), field_to_camera.rotation())

            field_to_camera_translate.append([field_to_camera_p.x, field_to_camera_p.y, field_to_camera_p.z])
            field_to_camera_rotation.append([field_to_camera_p.rotation().x, field_to_camera_p.rotation().y, field_to_camera_p.rotation().z])

        if len(ids) != 0:
            field_to_camera_translate = numpy.array(numpy.mean(numpy.asarray(field_to_camera_translate), axis=0)).tolist()
            field_to_camera_rotation = numpy.array(numpy.mean(numpy.asarray(field_to_camera_rotation), axis=0)).tolist()

            field_to_camera_ps = [field_to_camera_translate[0], field_to_camera_translate[1], field_to_camera_translate[2], field_to_camera_rotation[0], field_to_camera_rotation[1], field_to_camera_rotation[2]]
            return field_to_camera_ps
        return None