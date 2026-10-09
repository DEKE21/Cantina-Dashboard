import random
import serialx
import asyncio
from TelemetryData import TelemetryData
missionTime =0
data = TelemetryData(4,0,0,"LAUNCH_PAD",0,0,70,6,-86.382,34.7250,1,0,0,0,0,0,0,0,0).ToDict()

async def tim():
    global data
    while True:
     data["MissionTime"]+=1
     data["PacketCount"] +=1
     data['temp'] -= (data["altitude"] *0.01)
     data["batteryVoltage"] = round(random.uniform(5,6.4),2)
     data["gpsSats"] = random.randint(1,5)
     if(data["MissionTime"]>=5 and data["MissionTime"] <120):
            data["accelX"] = round(random.uniform(2,4),2)
            data["accelY"] = round(random.uniform(2,4),2)
            data["accelZ"] = round(random.uniform(4,6),2)
            data["gyroR"] =  round(random.uniform(0,2),2)
            data["gyroP"] =  round(random.uniform(0,1),2)
            data["gyroY"] =  round(random.uniform(0,2),2)
            data["State"] = "ASCENT"
            data["altitude"] += 5
            data["gpsLatitude"] = round(data["gpsLatitude"]+0.01,4)
            data["gpsLongitude"] = round(data["gpsLongitude"]+0.01,4)

     if(data["altitude"] >= 500 and data["State"] == "ASCENT"):
            data["accelX"] = round(random.uniform(2,4),2)
            data["accelY"] = round(random.uniform(2,4),2)
            data["accelZ"] = round(random.uniform(4,6),2)
            data["gyroR"] =  round(random.uniform(0,2),2)
            data["gyroP"] =  round(random.uniform(0,1),2)
            data["gyroY"] =  round(random.uniform(0,2),2)
            data["MechState"] = 1
            data["State"] = "APTOGE"
     if(data["MissionTime"] >=200 or data["MechState"]==1 ):
            data["leftSolarVolts"] = round(random.uniform(1,2.4),2)
            data["rightSolarvolts"] = round(random.uniform(1,2.4),2)

          
            data["altitude"] -= 4
            data["gpsLatitude"] +=0.02
            data["gpsLongitude"] +=0.02


     

     await asyncio.sleep(0.1)
    

async def read_loop(serial):
    while True:
        data = await serial.readline()

        if data:
            print("Received data:")
            data = data.decode('utf-8', errors='ignore')
            print(f"\n[Received]: {data}")
        await asyncio.sleep(1) 
    

async def write_loop(writer):
    """Sends a message every 2 seconds."""
    while True:
        print("[Sending]: ping")
        p ="ping\n"
        writer.write(p.encode('utf-8'))
        await writer.drain()
        await asyncio.sleep(1) 

async def main():
         reader, writer = await serialx.open_serial_connection(url="COM9", baudrate=115200)

         try:
             print("Starting concurrent tasks...")
             await asyncio.gather(
                 tim(), 
                 read_loop(reader), 
                 write_loop(writer)
             )
         finally:
             print("Closing Port")
             writer.close()
             await writer.wait_closed()     

             
    
     

asyncio.run(main())
 