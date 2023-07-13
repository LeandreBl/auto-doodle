#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable, TextIO
import time

from ad_types.configuration import ADConfiguration

from websocket_scheduler.client import ADClient

from logger.logger import logging

import threading

TEMPERATURE_SYSFILE: str = "/sys/class/thermal/thermal_zone0/temp"

class Service:
    def worker(self):
        self.running = True
        while self.running:
            try:
                self.callable({"temperature": 16, "unit": "°C"})
            except Exception as e:
                logging.critical(f"Failed to retrieve temperature from {TEMPERATURE_SYSFILE}: {e}")
            time.sleep(1)

    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> bool:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """
        self.log_file = log_file
        self.callable = callable_async_get
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()
        return True

    def cleanup(self) -> None:
        """
        Function called when the service is unloaded
        """
        self.running = False
        self.thread.join()

    def post(self, values: dict) -> None:
        """
        Function called when new values are to be used
        """
        pass
