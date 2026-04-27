# AMG Cluster v14 Smooth Full

## What is fixed
- Pi UI rebuilt for smoother running
- No automatic switching to Reverse Assist
- Simulation mode OFF on boot
- Simulation only turns ON when the button is pressed
- DHT11 now comes from ESP32 sensor hub
- Per-sensor live status updates
- Faster ESP32 polling on Pi
- Threaded low-latency camera page
- Offline map downloader included
- Enhanced map fallback for missing tiles

## Network
Pi hotspot:
- Pi: 192.168.4.1
- ESP32 sensor hub: 192.168.4.2
- ESP32-CAM: 192.168.4.3

## Pi run
```bash
cd ~/Desktop/amg_cluster_v14_smooth_full
chmod +x run_auto.sh run_download_maps.sh
find . -type d -name __pycache__ -exec rm -rf {} +
./run_auto.sh
```

## Download maps using Ethernet
```bash
cd ~/Desktop/amg_cluster_v14_smooth_full
./run_download_maps.sh
```

## Arduino sketches
Sensor hub:
```text
arduino/esp32_sensor_hub/esp32_sensor_hub.ino
```

Fast ESP32-CAM:
```text
arduino/esp32_cam_fast/esp32_cam_fast.ino
```

Also included at project root:
```text
ESP32_SENSOR_HUB_UPDATED.ino
ESP32_CAM_FAST_UPDATED.ino
```
