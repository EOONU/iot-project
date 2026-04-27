#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "AMG_CLUSTER";
const char* password = "12345678";

IPAddress local_IP(192, 168, 4, 3);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

WebServer server(80);
WiFiServer streamServer(81);

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

bool initCamera() {
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
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 20;
  config.fb_count = 1;
  config.grab_mode = CAMERA_GRAB_LATEST;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) return false;

  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    s->set_framesize(s, FRAMESIZE_QVGA);
    s->set_quality(s, 20);
    s->set_brightness(s, 0);
    s->set_contrast(s, 0);
    s->set_saturation(s, -1);
  }

  return true;
}

void handleRoot() {
  String msg = "ESP32-CAM OK\\n";
  msg += "Stream: http://";
  msg += WiFi.localIP().toString();
  msg += ":81/stream\\n";
  server.send(200, "text/plain", msg);
}

void streamTask(void* parameter) {
  while (true) {
    WiFiClient client = streamServer.available();

    if (!client) {
      vTaskDelay(5 / portTICK_PERIOD_MS);
      continue;
    }

    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
    client.println("Cache-Control: no-cache, no-store, must-revalidate");
    client.println("Pragma: no-cache");
    client.println("Expires: 0");
    client.println("Connection: close");
    client.println();

    while (client.connected()) {
      camera_fb_t* fb = esp_camera_fb_get();

      if (!fb) {
        vTaskDelay(5 / portTICK_PERIOD_MS);
        continue;
      }

      client.printf("--frame\\r\\n");
      client.printf("Content-Type: image/jpeg\\r\\n");
      client.printf("Content-Length: %u\\r\\n\\r\\n", fb->len);
      client.write(fb->buf, fb->len);
      client.write("\\r\\n", 2);

      esp_camera_fb_return(fb);

      if (!client.connected()) break;
      vTaskDelay(8 / portTICK_PERIOD_MS);
    }

    client.stop();
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  if (!WiFi.config(local_IP, gateway, subnet)) Serial.println("Static IP failed");

  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Connected!");
  Serial.print("CAM IP: ");
  Serial.println(WiFi.localIP());

  bool ok = initCamera();

  server.on("/", handleRoot);
  server.begin();

  if (ok) {
    streamServer.begin();
    xTaskCreatePinnedToCore(streamTask, "streamTask", 8192, NULL, 2, NULL, 1);
  } else {
    Serial.println("Camera init failed");
  }
}

void loop() {
  server.handleClient();
}
