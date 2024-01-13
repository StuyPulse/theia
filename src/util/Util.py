
import math
import numpy

from wpimath.geometry import *

def opencv_to_wpilib(tvec: numpy.typing.NDArray[numpy.float64], rvec: numpy.typing.NDArray[numpy.float64]) -> Pose3d:
    return Pose3d(
        Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]),
        Rotation3d(
            numpy.array([rvec[2][0], -rvec[0][0], -rvec[1][0]]),
            math.sqrt(math.pow(rvec[0][0], 2) + math.pow(rvec[1][0], 2) + math.pow(rvec[2][0], 2))
        ))

def average_pose3ds(poses: list[Pose3d]) -> Pose3d:
    sum = Pose3d()

    for pose in poses:
        sum += pose
    
    return sum / len(poses)
