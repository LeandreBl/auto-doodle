#!/usr/bin/env python3

from __future__ import annotations

import socketio

from service_scheduler.service import ADServiceWrapper


class ADClient:
    def __init__(self, websocket) -> None:
        print(type(websocket))
        self.websocket = websocket
        self.subscribed_services: list[ADServiceWrapper] = []
        self.connected = True
        self.username = "anonymous"

    def __del__(self) -> None:
        self.close()

    def __repr__(self) -> str:
        return f'{self.username}@{self.websocket.host}:{self.websocket.port}'

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

    async def send(self, event, packet) -> None:
        await self.websocket.emit(event, packet)