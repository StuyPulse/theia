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

class NTPublisher:

    fps_pub: ntcore.FloatPublisher
    latency_pub: ntcore.DoublePublisher
    tvecs_pub: ntcore.DoubleArrayPublisher
    rvecs_pub: ntcore.DoubleArrayPublisher
    ids_pub: ntcore.IntegerArrayPublisher

    msg_pub: ntcore.StringPublisher

    def __init__(self, config: Config):

        instance = ntcore.NetworkTableInstance.getDefault()
        instance.setServerTeam(config.local.team_number)
        instance.setServer(config.local.server_ip, ntcore.NetworkTableInstance.kDefaultPort4)
        instance.startClient4(config.local.device_name)
        table = instance.getTable("/" + config.local.device_name + "/output")
        logging.basicConfig(level=logging.DEBUG)

        self.fps_pub = table.getFloatTopic("fps").publish()
        self.fps_pub.setDefault(0)
        self.latency_pub = table.getDoubleTopic("latency").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.latency_pub.setDefault(0)
        # self.tvecs_pub = table.getDoubleArrayTopic("tvecs").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        # self.tvecs_pub.setDefault([])
        # self.rvecs_pub = table.getDoubleArrayTopic("rvecs").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        # self.rvecs_pub.setDefault([])
        self.tvec_rvec_pub = table.getDoubleArrayTopic("tvec_rvec").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.tvec_rvec_pub.setDefault([])
        self.ids_pub = table.getIntegerArrayTopic("ids").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.ids_pub.setDefault([])
        self.msg_pub = table.getStringTopic("_msg").publish()

    def send(self, fps: Union[float, None], latency: Union[float, None], tvec: numpy.typing.NDArray[numpy.float64], rvec: numpy.typing.NDArray[numpy.float64], ids: numpy.typing.NDArray[numpy.float64]):

        if fps is not None:
            self.fps_pub.set(fps)

        if latency is not None and rvec is not None and tvec is not None and ids is not None:
            self.latency_pub.set(latency * 1000, ntcore._now())
            self.tvec_rvec_pub.set([tvec[0], tvec[1], tvec[2], rvec[0], rvec[1], rvec[2]], ntcore._now())
            # self.tvecs_pub.set(tvec.flatten(), ntcore._now())
            # self.rvecs_pub.set(rvec.flatten(), ntcore._now())
            self.ids_pub.set(ids.flatten(), ntcore._now())
        else:
            # self.tvecs_pub.set([])
            # self.rvecs_pub.set([])
            self.tvec_rvec_pub.set([])
            self.ids_pub.set([])

    def sendMsg(self, msg: str):
        self.msg_pub.set(msg)
            
    def close(self):
        self.fps_pub.close()
        # self.tvecs_pub.close()
        # self.rvecs_pub.close()
        self.tvec_rvec_pub.close()
        self.ids_pub.close()
        self.msg_pub.close()
