from dataclasses import dataclass,asdict

@dataclass
class TelemetryData(object):
    TeamID: int
    MissionTime: int
    PacketCount: int
    State: str
    MechState: int
    altitude:float
    temp:float
    batteryVoltage:float
    gpsLatitude:float
    gpsLongitude:float
    gpsSats:int
    gyroR:float
    gyroP:float
    gyroY:float
    accelX:float
    accelY:float
    accelZ:float
    leftSolarVolts: float
    rightSolarvolts: float
    def __iter__(self):
        return iter(asdict(self))
    def ToDict(self):
        return asdict(self)

    def ToCSV(self):
        csv =""
        arg = asdict(self)
        for items in self:
            csv+=str(arg[items]) +','
        csv = csv[0:len(csv)-1]
        return csv
    def FromCSV(self,cvs=""):
        seperated = cvs.split(',')
        filtererd =[]
        print(len(seperated))

        if(len(seperated)==19):
            filtererd.append(int(seperated[0]))
            filtererd.append(seperated[1])
            filtererd.append(int(seperated[2]))
            filtererd.append(seperated[3])
            for x in range(4,len(seperated)):
                    if(x != 9):
                        filtererd.append(float(seperated[x]))
                    else:
                        filtererd.append(int(seperated[x]))
        arg = asdict(self)
        it=0
        for m in arg:
            arg[m]= filtererd[it]
            it+=1
        
        return TelemetryData(**arg)


            



            

 