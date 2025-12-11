#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include "rgb_lcd.h"
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include "DHT.h"
#include "BlueDot_BMA400.h"
#include "homepage.h"

rgb_lcd lcd;

HardwareSerial mySerial(1);
#define RXPin 16
#define TXPin 17
Adafruit_GPS GPS(&mySerial);

// -------- WiFi ----------
const char* ssid = "EO";
const char* password = "12345678";

WebServer server(80);

// --------- DHT ----------
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --------- Ultrasonic ----
#define TRIG1 33
#define ECHO1 25
#define TRIG2 27
#define ECHO2 14
#define TRIG3 12
#define ECHO3 13

// --------- BMA400 --------
BlueDot_BMA400 bma400;

//Timers
uint32_t screenTimer = 0;
uint32_t sensorTimer = 0;
uint8_t screenPage = 0;

//Sensor Storage
float tempC = 0;
float hum = 0;
long u1 = 0, u2 = 0, u3 = 0;
float ax, ay, az, gForce;

// -------- FUNCTIONS ---------

long readUltrasonic(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(3);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 25000);
  if (duration == 0) return -1;
  return duration * 0.034 / 2;
}

void handleRoot() {
  String page = FPSTR(HTML_PAGE);

  page.replace("%TEMP%", String(tempC));
  page.replace("%HUM%", String(hum));
  page.replace("%U1%", String(u1));
  page.replace("%U2%", String(u2));
  page.replace("%U3%", String(u3));
  page.replace("%AX%", String(ax, 3));
  page.replace("%AY%", String(ay, 3));
  page.replace("%AZ%", String(az, 3));
  page.replace("%GF%", String(gForce, 3));

  if (GPS.fix) {
    String gpsBlock =
      "Lat: " + String(GPS.latitudeDegrees, 6) +
      "<br>Lon: " + String(GPS.longitudeDegrees, 6);
    page.replace("%GPSDATA%", gpsBlock);
  } else {
    page.replace("%GPSDATA%", "No GPS Fix");
  }

  server.send(200, "text/html", page);
}


// -------- SETUP ---------
void setup() {
  Serial.begin(115200);

  // WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.begin();

  // LCD
  Wire.begin(21, 22);
  lcd.begin(16, 2);
  lcd.print("System Boot...");
  delay(1500);
  lcd.clear();

  // GPS
  mySerial.begin(9600, SERIAL_8N1, RXPin, TXPin);
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_NOANTENNA);

  // DHT
  dht.begin();

  // Ultrasonic pins
  pinMode(TRIG1, OUTPUT); pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT); pinMode(ECHO2, INPUT);
  pinMode(TRIG3, OUTPUT); pinMode(ECHO3, INPUT);

  // BMA400
  bma400.parameter.I2CAddress = 0x15;
  bma400.parameter.measurementRange = 0;
  bma400.parameter.outputDataRate = 7;
  bma400.parameter.powerMode = 2;
  bma400.init();
}


// -------- LOOP ---------
void loop() {

  server.handleClient();

  // GPS
  char c = GPS.read();
  if (GPS.newNMEAreceived()) GPS.parse(GPS.lastNMEA());

  // ---- SENSOR UPDATE ----
  if (millis() - sensorTimer > 200) {
    sensorTimer = millis();

    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t)) tempC = t;
    if (!isnan(h)) hum = h;

    u1 = readUltrasonic(TRIG1, ECHO1);
    u2 = readUltrasonic(TRIG2, ECHO2);
    u3 = readUltrasonic(TRIG3, ECHO3);

    bma400.readData();
    ax = bma400.parameter.acc_x / 1000.0;
    ay = bma400.parameter.acc_y / 1000.0;
    az = bma400.parameter.acc_z / 1000.0;
    gForce = sqrt(ax*ax + ay*ay + az*az);
  }

  // ---- SCREEN UPDATE ----
  if (millis() - screenTimer > 2000) {
    screenTimer = millis();
    screenPage = (screenPage + 1) % 3;
    lcd.clear();
  }

  // PAGE 0 — Temp/Humidity/G-Force
  if (screenPage == 0) {
    lcd.setCursor(0, 0);
    lcd.print("Temp:");
    lcd.print((int)tempC);
    lcd.print("C Hum:");
    lcd.print((int)hum);
    lcd.print("%");

    lcd.setCursor(0, 1);
    lcd.print("G:");
    lcd.print(gForce, 2);
  }

  // PAGE 1 — Ultrasonic
  if (screenPage == 1) {
    lcd.setCursor(0, 0);
    lcd.print("U1:");
    if (u1 < 0) lcd.print("Err "); else lcd.print(u1);
    lcd.print(" U2:");
    if (u2 < 0) lcd.print("Err"); else lcd.print(u2);

    lcd.setCursor(0, 1);
    lcd.print("U3:");
    if (u3 < 0) lcd.print("Err"); else {
      lcd.print(u3);
      lcd.print("cm");
    }
  }

  // PAGE 2 — GPS
  if (screenPage == 2) {
    lcd.setCursor(0, 0);
    if (GPS.fix) {
      lcd.print("Lat:");
      lcd.print(GPS.latitudeDegrees, 4);
    } else {
      lcd.print("No GPS Fix");
    }

    lcd.setCursor(0, 1);
    if (GPS.fix) {
      lcd.print("Lon:");
      lcd.print(GPS.longitudeDegrees, 4);
    }
  }
}
