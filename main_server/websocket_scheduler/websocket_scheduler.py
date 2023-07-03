#!/usr/bin/env python3

from __future__ import annotations

import asyncio

import websockets
import signal

from ad_types.configuration import ADConfiguration

from logger.logger import logging

from ad_types.packets import ADPacket
from .client import ADClient
from service_scheduler.service_scheduler import ADServiceScheduler

class WebsocketScheduler:
    """Websocket scheduler to parse packets and commands
    """

    def __init__(self, configuration: ADConfiguration) -> None:
        self.server = websockets.serve(
            self.__on_connect, "localhost", configuration.websocket_scheduler_port, logger=logging.getLogger())

        self.clients: list[ADClient] = []

        self.service_scheduler: ADServiceScheduler = ADServiceScheduler(
            configuration)

        self.on_events = {
            "subscribe": self.__on_subscribe,
            "unsubscribe": self.__on_unsubscribe,
        }

    async def __on_subscribe(self, client: ADClient, packet: ADPacket) -> None:
        if not "service_name" in packet:
            logging.warning(f"client {client} missing \"service_name\" key in subscribe packet")
            await client.send(ADPacket("subscribe", error=f"missing \"service_name\" key in packet"))
            return

        service_name: str = packet["service_name"]
        if not await self.service_scheduler.subscribe(service_name, client):
            await client.send(ADPacket("subscribe", error=f"fail to subscribe to service {service_name}"))
        else:
            await client.send(ADPacket("subscribe", message=f"successfully subscribed to service {service_name}"))

    async def __on_unsubscribe(self, client: ADClient, packet: ADPacket) -> None:
        if not "service_name" in packet:
            logging.warning(f"client {client} missing \"service_name\" key in subscribe packet")
            await client.send(ADPacket("subscribe", error=f"missing \"service_name\" key in packet"))
            return

        service_name: str = packet["service_name"]
        if not await self.service_scheduler.unsubscribe(service_name, client):
            await client.send(ADPacket("subscribe", error=f"failed to unsubscribed from service {service_name}"))
        else:
            await client.send(ADPacket("subscribe", message=f"successfully unsubscribed from service {service_name}"))

    def __register_new_client(self, websocket):
        self.clients.append(ADClient(websocket))
        return self.clients[-1]

    async def __event_loop(self, client: ADClient):
        while client.connected:
            packet: ADPacket = await client.receive()
            if packet == None:
                continue
            await self.__on_message(client, packet)
        await self.__on_disconnect(client)

    async def __on_message(self, client: ADClient, packet: ADPacket):
        event: str = packet.event.lower()
        if event in self.on_events:
            await self.on_events[event](client, packet)

    async def __on_disconnect(self, client: ADClient):
        await client.close()

    async def __on_connect(self, websocket):
        client: ADClient = self.__register_new_client(websocket)
        await self.__event_loop(client)

    def start(self) -> None:
        signal.signal(signal.SIGINT, lambda: self.stop())
        logging.info("Websocket scheduler started")
        asyncio.get_event_loop().run_until_complete(self.server)
        try:
            asyncio.get_event_loop().run_forever()
        except:
            pass
        logging.info("Websocket scheduler stopped")
        self.service_scheduler.stop()

    def stop(self) -> None:
        asyncio.get_event_loop().stop()
