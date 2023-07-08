#!/usr/bin/env python3

from __future__ import annotations

import signal
from typing import Callable, TextIO
import subprocess
import os

from ad_types.configuration import ADConfiguration

from logger.logger import logging

class Service:
    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> bool:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """
        self.log_file: TextIO = log_file

        mjpg_streamer_libpath: str = "/usr/local/lib/mjpg-streamer"

        if not os.path.exists(mjpg_streamer_libpath):
            logging.critical(f'Failed to start camera streaming daemon: mjpeg library at \"{mjpg_streamer_libpath}\" not found')
            return False

        self.command: list[str] = ["mjpg_streamer", "-o", "'output_http.so -w ./www'", "-i", "'input_raspicam.so -x 1920 -y 1080 -fps 30'", "&"]

        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = mjpg_streamer_libpath

        print(f'Starting {self.command[0]} as \"{" ".join(self.command)}\"', file=log_file, flush=True)

        try:
            self.process = subprocess.Popen(self.command, env=env, shell=True, stderr=log_file, stdout=log_file)
            print(f"Process {self.process.pid} started", file=self.log_file, flush=True)
            return True
        except Exception as e:
            logging.critical(f'Failed to start camera streaming daemon: {e}')
            return False

    def cleanup(self) -> None:
        """
        Function called when the service is unloaded
        """

        print(f"Stopping process {self.process.pid}", file=self.log_file, flush=True)
        self.process.send_signal(signal.SIGINT)
        try:
            ret: int = self.process.wait(0.5)
            print(f"Process {self.process.pid} exited with exit code {ret}", file=self.log_file, flush=True)
        except:
            print(f"Process {self.process.pid} takes too long to exit, sending SIGKILL", file=self.log_file, flush=True)
            self.process.kill()
            self.process.wait()
            os.system(f'pkill {self.command[0]}')
            print(f"Process {self.process.pid} killed successfully", file=self.log_file, flush=True)

    def post(self, values: dict) -> None:
        """
        Function called when new values are to be used
        """
        pass
