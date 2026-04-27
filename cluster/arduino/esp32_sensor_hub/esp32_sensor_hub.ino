#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include "BlueDot_BMA400.h"
#include "DHT.h"
#include <math.h>

const char* ssid = "AMG_CLUSTER";
const char* password = "12345678";

IPAddress local_IP(192, 168, 4, 2);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

WebServer server(80);

HardwareSerial mySerial(1);
#define RXPin 16
#define TXPin 17
Adafruit_GPS GPS(&mySerial);

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define TRIG1 33
#define ECHO1 25
#define TRIG2 27
#define ECHO2 14

BlueDot_BMA400 bma400;

long rearLeftCm = -1;
long rearRightCm = -1;

float tempC = 0.0;
float humidity = 0.0;

float ax = 0.0;
float ay = 0.0;
float az = 0.0;
float pitchDeg = 0.0;
float rollDeg = 0.0;

bool gpsFix = false;
float gpsLat = 0.0;
float gpsLon = 0.0;
float gpsSpeedKmh = 0.0;
float gpsHeadingDeg = 0.0;

bool ultrasonicLeftLive = false;
bool ultrasonicRightLive = false;
bool bma400Live = false;
bool dhtLive = false;
bool gpsLive = false;

unsigned long lastUltraUpdate = 0;
unsigned long lastBmaUpdate = 0;
unsigned long lastDhtUpdate = 0;

long readUltrasonicRaw(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  unsigned long duration = pulseIn(echoPin, HIGH, 18000UL);
  if (duration == 0) return -1;

  long cm = duration * 0.0343 / 2.0;
  if (cm < 3 || cm > 300) return -1;
  return cm;
}

long filteredRead(int trigPin, int echoPin, long lastValue) {
  long a = readUltrasonicRaw(trigPin, echoPin);
  delay(6);
  long b = readUltrasonicRaw(trigPin, echoPin);
  delay(6);
  long c = readUltrasonicRaw(trigPin, echoPin);

  long vals[3] = {a, b, c};

  for (int i = 0; i < 3; i++) {
    for (int j = i + 1; j < 3; j++) {
      if (vals[j] < vals[i]) {
        long t = vals[i];
        vals[i] = vals[j];
        vals[j] = t;
      }
    }
  }

  long median = vals[1];

  if (median < 0) return -1;
  if (lastValue < 0) return median;
  if (abs(median - lastValue) > 80) return lastValue;

  return (lastValue * 7 + median * 3) / 10;
}

float safeDistance(long value) {
  if (value < 0) return 400.0;
  return (float)value;
}

void updateGPS() {
  while (mySerial.available()) GPS.read();

  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA())) return;
  }

  gpsFix = GPS.fix;
  gpsLive = GPS.fix;

  if (gpsFix) {
    gpsLat = GPS.latitudeDegrees;
    gpsLon = GPS.longitudeDegrees;
    gpsSpeedKmh = GPS.speed * 1.852;
    gpsHeadingDeg = GPS.angle;
  }
}

void updateBMA400() {
  bma400.readData();

  ax = bma400.parameter.acc_x / 1000.0;
  ay = bma400.parameter.acc_y / 1000.0;
  az = bma400.parameter.acc_z / 1000.0;

  bma400Live = !(ax == 0.0 && ay == 0.0 && az == 0.0);

  pitchDeg = atan2(ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
  rollDeg  = atan2(ay, az) * 180.0 / PI;
}

void updateDHT() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  dhtLive = !isnan(t) && !isnan(h);

  if (!isnan(t)) tempC = t;
  if (!isnan(h)) humidity = h;
}

void updateUltrasonics() {
  long left = filteredRead(TRIG1, ECHO1, rearLeftCm);
  delay(12);
  long right = filteredRead(TRIG2, ECHO2, rearRightCm);

  ultrasonicLeftLive = left > 0 && left < 400;
  ultrasonicRightLive = right > 0 && right < 400;

  if (ultrasonicLeftLive) rearLeftCm = left;
  if (ultrasonicRightLive) rearRightCm = right;
}

void handleRoot() {
  server.send(200, "text/plain", "ESP32 sensor hub OK");
}

void handleData() {
  String json = "{";

  json += "\"rear_left_cm\":" + String(safeDistance(rearLeftCm), 1) + ",";
  json += "\"rear_right_cm\":" + String(safeDistance(rearRightCm), 1) + ",";
  json += "\"temp_c\":" + String(tempC, 1) + ",";
  json += "\"humidity\":" + String(humidity, 1) + ",";
  json += "\"gforce_x\":" + String(ax, 3) + ",";
  json += "\"gforce_y\":" + String(ay, 3) + ",";
  json += "\"gforce_z\":" + String(az, 3) + ",";
  json += "\"pitch_deg\":" + String(pitchDeg, 2) + ",";
  json += "\"roll_deg\":" + String(rollDeg, 2) + ",";
  json += "\"gps_fix\":" + String(gpsFix ? "true" : "false") + ",";
  json += "\"latitude\":" + String(gpsLat, 6) + ",";
  json += "\"longitude\":" + String(gpsLon, 6) + ",";
  json += "\"speed_kmh\":" + String(gpsSpeedKmh, 1) + ",";
  json += "\"heading_deg\":" + String(gpsHeadingDeg, 1) + ",";
  json += "\"ultrasonic_left_live\":" + String(ultrasonicLeftLive ? "true" : "false") + ",";
  json += "\"ultrasonic_right_live\":" + String(ultrasonicRightLive ? "true" : "false") + ",";
  json += "\"bma400_live\":" + String(bma400Live ? "true" : "false") + ",";
  json += "\"dht11_live\":" + String(dhtLive ? "true" : "false") + ",";
  json += "\"gps_live\":" + String(gpsLive ? "true" : "false") + ",";
  json += "\"uptime_ms\":" + String(millis());

  json += "}";

  server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
  server.sendHeader("Pragma", "no-cache");
  server.sendHeader("Expires", "0");
  server.send(200, "application/json", json);
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
  Serial.print("Sensor Hub IP: ");
  Serial.println(WiFi.localIP());

  Wire.begin(21, 22);

  mySerial.begin(9600, SERIAL_8N1, RXPin, TXPin);
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_NOANTENNA);

  dht.begin();

  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);

  bma400.parameter.I2CAddress = 0x15;
  bma400.parameter.measurementRange = 0;
  bma400.parameter.outputDataRate = 7;
  bma400.parameter.powerMode = 2;
  bma400.init();

  updateUltrasonics();
  updateBMA400();
  updateDHT();
  updateGPS();

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();
}

void loop() {
  server.handleClient();
  updateGPS();

  unsigned long now = millis();

  if (now - lastUltraUpdate >= 100) {
    updateUltrasonics();
    lastUltraUpdate = now;
  }

  if (now - lastBmaUpdate >= 20) {
    updateBMA400();
    lastBmaUpdate = now;
  }

  if (now - lastDhtUpdate >= 2000) {
    updateDHT();
    lastDhtUpdate = now;
  }
}
