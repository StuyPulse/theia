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

def cvtowpi(tvec, rvec):
    return Pose3d(Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]),
                  Rotation3d(
                      (rvec[2][0], -rvec[0][0], -rvec[1][0]),
                      (rvec[2][0]**2 + rvec[0][0]**2 + rvec[1][0]**2)**0.5))

def wpitocv(translation):
    return [-translation.Y(), -translation.Z(), translation.X()]

class FiducialPoseEstimator(PoseEstimator):

    fiducial_size = 0.0
    camera_matrix = None
    distortion_coefficient = None

    def __init__(self, config: Config):
        self.camera_matrix = config.local.camera_matrix
        self.distortion_coefficient = config.local.distortion_coefficient
    
    def process(self, fiducial, config: Config):

        if fiducial is None or len(fiducial) == 0: return (None, None, None)

        object_points = []
        image_points = []
        tag_ids = []
        tag_poses = []

        tag_layout = config.remote.fiducial_layout
        fid_size = config.remote.fiducial_size

        for tid, corners in fiducial:
            if tid in tag_layout:
                tag_pose = Pose3d(
                    Translation3d(
                        tag_layout[tid][0],
                        tag_layout[tid][1],
                        tag_layout[tid][2],
                    ),
                    Rotation3d(
                        tag_layout[tid][3],
                        tag_layout[tid][4],
                        tag_layout[tid][5],
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

                image_points += [
                    [corners[0][0][0], corners[0][0][1]],
                    [corners[0][1][0], corners[0][1][1]],
                    [corners[0][2][0], corners[0][2][1]],
                    [corners[0][3][0], corners[0][3][1]]
                ]

                tag_ids += [tid]
                tag_poses += [tag_pose]

        if len(tag_ids) == 1:
            object_points = numpy.array([[-fid_size / 2.0, fid_size / 2.0, 0.0],
                                         [fid_size / 2.0, fid_size / 2.0, 0.0],
                                         [fid_size / 2.0, -fid_size / 2.0, 0.0],
                                         [-fid_size / 2.0, -fid_size / 2.0, 0.0]])
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(object_points, numpy.array(image_points),
                                                              self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            except:
                return (None, None, None)
        
            # Calculate WPILib camera poses
            field_to_tag_pose = tag_poses[0]
            camera_to_tag_pose_0 = cvtowpi(tvecs[0], rvecs[0])
            camera_to_tag_pose_1 = cvtowpi(tvecs[1], rvecs[1])
            camera_to_tag_0 = Transform3d(camera_to_tag_pose_0.translation(), camera_to_tag_pose_0.rotation())
            camera_to_tag_1 = Transform3d(camera_to_tag_pose_1.translation(), camera_to_tag_pose_1.rotation())
            field_to_camera_0 = field_to_tag_pose.transformBy(camera_to_tag_0.inverse())
            field_to_camera_1 = field_to_tag_pose.transformBy(camera_to_tag_1.inverse())
            field_to_camera_pose_0 = Pose3d(field_to_camera_0.translation(), field_to_camera_0.rotation())
            field_to_camera_pose_1 = Pose3d(field_to_camera_1.translation(), field_to_camera_1.rotation())

            if errors[0][0] < errors[1][0] * 0.15: 
                return (tag_ids, field_to_camera_pose_0, errors[0][0])
            if errors[1][0] < errors[0][0] * 0.15: 
                return (tag_ids, field_to_camera_pose_1, errors[1][0])
            
            return (None, None, None)
        
        # Multi-tag, return one pose
        else:
            # Run SolvePNP with all tags
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(numpy.array(object_points), numpy.array(image_points),
                                                              self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_SQPNP)
            except:
                return (None, None, None)

            # Calculate WPILib camera pose
            camera_to_field_pose = cvtowpi(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())

            return (tag_ids, field_to_camera_pose, errors[0][0])
