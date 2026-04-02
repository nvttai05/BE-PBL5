#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "esp_http_server.h"
#include "esp_timer.h"
#include "img_converters.h"

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

#define CAMERA_MODEL_AI_THINKER

// ===== Pin mapping cho ESP32-CAM AI Thinker =====
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ================== Cấu hình ==================
const char* ssid = ".";
const char* password = "000000001";

const char* serverUrl  = "http://172.20.10.2:8000/api/v1/detect";
const char* speakerUrl = "http://172.20.10.5:80/play";

unsigned long previousMillis = 0;
const long interval = 3000;   // detect mỗi 3 giây

SemaphoreHandle_t camMutex = NULL;
httpd_handle_t stream_httpd = NULL;
httpd_handle_t index_httpd  = NULL;

static const char* INDEX_HTML = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ESP32-CAM Stream</title>
  <style>
    body{margin:0;background:#111;color:#fff;font-family:Arial;text-align:center}
    .wrap{padding:16px}
    img{width:min(96vw,900px);height:auto;border-radius:12px;border:2px solid #333}
    a{color:#7cc7ff}
    .note{color:#bbb;font-size:14px}
  </style>
</head>
<body>
  <div class="wrap">
    <h2>ESP32-CAM Live Stream</h2>
    <img src="/stream">
    <p class="note">Nếu lag, tăng interval detect lên 5 giây hoặc đổi FRAMESIZE_VGA → QVGA.</p>
  </div>
</body>
</html>
)rawliteral";

#define PART_BOUNDARY "frame"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

void sendPhotoToServer();
void sendUrlToSpeaker(String audioUrl);
void startCameraServer();

static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, INDEX_HTML, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t jpg_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;

  if (xSemaphoreTake(camMutex, pdMS_TO_TICKS(2000)) != pdTRUE) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  fb = esp_camera_fb_get();
  if (!fb) {
    xSemaphoreGive(camMutex);
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  res = httpd_resp_send(req, (const char*)fb->buf, fb->len);

  esp_camera_fb_return(fb);
  xSemaphoreGive(camMutex);
  return res;
}

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  char part_buf[64];

  httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache");

  while (true) {
    if (xSemaphoreTake(camMutex, pdMS_TO_TICKS(2000)) != pdTRUE) {
      vTaskDelay(10 / portTICK_PERIOD_MS);
      continue;
    }

    fb = esp_camera_fb_get();
    if (!fb) {
      xSemaphoreGive(camMutex);
      res = ESP_FAIL;
      break;
    }

    res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
    if (res == ESP_OK) {
      size_t hlen = snprintf(part_buf, sizeof(part_buf), STREAM_PART, fb->len);
      res = httpd_resp_send_chunk(req, part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
    }

    esp_camera_fb_return(fb);
    xSemaphoreGive(camMutex);

    if (res != ESP_OK) {
      break;
    }

    // nhả CPU một chút để loop detect và WiFi ổn định hơn
    vTaskDelay(20 / portTICK_PERIOD_MS);
  }

  return res;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 81;
  config.ctrl_port = 32769;
  config.max_uri_handlers = 8;

  httpd_uri_t index_uri = {
    .uri       = "/",
    .method    = HTTP_GET,
    .handler   = index_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t jpg_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = jpg_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&index_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(index_httpd, &index_uri);
    httpd_register_uri_handler(index_httpd, &jpg_uri);
    httpd_register_uri_handler(index_httpd, &stream_uri);
    Serial.println("Camera stream server started on port 81");
  } else {
    Serial.println("Failed to start camera server");
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  camMutex = xSemaphoreCreateMutex();
  if (camMutex == NULL) {
    Serial.println("Failed to create camera mutex");
    return;
  }

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);  // giúp stream ổn định hơn
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("ESP32-CAM connected! IP: " + WiFi.localIP().toString());

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  // ESP32 core mới dùng sccb; nếu core cũ báo lỗi thì đổi lại thành sscb
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn  = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Ưu tiên preview mượt hơn
  config.frame_size = FRAMESIZE_QVGA;   // 320x240 mượt hơn hẳn
  config.jpeg_quality = 12;
  config.fb_count = psramFound() ? 2 : 1;
  config.grab_mode = psramFound() ? CAMERA_GRAB_LATEST : CAMERA_GRAB_WHEN_EMPTY;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  startCameraServer();

  Serial.println("Camera ready!");
  Serial.println("Preview page: http://" + WiFi.localIP().toString() + ":81");
  Serial.println("Direct MJPEG:  http://" + WiFi.localIP().toString() + ":81/stream");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    sendPhotoToServer();
  }
}

void sendPhotoToServer() {
  camera_fb_t *fb = NULL;

  if (xSemaphoreTake(camMutex, pdMS_TO_TICKS(2000)) != pdTRUE) {
    Serial.println("Camera busy, skip detect cycle");
    return;
  }

  fb = esp_camera_fb_get();
  if (!fb) {
    xSemaphoreGive(camMutex);
    Serial.println("Camera capture failed");
    return;
  }

  Serial.printf("Detect capture: %d bytes\n", fb->len);

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "image/jpeg");
  http.setTimeout(5000);

  int httpCode = http.POST(fb->buf, fb->len);

  esp_camera_fb_return(fb);
  xSemaphoreGive(camMutex);

  if (httpCode == 200) {
    String payload = http.getString();
    Serial.println("Server response: " + payload);

    DynamicJsonDocument doc(2048);
    DeserializationError err = deserializeJson(doc, payload);

    if (err) {
      Serial.println("JSON parse failed");
      http.end();
      return;
    }

    if (doc["success"] && doc.containsKey("audio_url") && doc["audio_url"] != nullptr) {
      String audio_url = doc["audio_url"].as<String>();
      String full_url;

      if (audio_url.startsWith("http://") || audio_url.startsWith("https://")) {
        full_url = audio_url;
      } else {
        full_url = "http://172.20.10.2:8000" + audio_url;
      }

      Serial.println("Sending audio URL to speaker: " + full_url);
      sendUrlToSpeaker(full_url);
    }
  } else {
    Serial.println("HTTP Error from server: " + String(httpCode));
  }

  http.end();
}

void sendUrlToSpeaker(String audioUrl) {
  HTTPClient http;
  http.begin(speakerUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(3000);

  DynamicJsonDocument doc(256);
  doc["audio_url"] = audioUrl;

  String jsonString;
  serializeJson(doc, jsonString);

  int httpCode = http.POST(jsonString);

  if (httpCode > 0) {
    Serial.println("Sent to speaker successfully");
  } else {
    Serial.println("Failed to send to speaker");
  }

  http.end();
}