#!/usr/bin/env python3

from __future__ import annotations

import time

import GPIO

from logger.logger import logging

class HCSR04:
    """
    HCSR04 ultrasound sensor
    https://raspberry-lab.fr/Composants/Mesure-de-distance-avec-HC-SR04-Raspberry-Francais/Images/Schema-Branchement-Raspberry-Model.3-HC-SR04.png
    """

    MAX_TICK_TO_STALL: int = 1000
    """Max number of loop iteration before stating that the sensor stalled"""

    MAX_RANGE_HANDLED_METER: float = 4.0
    """Max range handled by the sensor in meter"""

    SOUND_SPEED_IN_AIR_METER_PER_SECOND: float = 331.29
    """Speed of sound in air in meter per second"""

    def __init__(self, trigger_pin: int, echo_pin: int) -> None:
        self.trigger_pin: int = trigger_pin
        self.echo_pin: int = echo_pin
        self.iscancel: bool = False

    def cancel(self) -> None:
        self.iscancel = True

    def setup(self) -> None:
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trigger_pin, False)

    def cleanup(self) -> None:
        GPIO.cleanup(self.trigger_pin)
        GPIO.cleanup(self.echo_pin)

    def getDistanceInMeter(self) -> float:
        GPIO.output(self.trigger_pin, True)
        """Put high state in the trigger GPIO"""

        time.sleep(0.00001)
        """Wait for 10µs"""

        GPIO.output(self.trigger_pin, False)
        """Put low state in the trigger GPIO"""

        counter = 0
        while GPIO.input(self.echo_pin) == 0 and self.iscancel == False:
            """Wait for the ultrasound to be sent"""
            counter += 1
            if counter > MAX_TICK_TO_STALL:
                logging.warning("HCSR-04 sensor stalled")
                return self.getDistanceInMeter()

        start_time: float = time.time()
        """Get the exact time when we sent the ultrasound"""

        counter = 0
        while GPIO.input(self.echo_pin) == 1 and self.iscancel == False:
            """Wait for the ultrasound to be received"""
            counter += 1
            if counter > MAX_TICK_TO_STALL:
                logging.warning("HCSR-04 sensor stalled")
                return self.getDistanceInMeter()

        stop_time: float = time.time()
        """Get the exact time when we received the ultrasound"""

        elapsed_seconds: float = stop_time - start_time
        """Compute the time elapsed between sending and receiving the ultrasound"""

        distance_meter: float = (
            elapsed_seconds * self.SOUND_SPEED_IN_AIR_METER_PER_SECOND) / 2.0
        """
        Compute the distance travelled by the sound
        Multiply the speed of the sound (m/s) by the elapsed time (s)
        Divide the distance by 2 because the sound is making a forward/backward travel
        """

        return distance_meter if distance_meter < self.MAX_RANGE_HANDLED_METER / 2 else self.MAX_RANGE_HANDLED_METER / 2
        """Return the distance but divide the max distance handled by 2 to avoid any hardware problem"""
