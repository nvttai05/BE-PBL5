#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

#include "AudioFileSourceHTTPStream.h"
#include "AudioFileSourceBuffer.h"
#include "AudioGeneratorWAV.h"
#include "AudioOutputI2S.h"

#define I2S_DOUT  22
#define I2S_BCLK  26
#define I2S_LRC   25

const char* ssid = ".";
const char* password = "000000001";

WebServer server(80);

AudioGeneratorWAV* wav = nullptr;
AudioFileSourceHTTPStream* file = nullptr;
AudioFileSourceBuffer* buff = nullptr;
AudioOutputI2S* out = nullptr;

bool isPlaying = false;
unsigned long lastHeapPrint = 0;

void stopPlayback() {
  if (wav) {
    wav->stop();
    delete wav;
    wav = nullptr;
  }

  if (buff) {
    delete buff;
    buff = nullptr;
  }

  if (file) {
    delete file;
    file = nullptr;
  }

  isPlaying = false;
  Serial.println("Playback stopped");
}

bool startPlayback(const String& url) {
  stopPlayback();

  file = new AudioFileSourceHTTPStream(url.c_str());
  if (!file) {
    Serial.println("Cannot create HTTP stream");
    return false;
  }

  // Buffer nhỏ, đủ nhẹ cho DevKit V1
  buff = new AudioFileSourceBuffer(file, 2048);
  if (!buff) {
    Serial.println("Cannot create stream buffer");
    delete file;
    file = nullptr;
    return false;
  }

  wav = new AudioGeneratorWAV();
  if (!wav) {
    Serial.println("Cannot create WAV generator");
    delete buff; buff = nullptr;
    delete file; file = nullptr;
    return false;
  }

  if (!wav->begin(buff, out)) {
    Serial.println("wav->begin() failed");
    stopPlayback();
    return false;
  }

  isPlaying = true;
  Serial.println("Playback started");
  return true;
}

void handlePlay() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "Bad Request: no body");
    return;
  }

  String body = server.arg("plain");
  Serial.println("Body: " + body);

  DynamicJsonDocument doc(512);
  DeserializationError err = deserializeJson(doc, body);
  if (err) {
    server.send(400, "text/plain", "Invalid JSON");
    return;
  }

  if (!doc.containsKey("audio_url")) {
    server.send(400, "text/plain", "Missing audio_url");
    return;
  }

  String audio_url = doc["audio_url"].as<String>();
  Serial.println("Received audio URL: " + audio_url);

  bool ok = startPlayback(audio_url);

  if (ok) {
    server.send(200, "text/plain", "Playing");
  } else {
    server.send(500, "text/plain", "Playback failed");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected! IP: " + WiFi.localIP().toString());

  out = new AudioOutputI2S();
  out->SetPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  out->SetGain(0.8); 

  server.on("/play", HTTP_POST, handlePlay);
  server.begin();

  Serial.println("Speaker server ready on port 80");
}

void loop() {
  server.handleClient();

  if (wav && isPlaying) {
    if (!wav->loop()) {
      Serial.println("Playback finished");
      stopPlayback();
    }
  }

  if (millis() - lastHeapPrint >= 10000) {
    lastHeapPrint = millis();
    Serial.printf("Free heap: %u bytes\n", ESP.getFreeHeap());
  }

  delay(1);
}