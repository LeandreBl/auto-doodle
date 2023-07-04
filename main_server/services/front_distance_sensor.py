#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable, TextIO

from ad_types.configuration import ADConfiguration

import threading

from services.sensors.HCSR04 import HCSR04

TRIGGER_GPIO_PIN: int = 23
"""Trigger GPIO pin"""

ECHO_GPIO_PIN: int = 24
"""Echo GPIO pin"""

class Service:
    """
    HC SR04 ultrasound sensor service
    """

    def __init__(self) -> None:
        self.sensor: HCSR04 = HCSR04(TRIGGER_GPIO_PIN, ECHO_GPIO_PIN)

    def worker(self):
        """
        Thread sending ultrasounds and counting the time
        they take to come back to get the distance
        """
        self.running = True
        while self.running:
            distance_in_meter: float = self.sensor.getDistanceInMeter()
            """Get the distance from the sensor"""

            self.notify({"distance": distance_in_meter, "unit": "m"})
            """Send the sensor values to the subscribed clients"""

    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> None:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """

        self.sensor.setup()

        self.notify = callable_async_get
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def cleanup(self) -> None:
        """
        Function called when the service is unloaded
        """
        self.running = False
        self.thread.join()
        self.sensor.cleanup()

    def post(self, values: dict) -> None:
        """
        Function called when new values are to be used
        """
        pass
