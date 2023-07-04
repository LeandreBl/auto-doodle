#!/usr/bin/env python3

from __future__ import annotations

import signal
import datetime
from typing import Callable, TextIO
import subprocess
import os

from ad_types.configuration import ADConfiguration

from logger.logger import logging

class Service:
    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> None:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """
        command: list[str] = ["mjpg_streamer", "-o", "output_http.so -w ./www", "-i", "input_http.so"]
        env = os.environ.copy()
        env["LD_PRELOAD"] = "/usr/local/lib/mjpg-streamer"
        try:
            self.process = subprocess.Popen(command, env=env, shell=True, stderr=log_file, stdout=log_file)
        except Exception as e:
            logging.critical(f'Failed to start camera streaming daemon: {e}')

    def cleanup(self) -> None:
        """
        Function called when the service is unloaded
        """
        self.process.send_signal(signal.SIGINT)
        self.process.wait()

    def post(self, values: dict) -> None:
        """
        Function called when new values are to be used
        """
        pass
