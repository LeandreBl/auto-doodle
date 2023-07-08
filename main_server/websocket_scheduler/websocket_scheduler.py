#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import signal

import websockets

from ad_types.configuration import ADConfiguration

from logger.logger import logging

from ad_types.packets import ADPacket
from .client import ADClient
from .packet_scheduler import PacketScheduler
from service_scheduler.service_scheduler import ADServiceScheduler


class WebsocketScheduler:
    """Websocket scheduler to handle packets and commands
    """

    def __init__(self, configuration: ADConfiguration) -> None:
        self.sigint_count: int = 0
        
        self.server = websockets.serve(
            self.__on_connect, "localhost", configuration.websocket_scheduler_port, logger=logging.getLogger())

        self.clients: list[ADClient] = []

        self.service_scheduler: ADServiceScheduler = ADServiceScheduler(
            configuration)

        logging.info(
            f"Scheduler started with {self.service_scheduler} service(s)")

        self.packet_scheduler: PacketScheduler = PacketScheduler()

        self.packet_scheduler.on("subscribe", self.__on_subscribe)
        self.packet_scheduler.on("unsubscribe", self.__on_unsubscribe)
        self.packet_scheduler.on(
            "get_subscriptions", self.__on_get_subscriptions)
        self.packet_scheduler.on("set_username", self.__on_set_username)

    async def __on_set_username(self, client: ADClient, packet: ADPacket) -> None:
        try:
            username: str = packet["username"]
            client.username = username
            await client.send(ADPacket('set_username', message=f"username changed to '{username}'"))
        except:
            await client.send(ADPacket('set_username', error="missing field 'username'"))

    async def __on_get_subscriptions(self, client: ADClient, packet: ADPacket) -> None:
        await client.send(ADPacket('get_subscriptions', subscriptions=[service.name for service in client.subscribed_services]))

    async def __on_subscribe(self, client: ADClient, packet: ADPacket) -> None:
        if not "service_name" in packet:
            logging.warning(
                f"client {client} missing \"service_name\" key in subscribe packet")
            await client.send(ADPacket("subscribe", error=f"missing \"service_name\" key in packet"))
            return

        service_name: str = packet["service_name"]
        if not await self.service_scheduler.subscribe(service_name, client):
            await client.send(ADPacket("subscribe", error=f"fail to subscribe to service {service_name}"))
        else:
            await client.send(ADPacket("subscribe", message=f"successfully subscribed to service {service_name}"))

    async def __on_unsubscribe(self, client: ADClient, packet: ADPacket) -> None:
        if not "service_name" in packet:
            logging.warning(
                f"client {client} missing \"service_name\" key in subscribe packet")
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
            await self.packet_scheduler.trigger(client, packet)
        await self.__on_disconnect(client)

    async def __on_disconnect(self, client: ADClient):
        await client.close()

    async def __on_connect(self, websocket):
        client: ADClient = self.__register_new_client(websocket)
        await self.__event_loop(client)

    def __on_sigint_wrapper_async(self, sig):
        self.sigint_count += 1
        if self.sigint_count > 1:
            exit(1)
        logging.info(
            f'Scheduler received signal [{signal.strsignal(sig)}] signal, stopping the daemon...')
        self.stop()

    def start(self) -> None:
        logging.info("Websocket scheduler started")
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().add_signal_handler(
            signal.SIGINT, lambda: self.__on_sigint_wrapper_async(signal.SIGINT))
        try:
            asyncio.get_event_loop().run_forever()
        except TypeError as e:
            pass
        except Exception as e:
            logging.warning(f"Asyncio poll exited abnormally: {e}")
        logging.info("Websocket scheduler stopped")
        self.service_scheduler.stop()

    def stop(self) -> None:
        asyncio.get_event_loop().stop()
