#include <Wire.h>
#include "rgb_lcd.h"
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>
#include "DHT.h"
#include "BlueDot_BMA400.h"

rgb_lcd lcd;

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
#define TRIG3 12
#define ECHO3 13

long readUltrasonic(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(3);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 25000);
  if (duration == 0) return -1;  // timeout
  return duration * 0.034 / 2;
}

BlueDot_BMA400 bma400 = BlueDot_BMA400();

//Timers
uint32_t screenTimer = 0;
uint32_t sensorTimer = 0;
uint8_t screenPage = 0;

//Sensor Storage
float tempC = 0;
float hum = 0;
long u1 = 0, u2 = 0, u3 = 0;
float ax, ay, az, gForce;

void setup() {
  Serial.begin(115200);

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

  // Ultrasonic
  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT);
  pinMode(ECHO2, INPUT);
  pinMode(TRIG3, OUTPUT);
  pinMode(ECHO3, INPUT);

  // BMA400
  bma400.parameter.I2CAddress = 0x15;
  bma400.parameter.measurementRange = 0; 
  bma400.parameter.outputDataRate = 7;    
  bma400.parameter.powerMode = 2;

  bma400.init();
}

void loop() {

  //GPS DATA
  char c = GPS.read();
  if (GPS.newNMEAreceived()) GPS.parse(GPS.lastNMEA());

  //SENSOR UPDATE EVERY 200ms
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
    gForce = sqrt(ax * ax + ay * ay + az * az);
  }

  //SCREEN CYCLE EVERY 2 SECONDS 
  if (millis() - screenTimer > 2000) {
    screenTimer = millis();
    screenPage = (screenPage + 1) % 3; 
    lcd.clear();
  }

  //PAGE 0 (TEMP/HUM/G-FORCE)
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

  // PAGE 1 (ULTRASONIC)
  if (screenPage == 1) {
    lcd.setCursor(0, 1);
    lcd.print("U1:");
    if (u1 < 0) lcd.print("Err "); else lcd.print(u1);
    lcd.print("  U2:");
    if (u2 < 0) lcd.print("Err"); else lcd.print(u2);

    lcd.setCursor(0, 0);
    lcd.print("U3:");
    if (u3 < 0) lcd.print("Err"); else { lcd.print(u3);
      lcd.print(" cm");
    }
  }

  //PAGE 2 (GPS)
  if (screenPage == 2) {
    lcd.setCursor(0, 0);
    if (GPS.fix) {
      lcd.print("Lat:");
      lcd.print(GPS.latitudeDegrees, 6);
      lcd.print(GPS.lat);
    } else {
      lcd.print("No GPS Fix");
    }

    lcd.setCursor(0, 1);
    if (GPS.fix) {
      lcd.print("Lon:");
      lcd.print(GPS. longitudeDegrees, 6);
      lcd.print(GPS.lon);
    }
  }
}