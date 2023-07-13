#!/usr/bin/env python3

from __future__ import annotations


import asyncio
import os
import importlib.util
from typing import Callable, TextIO
import datetime

from ad_types.configuration import ADConfiguration

from logger.logger import logging


class ADServiceTemplate:
    def setup(self, configuration: ADConfiguration, callable_async_get: Callable[[dict], None], log_file: TextIO) -> None:
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
        self.runner_loop = asyncio.get_event_loop()
        try:
            spec = importlib.util.spec_from_file_location(
                service_name, service_filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.service: ADServiceTemplate = module.Service()
            self.logging_file: TextIO = open(os.path.join(configuration.logging_directory, f'{service_name}.log'), 'a')
            logging.info(f"Successfully loaded <{service_name}> service at \"{realpath}\" with logfile at \"{self.logging_file.name}\"")
        except Exception as e:
            self.service = None
            logging.critical(f"Failed to load <{service_name}> service at \"{realpath}\" ({e})")
        self.name: str = service_name
        self.clients = []

    def __del__(self):
        if len(self.clients) != 0:
            self.service.cleanup()

    def __repr__(self) -> str:
        return f'{self.name}'

    async def broadcast(self, event, packet) -> None:
        logging.debug(f"Broadcasting to {len(self.clients)} clients")
        for client in self.clients:
            await client.send(event, packet)

    def __on_event_callable_wrapper(self, values: dict) -> None:
        logging.debug(f"Service <{self.name}> posting {values}...")
        task = self.runner_loop.create_task(self.broadcast("notify_values", {"service": self.name, "values": values}))
        self.runner_loop.run_until_complete(task)
        logging.debug(f"Service <{self.name}> posted {values}")

    def subscribe(self, client) -> bool:
        if client not in self.clients:
            if len(self.clients) == 0:
                logging.info(f"Setting up service <{self.name}>")
                now: datetime.datetime = datetime.datetime.now()
                print(f'[{now.strftime("%Y-%m-%d %H:%M:%S")}] <{self.name}> service started', file=self.logging_file, flush=True)
                status: bool = self.service.setup(self.configuration,
                                   self.__on_event_callable_wrapper, self.logging_file)
                if status == False:
                    logging.critical(f'Could not setup service <{self.name}>')
                    return False
            self.clients.append(client)
            client.subscribe(self)
            return True
        else:
            logging.warning(
                f"{client} is already subscribed to service <{self.name}>")
            return False

    def unsubscribe(self, client) -> bool:
        try:
            self.clients.remove(client)
            client.unsubscribe(self)
            if len(self.clients) == 0:
                logging.info(f"Cleaning up service <{self.name}>")
                self.service.cleanup()
            return True
        except:
            logging.warning(
                f"{client} is not subscribed to service <{self.name}> but tried to unsubscribe")
            return False
