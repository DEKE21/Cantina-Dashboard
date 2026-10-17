import asyncio
import json
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

connection = False
messageBuffer = []
recvBuffer = []

async def echo_handler(websocket):
    print("connected")
    global connection # Ensure we update the global variable
    connection = True
    
    # --- TASK 1: Constantly listen for commands from the dashboard ---
    async def receive_from_client():
        try:
            async for message in websocket:
                if message != "ping":
                    print("Received from client:", message)
                    recvBuffer.append(message)
        except ConnectionClosed:
            pass # Handled by the main try/finally block

    # --- TASK 2: Constantly stream telemetry to the dashboard ---
    async def send_to_client():
        try:
            while True:
                if len(messageBuffer) > 0:
                    # Pop all available messages instantly instead of 1 by 1
                    response = messageBuffer.pop(0) 
                    await websocket.send(response)
                else:
                    # Very brief pause to prevent maxing out the CPU loop
                    await asyncio.sleep(0.01) 
        except ConnectionClosed:
            pass

    try:
        # Run both tasks at the exact same time
        await asyncio.gather(receive_from_client(), send_to_client())
    except ConnectionClosed:
        pass
    finally:
        print("Client disconnected. Performing cleanup")
        connection = False

def SendMessage(message):
    messageBuffer.append(message)
    # print("Added", messageBuffer) # Muted to prevent console spam at 4Hz

def IsOpen():
    return connection

def MessagePasser():
    if len(recvBuffer) > 0:
        return recvBuffer[-1]
    return ""

async def NetworkHandler():
    async with serve(echo_handler, "localhost", 8001) as server:
        print("WebSocket server started on ws://localhost:8001")
        await server.serve_forever()