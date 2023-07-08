#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable, TextIO
import os
import importlib.util
import time

from ad_types.configuration import ADConfiguration

from websocket_scheduler.client import ADClient

from logger.logger import logging

import threading


class Service:
    def loop(self):
        self.running = True
        while self.running:
            time.sleep(1)
            self.callable({"cm": 35})

    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> bool:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """
        self.callable = callable_async_get
        self.thread = threading.Thread(target=self.loop)
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
