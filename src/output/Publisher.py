import ntcore
from typing import Union
import numpy.typing
import logging

from config.Config import Config

class Publisher:

    def __init__(self):
        raise NotImplementedError

    def send(self, pose: numpy.typing.NDArray[numpy.float64], fps: Union[float, None], latency: Union[float, None], tvecs: numpy.typing.NDArray[numpy.float64], ids: numpy.typing.NDArray[numpy.float64]):
        raise NotImplementedError
    
    def sendMsg(self, msg: str):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError

class NTPublisher:

    fps_pub: ntcore.FloatPublisher
    pose_pub: ntcore.DoubleArrayPublisher
    latency_pub: ntcore.DoublePublisher
    tvecs_pub: ntcore.DoubleArrayPublisher
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
        self.pose_pub = table.getDoubleArrayTopic("robot_pose").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.pose_pub.setDefault([])
        self.latency_pub = table.getDoubleTopic("latency").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.latency_pub.setDefault(0)
        self.tvecs_pub = table.getDoubleArrayTopic("tvecs").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.tvecs_pub.setDefault([])
        self.ids_pub = table.getIntegerArrayTopic("ids").publish(ntcore.PubSubOptions(keepDuplicates=True, periodic=0.01))
        self.ids_pub.setDefault([])
        self.msg_pub = table.getStringTopic("_msg").publish()

    def send(self, pose: numpy.typing.NDArray[numpy.float64], fps: Union[float, None], latency: Union[float, None], tvecs: numpy.typing.NDArray[numpy.float64], ids: numpy.typing.NDArray[numpy.float64]):

        if fps is not None:
            self.fps_pub.set(fps)

        if pose is not None and latency is not None and tvecs is not None and ids is not None:
            self.pose_pub.set(pose, ntcore._now())
            self.latency_pub.set(latency * 1000, ntcore._now())
            self.tvecs_pub.set(tvecs.flatten(), ntcore._now())
            self.ids_pub.set(ids.flatten(), ntcore._now())
        else:
            self.pose_pub.set([])
            self.tvecs_pub.set([])
            self.ids_pub.set([])

    def sendMsg(self, msg: str):
        self.msg_pub.set(msg)
            
    def close(self):
        self.fps_pub.close()
        self.pose_pub.close()
        self.tvecs_pub.close()
        self.ids_pub.close()
