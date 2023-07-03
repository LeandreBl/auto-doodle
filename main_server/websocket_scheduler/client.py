#!/usr/bin/env python3

from __future__ import annotations

import websockets

from logger.logger import logging
from ad_types.packets import ADPacket
from service_scheduler.service import ADServiceWrapper


class ADClient:
    def __init__(self, websocket) -> None:
        self.websocket = websocket
        self.subscribed_services: list[ADServiceWrapper] = []
        self.connected = True

    def __del__(self) -> None:
        self.close()

    def __repr__(self) -> str:
        return f'{self.websocket.host}:{self.websocket.port} -- services: {self.subscribed_services}'

    async def unsubscribe(self, service: ADServiceWrapper) -> bool:
        try:
            self.subscribed_services.remove(service)
            return True
        except:
            return False

    async def unsubscribe_all(self) -> None:
        for service in self.subscribed_services:
            await service.unsubscribe(self)
        self.subscribed_services = []

    async def subscribe(self, service: ADServiceWrapper) -> bool:
        if service not in self.subscribed_services:
            self.subscribed_services.append(service)
            return True
        return False

    async def close(self) -> None:
        if self.connected == True:
            self.connected = False
            await self.unsubscribe_all()
            await self.websocket.close()

    async def receive(self) -> ADPacket:
        try:
            frame = await self.websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            await self.close()
            return None
        try:
            return ADPacket(frame)
        except:
            logging.warning(f"Invalid ADPacket format: {frame}")
            await self.close()
            return None

    async def send(self, packet: ADPacket) -> None:
        await self.websocket.send(str(packet))
