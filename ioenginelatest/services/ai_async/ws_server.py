#!/usr/local/bin/python3.9

import asyncio
import websockets
from services.utils.ConnMQ import send2MQ
import json

async def receiveevents(websocket):
    data = await websocket.recv()
    try:
      data = json.loads(data) 
      print(">>>" + str(data))
      send2MQ('datalake','EVM', 'datalake',json.dumps(data))
      response = {'type': 'success'}
      await websocket.send(json.dumps(response))
      print(response)
      print("----------")
    except:
      print(">>>" + str(data))
      response = {'type': 'failure', 'result': 'Data is not a json object'}
      await websocket.send(json.dumps(response))
      print("----------")


async def main():
    async with websockets.serve(receiveevents, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
