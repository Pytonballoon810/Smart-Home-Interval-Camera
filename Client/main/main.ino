#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include "esp_camera.h"
#include "SPIFFS.h"

AsyncWebServer server(80);

// Camera configuration
#define CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

camera_config_t config;

void setup() {
  Serial.begin(115200);

  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS initialization failed");
    return;
  }

  // Initialize camera
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
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Init with high specs to pre-allocate larger buffers
  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;  // Quality: 0-63 lower means higher quality
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;  // Quality: 0-63 lower means higher quality
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Connect to WiFi
  WiFi.begin("your-ssid", "your-password");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  // Set up routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/latest-image", HTTP_GET, handleLatestImage);
  server.on("/live-mode", HTTP_GET, handleLiveMode);
  server.begin();
}

void loop() {
  // Capture and save image
  captureImage();

  delay(60000); // Capture image every 1 minute
}

void captureImage() {
  Serial.println("Capturing image...");
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  // Save image to SPIFFS
  char filename[32];
  sprintf(filename, "/image%d.jpg", millis());
  File file = SPIFFS.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("Failed to open file for writing");
    return;
  }
  file.write(fb->buf, fb->len);
  file.close();
  esp_camera_fb_return(fb);
  Serial.println("Image captured and saved");
}

void handleRoot(AsyncWebServerRequest *request) {
  request->send(SPIFFS, "/index.html", "text/html");
}

void handleLatestImage(AsyncWebServerRequest *request) {
  // Serve latest image
  Serial.println("Serving latest image");
  File file = findLatestImage();
  if (!file) {
    request->send(404);
    return;
  }
  request->send(SPIFFS, file.name(), "image/jpeg");
}

void handleLiveMode(AsyncWebServerRequest *request) {
  // Enable live mode
  // Implement logic to switch to live mode
}

File findLatestImage() {
  File root = SPIFFS.open("/");
  File latestFile;
  time_t latestTime = 0;

  while (File file = root.openNextFile()) {
    if (!file.isDirectory() && file.name()[1] == 'i' && file.name()[2] == 'm' && file.name()[3] == 'a' && file.name()[4] == 'g' && file.name()[5] == 'e') {
      time_t fileTime = atol(file.name() + 6);
      if (fileTime > latestTime) {
        latestTime = fileTime;
        latestFile = file;
      }
    }
  }
  return latestFile;
}
