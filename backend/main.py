import asyncio
from websockets.asyncio.server import serve
import numpy
 
from TelemetryData import TelemetryData
import Websocket
import serialx
msg =""
buffer =["0,1,0,boot,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"]
serInboundbuffer = []
 
async def read(read,buffer):
    async with read:
        print(read.readline())
async def serialMan():
    while True:
        try:
            async with serialx.async_serial_for_url('COM10',baudrate=115200) as serial:
                print("Connection")
                while True:
                    line = await serial.readline( )
                    print("no")
                    if(line):
                        global msg
                        buffer.append(line.decode())
                        print(line.decode())
                        await MessageHandler()
                        serInboundbuffer = Websocket.recvBuffer
                        if(len(serInboundbuffer) > 0):
                             print("Sending message to serial: ", serInboundbuffer[0])
                             await serial.write ((serInboundbuffer[0]+"\n").encode())
                             serInboundbuffer.pop(0)
                             
                             await asyncio.sleep(0.25)
                            

                        



        except Exception as e:
                print(e)
                #print('bad')

async def MessageHandler():
    
        if(len(buffer) > 0):
            Websocket.SendMessage(buffer[0])
            buffer.pop(0)
            await asyncio.sleep(0.25)

    
async def main():
    line =""
    telem =  TelemetryData(4,10,100,"st",0,100,1,2,3,4,5,6,7,8,9,1,2,3,4)
    tem = "0,1,0,t,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    buffer = []
    tasks =    asyncio.gather(Websocket.NetworkHandler(),serialMan())
    await tasks



asyncio.run(main())