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

        return numpy.array([numpy.array([roll]), numpy.array([pitch]), numpy.array([yaw])])
    
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
        
        tids = []
        rvecs = []
        tvecs = []
        rangs = []

        for i, tid in enumerate(ids):
            _, rvec, tvec = cv2.solvePnP(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            rvec, tvec = cv2.solvePnPRefineVVS(self.object_points, corners[i], self.camera_matrix, self.distortion_coefficient, rvec, tvec)

            rang, _ = cv2.Rodrigues(rvec) # Convert rotation vector [3x1] to rotation matrix [3x3]
            rang = self.matToEuler(rang)

            tids.append(tid)
            rvecs.append(rvec)
            tvecs.append(tvec)
            rangs.append(rang)

        return numpy.asarray(tids), numpy.asarray(rvecs), numpy.asarray(tvecs), numpy.asarray(rangs)

def rotate_vector(v, roll, pitch, yaw):
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
    cos_pit, sin_pit = math.cos(pitch), math.sin(pitch)
    cos_rol, sin_rol = math.cos(roll), math.sin(roll)
    
    return [
        (cos_yaw * cos_pit) * v[0] + (cos_yaw * sin_pit * sin_rol - sin_yaw * cos_rol) * v[1] + (cos_yaw * sin_pit * cos_rol + sin_yaw * sin_rol) * v[2],
        (sin_yaw * cos_pit) * v[0] + (sin_yaw * sin_pit * sin_rol + cos_yaw * cos_rol) * v[1] + (sin_yaw * sin_pit * cos_rol - cos_yaw * sin_rol) * v[2],
        (-sin_pit) * v[0] + (cos_pit * sin_rol) * v[1] + (cos_pit * cos_rol) * v[2] 
    ]

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

        for rang, tvec, tid in zip(rangs, tvecs, ids):
            if tid in tag_poses:
                # converts from OpenCV 3D coordinate system to wpilib field coordinate system
                wpi_tvecs = [tvec[2], -tvec[0], tvec[1]]
    
                camera_offset = config.remote.camera_offset
                camera_offset = rotate_vector(camera_offset[:3], -camera_offset[3], -camera_offset[4], -camera_offset[5])

                wpi_tvecs = [
                    wpi_tvecs[0] - camera_offset[0],
                    wpi_tvecs[1] - camera_offset[1],
                    wpi_tvecs[2] - camera_offset[2],
                ]

                # Yaw Correction
                camera_rangs = [
                    tag_poses[tid][3] - rang[0],
                    tag_poses[tid][4] - rang[1],
                    tag_poses[tid][5] - rang[2],
                ]
                rotated_tvecs = rotate_vector(wpi_tvecs, camera_rangs[0], camera_rangs[1], camera_rangs[2])

                camera_offset = config.remote.camera_offset
                robot_rang = [
                        tag_poses[tid][3] - rang[0] - camera_offset[3],
                        tag_poses[tid][4] - rang[1] - camera_offset[4],
                        tag_poses[tid][5] - rang[2] - camera_offset[5]
                    ]
                
                alltvecs.append([tag_poses[tid][0] - rotated_tvecs[0],
                                 tag_poses[tid][1] - rotated_tvecs[1],
                                 tag_poses[tid][2] - rotated_tvecs[2]])
                allrangs.append(robot_rang)

        if len(alltvecs) != 0 and len(allrangs) != 0:
            alltvecs = numpy.concatenate(numpy.mean(alltvecs, axis=0))
            allrangs = numpy.concatenate(numpy.mean(allrangs, axis=0))
            robot_pose = []
            robot_pose.append(alltvecs)
            robot_pose.append(allrangs)
            robot_pose = numpy.concatenate(robot_pose)

            return robot_pose
        return None

if __name__ == '__main__':
    camera_offset = []
    print()
