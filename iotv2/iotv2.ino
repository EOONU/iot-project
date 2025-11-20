#include <Wire.h>
#include "rgb_lcd.h"
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include "DHT.h"
#include "BlueDot_BMA400.h"

// ---------------- LCD ----------------
rgb_lcd lcd;

// ---------------- GPS ----------------
HardwareSerial mySerial(1);
#define RXPin 16
#define TXPin 17
Adafruit_GPS GPS(&mySerial);
uint32_t timer = millis();

// ---------------- DHT11 ----------------
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ---------------- Ultrasonic ----------------
#define TRIG1 25
#define ECHO1 26
#define TRIG2 27
#define ECHO2 14
#define TRIG3 12
#define ECHO3 13

long readUltrasonic(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 25000);
  long distance = duration * 0.034 / 2;

  return distance;
}

// ---------------- BMA400 ----------------
BlueDot_BMA400 bma400 = BlueDot_BMA400();

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 FULL SYSTEM STARTING...");

  // I2C
  Wire.begin(21, 22);

  // LCD
  lcd.begin(16, 2);
  lcd.print("Booting...");
  delay(2000);

  // GPS
  mySerial.begin(9600, SERIAL_8N1, RXPin, TXPin);
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_NOANTENNA);

  // DHT sensor
  dht.begin();

  // Ultrasonic pins
  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);
  pinMode(TRIG3, OUTPUT);
  pinMode(ECHO3, INPUT);

  // BMA400 accelerometer
  bma400.parameter.I2CAddress = 0x15;
  bma400.parameter.powerMode = 0x02;
  bma400.parameter.measurementRange = 0x00; // 2g
  bma400.parameter.outputDataRate = 0x07;   // 50Hz
  bma400.parameter.oversamplingRate = 0x03;

  if (bma400.init() == 0x90)
    Serial.println("BMA400 OK");
  else
    Serial.println("BMA400 INIT FAILED");

  lcd.clear();
}

void loop() {

  // ---- GPS Poll ----
  char c = GPS.read();
  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA())) return;
  }

  // ---- Sensors ----
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  long d1 = readUltrasonic(TRIG1, ECHO1);
  long d2 = readUltrasonic(TRIG2, ECHO2);
  long d3 = readUltrasonic(TRIG3, ECHO3);

  // BMA400 accelerometer
  bma400.readData();
  float ax = bma400.parameter.acc_x / 1000.0;
  float ay = bma400.parameter.acc_y / 1000.0;
  float az = bma400.parameter.acc_z / 1000.0;

  float gForce = sqrt(ax * ax + ay * ay + az * az);

  // ---- LCD Update Every 1s ----
  if (millis() - timer > 1000) {
    timer = millis();
    lcd.clear();

    // First row: Temp, Humidity, G-force
    lcd.setCursor(0, 0);
    lcd.print(temp, 0); lcd.print("C ");
    lcd.print(hum, 0); lcd.print("%");

    // Show G-force on end of line
    lcd.setCursor(11, 0);
    lcd.print(gForce, 1);

    // Second row: GPS or fallback
    lcd.setCursor(0, 1);
    if (GPS.fix) {
      lcd.print(GPS.latitude, 2);
      lcd.print(GPS.lat);
    } else {
      lcd.print("No GPS Fix");
    }

    // ---- Serial Debug ----
    Serial.println("------ SENSOR DATA ------");
    Serial.print("Temp: "); Serial.print(temp); Serial.println(" C");
    Serial.print("Hum : "); Serial.print(hum); Serial.println(" %");

    Serial.print("Ultrasonic: ");
    Serial.print(d1); Serial.print(" cm  ");
    Serial.print(d2); Serial.print(" cm  ");
    Serial.print(d3); Serial.println(" cm");

    Serial.print("Accel X: "); Serial.print(ax); Serial.println(" g");
    Serial.print("Accel Y: "); Serial.print(ay); Serial.println(" g");
    Serial.print("Accel Z: "); Serial.print(az); Serial.println(" g");
    Serial.print("Total G: "); Serial.println(gForce);

    if (GPS.fix) {
      Serial.print("GPS lat: ");
      Serial.print(GPS.latitude, 6); Serial.println(GPS.lat);
      Serial.print("GPS lon: ");
      Serial.print(GPS.longitude, 6); Serial.println(GPS.lon);
      Serial.print("Satellites: ");
      Serial.println(GPS.satellites);
    } else {
      Serial.println("Waiting for GPS fix...");
    }
  }
}
