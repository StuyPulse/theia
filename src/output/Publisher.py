"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import ntcore
from typing import Union
import numpy.typing
import logging
from wpimath.geometry import *

from config.Config import Config

class Publisher:

    def __init__(self):
        raise NotImplementedError

    def send(self, fps: Union[float, None], latency: Union[float, None], tvecs: numpy.typing.NDArray[numpy.float64], ids: numpy.typing.NDArray[numpy.float64]):
        raise NotImplementedError
    
    def sendMsg(self, msg: str):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError

def poseToArray(pose: Pose3d):
    return [
        pose.translation().X(),
        pose.translation().Y(),
        pose.translation().Z(),
        pose.rotation().X(),
        pose.rotation().Y(),
        pose.rotation().Z()
    ]

class NTPublisher:

    fps_pub: ntcore.FloatPublisher
    latency_pub: ntcore.DoublePublisher
    tvecs_pub: ntcore.DoubleArrayPublisher
    rvecs_pub: ntcore.DoubleArrayPublisher
    tids_pub: ntcore.IntegerArrayPublisher
    areas_pub: ntcore.DoubleArrayPublisher

    msg_pub: ntcore.StringPublisher
    update_counter_pub: ntcore.IntegerPublisher
    counter: int

    def __init__(self, config: Config):

        instance = ntcore.NetworkTableInstance.getDefault()
        instance.setServerTeam(config.local.team_number)
        instance.setServer(config.local.server_ip, ntcore.NetworkTableInstance.kDefaultPort4)
        instance.startClient4(config.local.device_name)
        table = instance.getTable("/" + config.local.device_name + "/output")
        logging.basicConfig(level=logging.DEBUG)

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
        self.msg_pub = table.getStringTopic("_msg").publish()
        self.update_counter_pub = table.getIntegerTopic("update_counter").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.02))
        
        self.counter = 0

    def send(self, fps: Union[float, None], latency: Union[float, None], tids, primary_pose, areas):

        if fps is not None:
            self.fps_pub.set(fps)

        if latency is not None and tids is not None and primary_pose is not None and len(areas) > 0:
            self.latency_pub.set(latency * 1000, ntcore._now())
            self.tids_pub.set(tids, ntcore._now())
            self.pose_sub.set(poseToArray(primary_pose), ntcore._now())
            self.areas_pub.set(areas, ntcore._now())
            self.update_counter_pub.set(self.counter, ntcore._now())
            self.counter += 1
        else:
            self.tids_pub.set([])
            self.pose_sub.set([])
            self.areas_pub.set([])

    def sendMsg(self, msg: str):
        self.msg_pub.set(msg)
            
    def close(self):
        self.fps_pub.close()
        self.tids_pub.close()
        self.pose_sub.close()
        self.msg_pub.close()
        self.update_counter_pub.close()
