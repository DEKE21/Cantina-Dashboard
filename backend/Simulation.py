import random
import serialx
import asyncio
import traceback
from TelemetryData import TelemetryData

data = TelemetryData(
 4,5,3,0,0,5,69.95,5.61,34.74037,-86.576105,3,1.41,0.35,0.2,3.18,3.03,5.02,0,0).ToDict()
BASE_TEMP = 70.0
CX = True
async def tim():
    global data
    while True:
        try:
            data["MissionTime"] += 1
            data["batteryVoltage"] = round(random.uniform(5, 6.4), 2)
            data["gpsSats"] = random.randint(1, 5)

            if data["MissionTime"] >= 5 and data["MechState"] == 0:
                data["State"] = "ASCENT"
                data["accelX"] = round(random.uniform(2, 4), 2)
                data["accelY"] = round(random.uniform(2, 4), 2)
                data["accelZ"] = round(random.uniform(4, 6), 2)
                data["gyroR"] = round(random.uniform(0, 2), 2)
                data["gyroP"] = round(random.uniform(0, 1), 2)
                data["gyroY"] = round(random.uniform(0, 2), 2)
                data["altitude"] += 5
                data["gpsLatitude"]  +=0.01
                data["gpsLongitude"] +=0.01
           #     data["gpsLatitude"] = round(data["gpsLatitude"], 6)
            #    data["gpsLongitude"] = round(data["gpsLongitude"], 6)
                if data["altitude"] >= 500:
                    data["MechState"] = 1
                    data["State"] = "APOGEE"

            elif data["MechState"] == 1:
                data["leftSolarVolts"] = round(random.uniform(1, 2.4), 2)
                data["rightSolarVolts"] = round(random.uniform(1, 2.4), 2)

                if data["altitude"] > 0:
                    data["State"] = "DESCENT"
                    data["altitude"] = max(0, data["altitude"] - 4)
                    data["gpsLatitude"]  +=0.01
                    data["gpsLongitude"] +=0.01
                    data["gpsLatitude"] = round(data["gpsLatitude"], 6)
                    data["gpsLongitude"] = round(data["gpsLongitude"], 6)
                else:
                    data["State"] = "LANDED"

            data["temp"] = round(BASE_TEMP - (data["altitude"] * 0.01), 2)

        except Exception as e:
            print(f"[Error in tim()]: {e}")

        await asyncio.sleep(0.1)


async def read_loop(reader):
    global CX
    while True:
        try:
            incoming = await reader.read(1024)
            if incoming:
                decoded = incoming.decode("utf-8", errors="ignore").strip()
                print(f"\n[Received]: {decoded}")
                if decoded == "CMD CX STOP":
                    CX = False
                elif decoded == "CMD CX START":
                    CX = True
            else:
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[Error in read_loop()]: {e}")
            await asyncio.sleep(1)


async def write_loop(writer):
    global data
    global CX
    while True:
        try:

            data["PacketCount"] += 1
            D = TelemetryData(*data.values())

            p = ""
            if(CX==True):
                p = D.ToCSV()
            

            print("[Sending]:", p.strip())

            if not p.endswith("\n"):
                p += "\n"
            
            writer.write(p.encode("utf-8"))
            await writer.drain()
        except Exception as e:
            print(f"[Error in write_loop()]: {e}")
            traceback.print_exc()

        await asyncio.sleep(0.25)


async def main():
    reader, writer = await serialx.open_serial_connection(url="COM9", baudrate=115200)

    try:
        print("Starting concurrent tasks...")
        await asyncio.gather(
            tim(),
            read_loop(reader),
            write_loop(writer)
        )
    except Exception as e:
        print(f"Main loop crashed with error: {e}")
        traceback.print_exc()
    finally:
        print("Closing Port")
        writer.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user.")