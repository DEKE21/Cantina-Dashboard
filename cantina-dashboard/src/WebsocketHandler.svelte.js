class TelemetryData {
  constructor() {
    this.TEAM_ID = 0;
    this.MISSION_TIME = 0.00;
    this.PACKET_COUNT = 0;
    this.STATE = '';
    this.MECH_STATE = '';
    this.ALTITUDE = 0;
    this.TEMP = 0;
    this.BATTERY_VOLTAGE = 0;
    this.GPS_LATITUDE = 0;
    this.GPS_LONGITUDE = 0;
    this.GPS_SATS = 0;
    this.GYRO_R = 0;
    this.GYRO_P = 0;
    this.GYRO_Y = 0;
  }
}

export class RealTimeData {
  messages = $state([]);
  status = $state('disconnected');
  #socket;


  constructor(url) {
    this.#socket = new WebSocket(url);
    this.#socket.onopen(this.status = 'connected');

    this.#socket.onmessage((event) => {
      const data = event;
      let telem = TelemetryData();
      this.messages.push(event)
    });
  }
}