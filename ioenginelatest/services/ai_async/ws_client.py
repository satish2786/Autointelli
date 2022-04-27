import asyncio
import websockets
import json


async def sendevents():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        #name = {'ciname' : 'testserver', 'severity': 'critical', 'description':  'Test description', 'notes': 'This is test notes'}
        name = {'msg_updated_time': '11-30-2021 12:13:20', 'customer_id': 'IRESS', 'priority': 'High', 'machine': 'appvm1', 'application': 'DRFinancialAPP', 'value': '1', 'cmdline': 'test', 'description': 'telnet 8.8.8.8 Server', 'extra_description': 'This is Extra Descriptio', 'severity': 'CRITICAL', 'source': 'AUTOINTELLI', 'event_created_time': 1640852559.48775, 'id': '1', 'asset_number': '1', 'region': 'APAC', 'asset_state': '1', 'version': '1', 'package': '1', 'pac_ver': '1', 'pac_ver_no': '1', 'msg_created_time': '11-30-2021 12:13:20', 'status_update': '1', 'additional_props': {}, 'modified_by': 'Anand'}

        await websocket.send(json.dumps(name))
        print(f">>> {name}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")

if __name__ == "__main__":
    asyncio.run(sendevents())
