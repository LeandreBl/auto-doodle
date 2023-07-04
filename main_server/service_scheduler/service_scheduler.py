#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable

from ad_types.configuration import ADConfiguration
from ad_types.packets import ADPacket
from utils.utils import get_matching_filenames_in_directory
from logger.logger import logging
from .service import ADServiceWrapper
from websocket_scheduler.client import ADClient


class ADServiceScheduler:
    def __init__(self, configuration: ADConfiguration) -> None:
        files: list[str] = get_matching_filenames_in_directory(
            configuration.services_directory_path, ".py")
        self.services: dict[str, ADServiceWrapper] = {
            i.name: i for i in filter(lambda x: x.service != None, map(lambda file: ADServiceWrapper(file, configuration), files))}

    def __repr__(self) -> str:
        return f"{[*self.services.keys()]}"

    def stop(self) -> None:
        logging.info("Cleaning up all services")
        for name, service in self.services.items():
            if len(service.clients) != 0:
                logging.info(f"Cleaning up service <{name}>")
                service.service.cleanup()
        self.services = []
        logging.info("Successfully cleaned up all services")

    async def subscribe(self, service_name: str, client: ADClient) -> bool:
        if service_name not in self.services:
            logging.warning(
                f"Client {client} tried to subscribe to non existing service {service_name}")
            return False
        logging.debug(f"{client} subscribing to <{service_name}> ...")
        if not await self.services[service_name].subscribe(client):
            return False
        else:
            logging.info(f"{client} subscribed to <{service_name}>")
            return True

    async def unsubscribe(self, service_name: str, client: ADClient) -> bool:
        if service_name not in self.services:
            logging.warning(
                f"Client {client} tried to unsubscribe to non existing service {service_name}")
            return False
        logging.debug(f"{client} unsubscribing from <{service_name}> ...")
        if not await self.services[service_name].unsubscribe(client):
            return False
        else:
            logging.info(f"{client} unsubscribed from <{service_name}>")
            return True
