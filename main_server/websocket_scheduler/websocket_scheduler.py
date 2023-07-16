#!/usr/bin/env python3

from __future__ import annotations

import uvicorn
import socketio
import asyncio

from ad_types.configuration import ADConfiguration

from logger.logger import logging, LOG_FORMAT

from .client import ADClient
from service_scheduler.service_scheduler import ADServiceScheduler


class WebsocketScheduler:
    """Websocket scheduler to handle packets and commands
    """

    def __init__(self, configuration: ADConfiguration) -> None:
        self.server = socketio.AsyncServer(
            logger=logging.getLogger(), async_mode="asgi")

        self.app = socketio.ASGIApp(self.server)

        self.clients: dict[str, ADClient] = {}

        self.service_scheduler: ADServiceScheduler = ADServiceScheduler(
            configuration)

        self.configuration = configuration

        logging.info(
            f"Scheduler started with {self.service_scheduler} service(s)")

    def client_from_sid(self, sid: str) -> ADClient:
        return self.clients[sid]

    def register_callbacks(self):
        @self.server.event
        async def connect(sid, environ):
            client: ADClient = ADClient(sid, self.server)
            self.clients[sid] = client

        @self.server.event
        def disconnect(sid):
            client: ADClient = self.client_from_sid(sid)
            client.close()
            self.clients.pop(sid)

        @self.server.event
        async def set_username(sid, data) -> None:
            client: ADClient = self.client_from_sid(sid)
            try:
                username: str = data["username"]
                client.username = username
                await client.send('set_username', {"message": f"username changed to '{username}'"})
            except:
                await client.send('set_username', {"error": "missing field 'username'"})

        @self.server.event
        async def get_subscriptions(sid, data) -> None:
            client: ADClient = self.client_from_sid(sid)
            await client.send('get_subscriptions', {"subscriptions": [service.name for service in client.subscribed_services]})

        @self.server.event
        async def subscribe(sid, data) -> None:
            client: ADClient = self.client_from_sid(sid)
            if not "service_name" in data:
                logging.warning(
                    f"client {sid.client} missing \"service_name\" key in subscribe packet")
                await client.send("subscribe", {"error": f"missing \"service_name\" key in packet"})
                return

            service_name: str = data["service_name"]
            if not await self.service_scheduler.subscribe(service_name, client):
                await client.send("subscribe", {"error": f"fail to subscribe to service {service_name}"})
            else:
                await client.send("subscribe", {"message": f"successfully subscribed to service {service_name}"})

        @self.server.event
        async def on_unsubscribe(sid, data) -> None:
            client: ADClient = self.client_from_sid(sid)
            if not "service_name" in data:
                logging.warning(
                    f"client {sid.client} missing \"service_name\" key in subscribe packet")
                await sid.client.send("subscribe", {"error": f"missing \"service_name\" key in packet"})
                return

            service_name: str = data["service_name"]
            if not await self.service_scheduler.unsubscribe(service_name, client):
                await client.send("subscribe", {"error": f"failed to unsubscribed from service {service_name}"})
            else:
                await client.send("subscribe", {"message": f"successfully unsubscribed from service {service_name}"})

    def start(self) -> None:
        logging.info("Websocket scheduler started")
        self.register_callbacks()
        try:
            log_config = uvicorn.config.LOGGING_CONFIG
            log_config["formatters"]["access"]["fmt"] = LOG_FORMAT
            log_config["formatters"]["default"]["fmt"] = LOG_FORMAT
            uvicorn.run(self.app, host="127.0.0.1", port=self.configuration.websocket_scheduler_port, log_level=self.configuration.logging_level.lower(), ws="websockets", log_config=log_config)
        except Exception as e:
            logging.warning(f"Application stopped: {e}")
        logging.info("Websocket scheduler stopped")
        self.service_scheduler.stop()
