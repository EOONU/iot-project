#ifndef HOMEPAGE_H
#define HOMEPAGE_H

const char HTML_PAGE[] PROGMEM = R"=====( 
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="1">
<style>
body { font-family: Arial; background:#111; color:#0f0; padding:20px; }
.box { background:#000; padding:15px; margin-bottom:15px; border-radius:10px; }
h2 { margin:0 0 10px 0; }
</style>
</head>
<body>

<h1>ESP32 LIVE SENSOR DATA</h1>

<div class="box">
<h2>Temperature & Humidity</h2>
Temp: %TEMP%C<br>
Humidity: %HUM% %
</div>

<div class="box">
<h2>Ultrasonic Sensors</h2>
U1: %U1% cm<br>
U2: %U2% cm<br>
U3: %U3% cm
</div>

<div class="box">
<h2>Accelerometer (BMA400)</h2>
ax: %AX% g<br>
ay: %AY% g<br>
az: %AZ% g<br>
G-Force: %GF% g
</div>

<div class="box">
<h2>GPS</h2>
%GPSDATA%
</div>

</body>
</html>
)=====";

#endif
