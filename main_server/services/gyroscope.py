#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable, TextIO

from ad_types.configuration import ADConfiguration

import threading

from services.sensors.MPU6050 import MPU6050

class Service:
    """
    MPU 6050 gyroscope service
    """

    def __init__(self) -> None:
        self.sensor: MPU6050 = MPU6050()

    def worker(self):
        """
        Thread polling gyroscope data 
        """
        self.running = True
        while self.running:
            ax_ms, ay_ms, az_ms = self.sensor.getAcceleration()
            """Get the acceleration values"""

            self.notify({"ax": ax_ms, "ay": ay_ms, "az": az_ms, "unit": "m/s"})
            """Send the sensor values to the subscribed clients"""

    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> None:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """

        self.notify = callable_async_get
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

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
