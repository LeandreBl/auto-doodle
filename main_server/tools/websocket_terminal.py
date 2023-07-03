#!/usr/bin/env python3

from __future__ import annotations

import sys

import asyncio
import websockets
import readline
import json
import atexit

readline.parse_and_bind('tab: complete')
try:
    readline.read_history_file(".history")
except:
    pass

atexit.register(readline.write_history_file, ".history")

async def test(port: int):
    async with websockets.connect(f'ws://localhost:{port}') as websocket:
        while True:
            try:
                line = input("> ")
            except:
                return
            await websocket.send(line)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1)
                print("received: ", json.loads(response))
            except:
                pass
 
def main(argv: list[str]) -> int:
    port: int = int(argv[1]) if len(argv) > 1 else 8000
    
    asyncio.get_event_loop().run_until_complete(test(port))

if __name__ == '__main__':
    sys.exit(main(sys.argv))  # next section explains the use of sys.exit
