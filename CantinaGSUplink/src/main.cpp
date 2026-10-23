#include <Arduino.h>
// Libraries
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <string>
#include <vector>
#define PIN 32
TaskHandle_t MusicTaskHandle = NULL;
struct Note {
  int frequency;
  int durationMs;
  int postDelayMs; // Rest period after the note plays
};

const Note song[] = {
    {440, 110, 110}, {587, 110, 110}, {440, 110, 110}, {587, 110, 110},
    {440, 120, 10},  {587, 100, 120}, {440, 210, 10},  {415, 100, 0},
    {440, 110, 110}, {440, 110, 20},  {415, 100, 0},   {440, 110, 10},
    {392, 100, 120}, {370, 100, 0},   {392, 110, 20},  {370, 90, 0},
    {349, 340, 10},  {294, 320, 220}, {440, 110, 110}, {587, 110, 120},
    {440, 110, 110}, {587, 110, 110}, {440, 110, 20},  {587, 90, 130},
    {440, 210, 10},  {415, 100, 0},   {440, 110, 110}, {392, 110, 110},
    {392, 330, 20},  {370, 100, 0},   {392, 110, 110}, {523, 110, 10},
    {466, 100, 130}, {440, 90, 130},  {392, 320, 0},   {440, 110, 110},
    {587, 110, 110}, {440, 110, 110}, {587, 110, 120}, {440, 110, 10},
    {587, 100, 120}, {440, 210, 20},  {415, 90, 0},    {440, 110, 110},
    {523, 120, 110}, {523, 330, 10},  {440, 100, 0},   {392, 110, 110},
    {349, 340, 10},  {294, 320, 220}, {294, 280, 0},   {277, 60, 10},
    {294, 40, 0},    {330, 50, 10}};
const int totalNotes = sizeof(song) / sizeof(Note);
void MusicTaskCode(void *pvParameters) {
  (void)pvParameters;

  for (;;) {
    for (int i = 0; i < totalNotes; i++) {
      // Play the tone
      tone(PIN, song[i].frequency);
      vTaskDelay(pdMS_TO_TICKS(song[i].durationMs));

      // Stop the tone
      noTone(PIN);

      // Execute post-note rest interval if one is specified
      if (song[i].postDelayMs > 0) {
        vTaskDelay(pdMS_TO_TICKS(song[i].postDelayMs));
      }
    }

    // Pause 3 seconds before repeating the song loop
    vTaskDelay(pdMS_TO_TICKS(3000));
  }
}
// Command string to se nd to the flight computer (Initiator)
String cmd;

// The MAC ADDRESS of Initiator (Flight Computer)
uint8_t MAC[] = {0x68, 0x09, 0x47, 0x9C, 0xA7, 0xC0};

void onDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
  // Local buffer with room for a null terminator to prevent crashes
  char tempBuffer[251];
  int copyLen = (len > 250) ? 250 : len;
  memcpy(tempBuffer, incomingData, copyLen);
  tempBuffer[copyLen] = '\0'; // Force null-termination

  // Use Serial.print instead of println because the CSV string already ends
  // with '\n'
  static const std::string confirm = "AT\n";
  esp_now_send(MAC, (uint8_t *)confirm.c_str(), confirm.length() + 1);

  Serial.print(tempBuffer);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);

  // Activate Long Range mode
  esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);

  const int chan = 4;
  ESP_ERROR_CHECK(esp_wifi_set_channel(chan, WIFI_SECOND_CHAN_NONE));

  if (esp_now_init() != ESP_OK) {
    ESP.restart();
    return;
  }

  esp_now_peer_info_t peerInfo = {};
  peerInfo.channel = chan;
  peerInfo.ifidx = WIFI_IF_STA;
  peerInfo.encrypt = false;
  memcpy(peerInfo.peer_addr, MAC, 6);

  if (esp_now_add_peer(&peerInfo) == ESP_OK) {
    Serial.printf("# Peer Added\r\n");
  } else {
    Serial.printf("# Unable to add peer\r\n");
  }

  delay(300);
  Serial.println("# Start CB");
  delay(2000);

  // Listen for incoming telemetry packets in the background
  esp_now_register_recv_cb(onDataRecv);
  ledcSetup(6, 2000, 8);
  ledcAttachPin(PIN, 6);

  xTaskCreatePinnedToCore(MusicTaskCode, "MusicTask", 4000, NULL, 1,
                          &MusicTaskHandle, 1);
}

void loop() {
  // Read command from Serial Monitor / Python backend and send to Flight
  // Computer
  if (Serial.available()) {
    cmd = Serial.readStringUntil('\n');

    cmd.trim();

    if (cmd.length() > 0) {
      esp_now_send(MAC, (uint8_t *)cmd.c_str(), cmd.length() + 1);
    }
  }
}