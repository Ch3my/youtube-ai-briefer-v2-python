import asyncio
import websockets
import json

from build_video_data import build_video_data
from globals import Globals
from query_rag import query_rag

globals = Globals()


async def handle_connection(websocket):
    # Register the new client
    # Test Video: https://www.youtube.com/watch?v=XOqGDLy1IGU
    globals.connected_clients.add(websocket)
    try:
        while True:
            # Receive message from client
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("action") == "build":
                # Esto nos ayuda a que no se bloquee el WS, ademas
                # las funciones adentro de aqui pueden usar await para enviar mensajes via WS
                asyncio.create_task(handle_build(data))
            elif data.get("action") == "query":
                asyncio.create_task(handle_query(data))

            # # Send response back to client
            # response_data = {
            #     "status": "ok",
            #     "message": "Action processed",
            #     "received_data": data,
            # }
            # await websocket.send(json.dumps(response_data))

    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        # Unregister the client on disconnect
        globals.connected_clients.remove(websocket)


async def handle_build(data):
    await build_video_data(data)


async def handle_query(data):
    # TODO. Check query is defined
    await query_rag(data.get("query"))


# Start WebSocket server
start_server = websockets.serve(handle_connection, "localhost", 12345)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on ws://localhost:12345")
asyncio.get_event_loop().run_forever()
