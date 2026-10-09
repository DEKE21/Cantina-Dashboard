// Libraries
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

// the command I want to send to the initiator
String cmd;

// The MAC ADDRESS of Initiator
uint8_t MAC[] = {
0x68,
0x09,
0x47,
0x9C,
0xA7,
0xC0
};

// Function from ESP-NOW to receive any data that came in
void onDataRecv(
  const esp_now_recv_info_t *info,
  const uint8_t *incomingData,
  int len) 
  {
    Serial.println((char *)incomingData);
}

void setup() {
  // Serial monitor communication bus begin
  Serial.begin(115200);
  delay(1000);
  // Wifi stuff
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);
  // Long range made activated
  esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);

  esp_now_peer_info_t peerInfo = {};

// the int chan will be your team number.
// Also with my error earlier, found something on basically a Redit site below of how to fix the peer stuff.
  int chan=2;
  ESP_ERROR_CHECK(esp_wifi_set_channel(chan,WIFI_SECOND_CHAN_NONE));
  if (esp_now_init() != ESP_OK) { ESP.restart(); return; }
    peerInfo.channel = chan;
    memcpy(peerInfo.peer_addr, MAC, 6);
  if (esp_now_add_peer(&peerInfo) == ESP_OK){Serial.printf("# Peer Added\r\n");}
  else {Serial.printf("# Unable to add peer \r\n");}

  delay(300);  
  Serial.println("Start CB");
  delay(2000);
  // This will be the function playing in the background listening for any commands coming in.
  esp_now_register_recv_cb(onDataRecv);
}

void loop() {

// With this if-statment, I am able to type into the Serial Monitor then to have this function read what I sent
// After it will make equal to what I typed the command that is being sent to the initiator
if (Serial.available()){
  cmd = Serial.readStringUntil('\n');
  cmd.trim();

    esp_now_send(
      MAC,
      (uint8_t *)cmd.c_str(),
      cmd.length() + 1
    );
  }
}