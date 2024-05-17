"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import cv2
import dataclasses
from datetime import datetime
from threading import Thread, Condition
import subprocess

from config.Config import Config
from output.Publisher import NTPublisher

class Capture:
    def __init__(self) -> None:
        raise NotImplementedError
        
    def getFrame(self, config: Config) -> None:
        raise NotImplementedError
    
    def release(self) -> None:
        raise NotImplementedError
    
    @classmethod
    def configChanged(cls, config_a: Config, config_b: Config) -> bool:
        if config_a == None or config_b == None:
            return True

        remote_a = config_a.remote
        remote_b = config_b.remote

        return remote_a.camera_id != remote_b.camera_id or remote_a.camera_resolution_width != remote_b.camera_resolution_width or remote_a.camera_resolution_height != remote_b.camera_resolution_height or remote_a.camera_auto_exposure != remote_b.camera_auto_exposure or remote_a.camera_exposure != remote_b.camera_exposure or remote_a.camera_gain != remote_b.camera_gain or remote_a.camera_brightness != remote_b.camera_brightness or remote_a.fiducial_size != remote_b.fiducial_size or remote_a.fiducial_layout != remote_b.fiducial_layout
                
class WebcamVideoStream:
    def __init__(self, config: Config, src=0):

        self.cond = Condition()

        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*"MJPG"))
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, config.remote.camera_resolution_height)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, config.remote.camera_resolution_width)
        self.stream.set(cv2.CAP_PROP_FPS, 50)
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, config.remote.camera_auto_exposure)
        self.stream.set(cv2.CAP_PROP_EXPOSURE, config.remote.camera_exposure)
        self.stream.set(cv2.CAP_PROP_GAIN, config.remote.camera_gain)
        self.stream.set(cv2.CAP_PROP_BRIGHTNESS, config.remote.camera_brightness)

        self.grabbed, self.frame = self.stream.read()
        self.has_read = False
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def set(self, propId, value):
        self.stream.set(propId, value)

    def update(self):
        while True:
            if self.stopped:
                return
            
            self.grabbed, self.frame = self.stream.read()

            with self.cond:
                self.has_read = False
                self.cond.notify_all()

    
    def read(self):
        with self.cond:
            while self.has_read:
                self.cond.wait()
            self.has_read = True
            return self.frame
    
    def release(self):
        self.stopped = True
        self.stream.release()

class DefaultCapture(Capture):
    
    video = None
    last_config: Config = None
    publisher: NTPublisher = None

    def __init__(self, publisher: NTPublisher) -> None:
        self.publisher = publisher
        pass
    
    def getFrame(self, config: Config):

        if self.video == None and config != None:
            self.publisher.sendMsg(str(datetime.now()) + " - Starting video capture")
            print(str(datetime.now()) + " - Starting video capture")
            self.video = WebcamVideoStream(config, src=0).start()
            self.publisher.sendMsg(str(datetime.now()) + " - Video capture successfully started")
            print(str(datetime.now()) + " - Video capture successfully started")
            self.last_config = Config(dataclasses.replace(config.local), dataclasses.replace(config.remote))
            if config.local.server_ip != "127.0.0.1": subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "-c", "exposure_absolute=8"])

        return self.video.read()
    
    def release(self) -> None:
        self.publisher.sendMsg(str(datetime.now()) + " - Releasing video capture")
        print(str(datetime.now()) + " - Releasing video capture")
        if self.video != None: self.video.release()
        self.video = None
