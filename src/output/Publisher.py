"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

"""
ntcore passes non-driver station data to and from the robot across a network
https://github.com/robotpy/pyntcore/tree/main
"""
import ntcore
from typing import Union
import numpy.typing
import logging
from wpimath.geometry import *


from config.Config import Config

class Publisher:
    """
    Initial definition of the functions.
    Raises exceptions if the functions are not implmented
    """

    def __init__(self):
        raise NotImplementedError

    def send(self, fps: Union[float, None], latency: Union[float, None], tvecs: numpy.typing.NDArray[numpy.float64], ids: numpy.typing.NDArray[numpy.float64]):
        raise NotImplementedError
    
    def sendMsg(self, msg: str):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError

def poseToArray(pose: Pose3d):
    #Converts the Pose3D into an array by mapping the XYZ translation and rotation values.
    return [
        pose.translation().X(),
        pose.translation().Y(),
        pose.translation().Z(),
        pose.rotation().X(),
        pose.rotation().Y(),
        pose.rotation().Z()
    ]

class NTPublisher:
    """
    Creates topics (data channels) and publishes values to it
    https://docs.wpilib.org/en/stable/docs/software/networktables/publish-and-subscribe.html
    """

    fps_pub: ntcore.FloatPublisher          #Frames per second
    latency_pub: ntcore.DoublePublisher     #Latency -- Time for data packet to transfer
    tvecs_pub: ntcore.DoubleArrayPublisher  #Translation vectors
    rvecs_pub: ntcore.DoubleArrayPublisher  #Rotation vectors
    tids_pub: ntcore.IntegerArrayPublisher  
    areas_pub: ntcore.DoubleArrayPublisher
    reprojection_error_pub: ntcore.DoublePublisher
    
    msg_pub: ntcore.StringPublisher
    update_counter_pub: ntcore.IntegerPublisher
    counter: int

    def __init__(self, config: Config):
        """
        The self parameter invokes the NetworkTable.
        The config parameter provides information related to the camera.
        """
        # Initializes an instance of a NetworkTable, gets misallenous information, and starts logging
        instance = ntcore.NetworkTableInstance.getDefault()
        instance.setServerTeam(config.local.team_number)
        instance.setServer(config.local.server_ip, ntcore.NetworkTableInstance.kDefaultPort4)
        instance.startClient4(config.local.device_name)
        table = instance.getTable("/" + config.local.device_name + "/output")
        logging.basicConfig(level=logging.DEBUG)

        # Starts publishing data periodically to the NetworkTable and setting items to their default values
        self.fps_pub = table.getFloatTopic("fps").publish()
        self.fps_pub.setDefault(0)
        self.latency_pub = table.getDoubleTopic("latency").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        self.latency_pub.setDefault(0)
        self.tids_pub = table.getIntegerArrayTopic("tids").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        self.tids_pub.setDefault([])
        self.pose_sub = table.getDoubleArrayTopic("pose").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        self.pose_sub.setDefault([])
        self.areas_pub = table.getDoubleArrayTopic("areas").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        self.areas_pub.setDefault([])
        self.reprojection_error_pub = table.getDoubleTopic("reprojection_error").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        self.reprojection_error_pub.setDefault(0)
        self.msg_pub = table.getStringTopic("_msg").publish()
        self.update_counter_pub = table.getIntegerTopic("update_counter").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        
        self.counter = 0

    def send(self, fps: Union[float, None], latency: Union[float, None], tids: Union[list, None], primary_pose: Union[list, None], areas: list, reprojection_error: Union[float, None]):
        """
        Updates the data by setting their value if there's not nothing (aka theres's something).
        Else, it sets values to default (empty array or 0)
        """

        if fps is not None:
            self.fps_pub.set(fps)

        #ntcore._now() returns the current time (used to show when information was updated)
        if latency is not None and tids is not None and primary_pose is not None and len(areas) > 0:
            self.latency_pub.set(latency * 1000, ntcore._now())
            self.tids_pub.set(tids, ntcore._now())
            self.pose_sub.set(poseToArray(primary_pose), ntcore._now())
            self.areas_pub.set(areas, ntcore._now())
            self.update_counter_pub.set(self.counter, ntcore._now())
            self.reprojection_error_pub.set(reprojection_error, ntcore._now())
            self.counter += 1
        else:
            self.tids_pub.set([])
            self.pose_sub.set([])
            self.areas_pub.set([])
            self.reprojection_error_pub.set(0)

    def sendMsg(self, msg: str):
        #sends message (string) to the NetworkTable
        self.msg_pub.set(msg)
            
    def close(self):
        #Stops publishing to the NetworkTable
        self.fps_pub.close()
        self.tids_pub.close()
        self.pose_sub.close()
        self.msg_pub.close()
        self.update_counter_pub.close()
