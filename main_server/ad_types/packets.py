#!/usr/env python3

from __future__ import annotations

import json


class ADPacket:
    def __init__(self, event_or_string_packet: str, content: dict = None, **kwargs) -> None:
        if content == None:
            try:
                packet = json.loads(event_or_string_packet)
            except:
                self.event = event_or_string_packet.lower()
                self.payload = {
                    **kwargs
                }
                return
            if not "event" in packet:
                raise KeyError('event')
            elif not "payload" in packet:
                self.payload = {}
            else:
                self.payload = packet["payload"]
            self.event = packet["event"].lower()
        else:
            self.event = event_or_string_packet.lower()
            self.payload = {
                **content,
                **kwargs
            }

    def __repr__(self) -> str:
        return json.dumps({"event": self.event, "payload": self.payload})

    def __contains__(self, key) -> bool:
        return key in self.payload

    def __getitem__(self, key):
        return self.payload[key]
