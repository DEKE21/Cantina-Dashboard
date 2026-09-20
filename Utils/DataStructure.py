class TelemetryData:
    def TelemetryData(Data = []):
        teamId = ""
        missionTime =""
        packetCount = 0 
        state = ""
        mechState = ""
        altitude = 0.0
        temp = 0.0
        batteryVoltage = 0.0
        gpsLatitude = 0.0
        gpsLongitude = 0.0 
        gpsSats = 0.0
        gyroR = 0.0 
        gyroP = 0.0
        gyroY = 0.0
        challengeOptionData = 0.0

        KnownPacketOrder = ["TEAM_ID","MISSION_TIME","PACKET_COUNT","STATE","MECH_STATE","ALTITUDE,"
          "TEMP","BATTERY_VOLTAGE","GPS_LATITUDE","GPS_LONGITUDE","GPS_SATS,"
          "GYRO_R","GYRO_P","GYRO_Y","CHALLENGE_OPTION_DATA"][teamId,missionTime,packetCount,state,mechState,altitude,temp,batteryVoltage,gpsLatitude,gpsLongitude,gpsSats,gyroR,gyroP,gyroY,challengeOptionData]


        if(Data != []):
            ParseData(Data)

        def ParseData(arr):

            teamId = arr[0]
            missionTime = arr[1]
            packetCount = round(float(arr[2]))
            pass
        def ConvertType(List):
            
            pass



