import ntcore
from typing import Union
import numpy.typing

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
    tvecs_pub: ntcore.DoubleArrayPublisher
    ids_pub: ntcore.IntegerArrayPublisher

    msg_pub: ntcore.StringPublisher

    def __init__(self, config: Config):

        instance = ntcore.NetworkTableInstance.getDefault()
        instance.setServerTeam(config.local.team_number)
        instance.setServer(config.local.server_ip, ntcore.NetworkTableInstance.kDefaultPort4)
        instance.startClient4(config.local.device_name)
        table = instance.getTable("/" + config.local.device_name + "/output")

        self.fps_pub = table.getFloatTopic("fps").publish()
        self.fps_pub.setDefault(-1)
        self.pose_pub = table.getDoubleArrayTopic("robot_pose").publish(ntcore.PubSubOptions(keepDuplicates=True, pollStorage=10, periodic=0.02))
        self.pose_pub.setDefault([])
        self.tvecs_pub = table.getDoubleArrayTopic("tvecs").publish(ntcore.PubSubOptions(keepDuplicates=True, pollStorage=10, periodic=0.02))
        self.tvecs_pub.setDefault([])
        self.ids_pub = table.getIntegerArrayTopic("ids").publish(ntcore.PubSubOptions(keepDuplicates=True, pollStorage=10, periodic=0.02))
        self.ids_pub.setDefault([])

        self.msg_pub = table.getStringTopic("_msg").publish()

    def send(self, pose: numpy.typing.NDArray[numpy.float64], fps: Union[float, None], latency: Union[float, None], tvecs: numpy.typing.NDArray[numpy.float64], ids: numpy.typing.NDArray[numpy.float64]):
        
        if fps is not None:
            self.fps_pub.set(fps)

        if pose is not None and latency is not None:
            pose = numpy.insert(pose, pose.size, latency * 1000)
            self.pose_pub.set(pose, ntcore._now())
        else: 
            self.pose_pub.set([], ntcore._now())
        
        if tvecs is not None:
            self.tvecs_pub.set(tvecs.flatten(), ntcore._now())

        if ids is not None:
            self.ids_pub.set(ids.flatten(), ntcore._now())

    def sendMsg(self, msg: str):
        self.msg_pub.set(msg)
            
    def close(self):
        self.fps_pub.close()
        self.pose_pub.close()
        self.tvecs_pub.close()
        self.ids_pub.close()
