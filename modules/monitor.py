import threading
import socket
from settings import MainProperties
import modules
import asyncio
from websockets import serve
import json


class Monitoring:
    def __init__(self, port):
        self.host = "0.0.0.0"
        self.port = port

    def thread(self):
        print("Monitor thread running")

        async def echo(websocket):
            async for message in websocket:
                try:
                    if "MainProperties" in message and not " = " in message:
                        path = message.replace(
                            "MainProperties", "").replace('"', "'")
                        print(eval(message))
                        await websocket.send(json.dumps({path: eval(message)}))
                    else:
                        exec(message)
                except Exception as e:
                    print(e)

        async def main():
            async with serve(echo, "0.0.0.0", self.port):
                await asyncio.Future()  # run forever

        def initWebServer():
            asyncio.run(main())

        initWebServer()


monitor_module = Monitoring(65432)
threading.Thread(target=monitor_module.thread, daemon=True).start()
