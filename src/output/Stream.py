"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import socketserver
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

import cv2
from PIL import Image

from config.Config import Config

class StreamServer:

    def start(self, config: Config) -> None:
        """Starts the output stream."""
        raise NotImplementedError

    def set_frame(self, frame: cv2.Mat) -> None:
        """Sets the frame to serve."""
        raise NotImplementedError

class MJPGServer(StreamServer):
    _frame: cv2.Mat
    _has_frame: bool = False

    def _make_handler(self_mjpeg):  # type: ignore
        class StreamingHandler(BaseHTTPRequestHandler):
            HTML = """
                <html>
                    <head>
                        <title>Camera Stream</title>
                        <style>
                            body {
                                min-height: 100vh;
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                justify-content: center;
                                background-color: #001111;
                                font-family: sans-serif;
                            }

                            h1 {
                                color: white;
                                margin: 4rem;
                            }

                            img {
                                width: 80%;
                                max-width: 800px;
                                max-height: 600px;
                            }
                        </style>
                    </head>
                    <body>
                        <img src="stream.mjpg" />
                    </body>
                </html>
            """

            def do_GET(self):
                if self.path == "/":
                    content = self.HTML.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                elif self.path == "/stream.mjpg":
                    self.send_response(200)
                    self.send_header("Age", "0")
                    self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0")
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Content-Type", "multipart/x-mixed-replace;boundary=FRAME")
                    self.end_headers()
                    try:
                        while True:
                            if not self_mjpeg._has_frame:
                                time.sleep(0.1)
                            else:
                                pil_im = Image.fromarray(self_mjpeg._frame)
                                stream = BytesIO()
                                pil_im.save(stream, format="JPEG")
                                frame_data = stream.getvalue()

                                self.wfile.write(b"--FRAME\r\n")
                                self.send_header("Content-Type", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
                                self.send_header("Content-Length", str(len(frame_data)))
                                self.end_headers()
                                self.wfile.write(frame_data)
                                self.wfile.write(b"\r\n")
                    except Exception as e:
                        print("Removed streaming client %s: %s", self.client_address, str(e))
                else:
                    self.send_error(404)
                    self.end_headers()

        return StreamingHandler

    class StreamingServer(socketserver.ThreadingMixIn, HTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    def _run(self, port: int) -> None:
        server = self.StreamingServer((bytes("", "UTF8"), port), self._make_handler())
        server.serve_forever()
        
    def start(self, config: Config) -> None:
        threading.Thread(target=self._run, daemon=True, args=(config.local.stream_port,)).start()
        print(str(datetime.now()) + " - Stream server started on port " + str(config.local.stream_port))

    def set_frame(self, frame: cv2.Mat) -> None:
        self._frame = frame
        self._has_frame = True