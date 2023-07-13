#!/usr/bin/env python3

from __future__ import annotations

import uvicorn
import socketio

from ad_types.configuration import ADConfiguration

from logger.logger import logging

from .client import ADClient
from service_scheduler.service_scheduler import ADServiceScheduler


class WebsocketScheduler:
    """Websocket scheduler to handle packets and commands
    """

    def __init__(self, configuration: ADConfiguration) -> None:
        self.server = socketio.AsyncServer(
            logger=logging.getLogger(), async_mode="asgi")

        self.app = socketio.ASGIApp(self.server)

        self.clients: list[ADClient] = []

        self.service_scheduler: ADServiceScheduler = ADServiceScheduler(
            configuration)

        self.configuration = configuration

        logging.info(
            f"Scheduler started with {self.service_scheduler} service(s)")

    def register_callbacks(self):
        @self.server.event
        async def connect(sid, environ):
            client: ADClient = ADClient(sid)
            self.clients.append(client)
            setattr(sid, "client", client)

        @self.server.event
        def disconnect(sid):
            # pop from list
            # client.close()
            pass

        @self.server.event
        async def set_username(sid, data) -> None:
            try:
                username: str = data["username"]
                sid.client.username = username
                await sid.client.send('set_username', {"message": f"username changed to '{username}'"})
            except:
                await sid.client.send('set_username', {"error": "missing field 'username'"})

        @self.server.event
        async def get_subscriptions(sid, data) -> None:
            await sid.client.send('get_subscriptions', {"subscriptions": [service.name for service in sid.client.subscribed_services]})

        @self.server.event
        async def subscribe(sid, data) -> None:
            if not "service_name" in data:
                logging.warning(
                    f"client {sid.client} missing \"service_name\" key in subscribe packet")
                await sid.client.send("subscribe", {"error": f"missing \"service_name\" key in packet"})
                return

            service_name: str = data["service_name"]
            if not await self.service_scheduler.subscribe(service_name, sid.client):
                await sid.client.send("subscribe", {"error": f"fail to subscribe to service {service_name}"})
            else:
                await sid.client.send("subscribe", {"message": f"successfully subscribed to service {service_name}"})

        @self.server.event
        async def on_unsubscribe(sid, data) -> None:
            if not "service_name" in data:
                logging.warning(
                    f"client {sid.client} missing \"service_name\" key in subscribe packet")
                await sid.client.send("subscribe", {"error": f"missing \"service_name\" key in packet"})
                return

            service_name: str = data["service_name"]
            if not await self.service_scheduler.unsubscribe(service_name, sid.client):
                await sid.client.send("subscribe", {"error": f"failed to unsubscribed from service {service_name}"})
            else:
                await sid.client.send("subscribe", {"message": f"successfully unsubscribed from service {service_name}"})

    def start(self) -> None:
        logging.info("Websocket scheduler started")
        self.register_callbacks()
        try:
            uvicorn.run(self.app, host="127.0.0.1", port=self.configuration.websocket_scheduler_port, log_level=self.configuration.logging_level.lower(), ws="websockets")
        except Exception as e:
            logging.warning(f"Application stopped: {e}")
        logging.info("Websocket scheduler stopped")
        self.service_scheduler.stop()

    def stop(self) -> None:
        self.service_scheduler.stop()
        exit(1)
