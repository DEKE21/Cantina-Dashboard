import asyncio
import json
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

connection =False
messageBuffer = ["1","2","3"]
recvBuffer = []
async def echo_handler(websocket):
    print("connected")
    connection = True
    try:
     async for message in websocket:
        print("Received from client:", message)
        if(message != "ping"):
            recvBuffer.append(message)
        response = ""
        if(len(messageBuffer)!=0):
            response = messageBuffer.pop(0)

            await websocket.send(response)
            #print("Sent: ",response)

    except ConnectionClosed:
        print("Client disconnected.")
        connection = False
    finally:
        print("Performing cleanup")
def SendMessage(message):
    messageBuffer.append(message)
   # print("Added", messageBuffer)
def IsOpen():
    return connection
def MessagePasser():
    return recvBuffer[-1]
async def NetworkHandler():
    async with serve(echo_handler, "localhost", 8001) as server:
        print("WebSocket server started on ws://localhost:8001")
        await server.serve_forever()  

 