import numpy as np
import math

# stores all angles in radians
class Pose3d:
    def poses_to_tvecs(poses: list) -> list:
        print(poses is None)
        return [pose.tvec() for pose in poses]

    def poses_to_rangs(poses: list) -> list:
        return [pose.rang() for pose in poses]

    # DOUBLE CHECK THIS
    # NOT SURE IF Z SHOULD BE NEGATED
    def from_cv2_pose(tvec, rang):
        return Pose3d(
            tvec[2], -tvec[0], -tvec[1],
            math.radians(rang[0]), math.radians(rang[1]), math.radians(-rang[2])
        )

    def __init__(self, x: float, y: float, z: float, roll: float, pitch: float, yaw: float):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
    
    def rotate_2d(self, rad: float):
        return Pose3d(
            self.x * math.cos(rad) - self.y * math.sin(rad),
            self.x * math.sin(rad) + self.y * math.cos(rad),
            self.z,
            self.roll,
            self.pitch,
            self.yaw + rad
        )
    
    def tvec(self):
        print(self.as_cv2() is None)
        return self.as_cv2()[:3]

    def rvec(self):
        return np.array(list(map(math.degrees, self.as_cv2()[3:])))

    def as_cv2(self) -> list:
        print(list(map(type, [self.y, -self.z, self.x, self.roll, self.pitch, -self.yaw])))
        return np.array([self.y, -self.z, self.x, self.roll, self.pitch, -self.yaw])

    def as_robot_pose(self) -> list:
        return np.array([self.x, self.y, self.z, self.roll, self.pitch, self.yaw])

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'[x: {self.x}, y: {self.y}, z: {self.z}, roll: {math.degrees(self.roll)}, pitch: {math.degrees(self.pitch)}, yaw: {math.degrees(self.yaw)}]'
