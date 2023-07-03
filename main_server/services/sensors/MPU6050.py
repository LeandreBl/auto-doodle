#!/usr/bin/env python3

from __future__ import annotations

import time

import GPIO

from mpu6050 import mpu6050

class MPU6050:
    """
    MPU6050 Accelerometer Gyroscope
    https://www.electronicwings.com/raspberry-pi/mpu6050-accelerometergyroscope-interfacing-with-raspberry-pi
    """
    
    def __init__(self, address: int = 0x68) -> None:
        self.sensor = mpu6050(address)
        
    def getTemperatureCelsius(self) -> float:
        return self.sensor.get_temp()
    
    def getAcceleration(self) -> float, float, float:
        data: dict[str, float] = self.sensor.get_accel_data()
        return data['x'], data['y'], data['z']
    
    def getGyroscope(self) -> float, float, float:
        data: dict[str, float] = self.sensor.get_gyro_data()
        return data['x'], data['y'], data['z']
