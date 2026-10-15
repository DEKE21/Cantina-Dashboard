import asyncio
from websockets.asyncio.server import serve
import numpy
 
from TelemetryData import TelemetryData
import Websocket
import serialx
msg =""
buffer =[]
serInboundbuffer = []
 

async def serialMan():
    while True:
        try:
            async with serialx.async_serial_for_url('COM11',baudrate=115200) as serial:
                print("Connection")
                while True:
                    line = await serial.readline()
                    if(line):
                        global msg
                        buffer.append(line.decode())
                        print(line.decode())
                        serInboundbuffer = Websocket.recvBuffer
                        if(len(serInboundbuffer) > 0):
                             print("Sending message to serial: ", serInboundbuffer[0])
                             await serial.write((serInboundbuffer[0]).encode())
                             serInboundbuffer.pop(0)
                             await asyncio.sleep(0.01)
        except Exception as e:
                print(e)
                             

async def MessageHandler():
    while True:
        if(len(buffer) > 0):
            Websocket.SendMessage(buffer[0])
            message = open("Flight_0004.csv", "a")
            message.write(buffer[0])
            buffer.pop(0)
        await asyncio.sleep(0.01)
        

    
async def main():
    tasks =    asyncio.gather(Websocket.NetworkHandler(),serialMan(),MessageHandler())
    await tasks



asyncio.run(main())