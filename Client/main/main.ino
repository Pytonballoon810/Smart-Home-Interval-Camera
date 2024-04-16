#include <WiFi.h>
#include "esp_camera.h"
#include <HTTPClient.h>
#include <SPI.h>
#include <SD.h>
#include "secrets.h"

// WiFi credentials
const char* ssid = wifi_ssid;
const char* password = wifi_password;

// Server details
const char* serverUrl = "http://your-server-url/upload"; // Change this to your server URL
const char* uploadFileName = "image.jpg"; // Change this to the name you want to use for the uploaded image file

// Cron time format: minute hour day month day_of_week
const char* cronTime = "0 15 * * *"; // Take picture every day at 15:00

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

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("WiFi connected");

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

  // Initialize SD card
  if (!SD.begin()) {
    Serial.println("Failed to initialize SD card");
    return;
  }
}

void loop() {
  // Get current time
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    delay(1000);
    return;
  }

  // Parse cron time format
  int cronMinute, cronHour;
  sscanf(cronTime, "%d %d", &cronMinute, &cronHour);

  // Check if it's time to take picture
  if (timeinfo.tm_min == cronMinute && timeinfo.tm_hour == cronHour) {
    // Capture image
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      delay(1000);
      return;
    }

    // Save image to SD card
    saveImageToSD(fb);

    // Send image to server
    sendImageToServer(fb);

    // Free camera framebuffer
    esp_camera_fb_return(fb);
  }

  delay(1000); // Check time every second
}

void saveImageToSD(camera_fb_t *fb) {
  // Open file on SD card
  File file = SD.open(uploadFileName, FILE_WRITE);
  if (!file) {
    Serial.println("Failed to open file on SD card");
    return;
  }

  // Write image data to file
  file.write(fb->buf, fb->len);

  // Close file
  file.close();

  Serial.println("Image saved to SD card");
}

void sendImageToServer(camera_fb_t *fb) {
  // Create HTTPClient object
  HTTPClient http;

  // Start HTTPClient with server URL
  http.begin(serverUrl);

  // Set header content type
  http.addHeader("Content-Type", "image/jpeg");

  // Send image data as binary body
  http.POST((uint8_t*)fb->buf, fb->len);

  // End HTTPClient
  http.end();

  Serial.println("Image sent to server");
}
