#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable

from ad_types.packets import ADPacket
from .client import ADClient

class PacketScheduler:
    """Packet scheduler to parse packets and commands
    """

    def __init__(self) -> None:
        self.reactions: dict[str, Callable[[ADClient, ADPacket], None]] = {}
    
    def on(self, event: str, callback: Callable[[ADClient, ADPacket], None]) -> None:
        self.reactions[event] = callback
        
    async def trigger(self, client: ADClient, packet: ADPacket) -> bool:
        event: str = packet.event
        if event not in self.reactions:
            return False
        await self.reactions[event](client, packet)
        return True