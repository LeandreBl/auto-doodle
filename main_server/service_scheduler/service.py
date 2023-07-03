#!/usr/bin/env python3

from __future__ import annotations


from typing import Callable
import asyncio
import os
import importlib.util

from ad_types.configuration import ADConfiguration
from ad_types.packets import ADPacket

from logger.logger import logging


class ADServiceTemplate:
    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None] = None) -> None:
        """
        Function called the first time the service is loaded
        the passed callable_async_get is a function that should be called whenever new values are ready
        """
        pass

    def cleanup(self) -> None:
        """
        Function called when the service is unloaded
        """
        pass

    def post(self, values: dict) -> None:
        """
        Function called when new values are to be used
        """
        pass


class ADServiceWrapper:
    def __init__(self, service_filepath: str, configuration: ADConfiguration) -> None:
        self.configuration = configuration
        realpath: str = os.path.realpath(service_filepath)
        filename: str = os.path.basename(service_filepath)
        service_name, _ = os.path.splitext(filename)
        try:
            spec = importlib.util.spec_from_file_location(
                service_name, service_filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.service: ADServiceTemplate = module.Service()
            logging.info(f"{realpath} module loaded successfully")
        except:
            logging.exception(f"Failed to load module file {realpath}")
        self.name: str = service_name
        self.clients = []

    def __del__(self):
        if len(self.clients) != 0:
            self.service.cleanup()

    def __repr__(self) -> str:
        return f'{self.name} - {self.clients}'

    async def broadcast(self, packet: ADPacket) -> None:
        for client in self.clients:
            await client.send(packet)

    def __on_event_callable_wrapper(self, values: dict) -> None:
        logging.debug(f"service {self.name} posts {values}")
        asyncio.run(self.broadcast(
            ADPacket("notify_values", service=self.name, values=values)))

    async def subscribe(self, client) -> bool:
        if client not in self.clients:
            if len(self.clients) == 0:
                logging.info(f"Setting up service {self.name}")
                self.service.setup(self.configuration,
                                   self.__on_event_callable_wrapper)
            self.clients.append(client)
            await client.subscribe(self)
            return True
        else:
            logging.warning(
                f"{client} is already subscribed to service {self.name}")
            return False

    async def unsubscribe(self, client) -> bool:
        try:
            self.clients.remove(client)
            await client.unsubscribe(self)
            if len(self.clients) == 0:
                self.service.cleanup()
            return True
        except:
            logging.warning(
                f"{client} is not subscribed to service {self.name} but tried to unsubscribe")
            return False
