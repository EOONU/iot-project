import math
import os
import time
import socket
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

TILE_ROOT = "data/offline_tiles"
CENTER_LAT = 53.35653
CENTER_LON = -6.12403
ZOOMS = [10, 11, 12, 13, 14, 15]
RADIUS_BY_ZOOM = {10: 2, 11: 3, 12: 5, 13: 8, 14: 12, 15: 18}
USER_AGENT = "RaspberryPiCarCluster/1.0 offline tile cache"

def internet_available(timeout=3):
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout)
        return True
    except OSError:
        return False

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2 ** zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

def download_tile(z, x, y):
    folder = os.path.join(TILE_ROOT, str(z), str(x))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{y}.png")

    if os.path.exists(path) and os.path.getsize(path) > 100:
        return "cached"

    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/png,image/*,*/*"})

    try:
        with urlopen(req, timeout=10) as response:
            if response.status != 200:
                return f"failed {response.status}"
            data = response.read()

        if len(data) < 100:
            return "failed empty"

        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
        return "downloaded"
    except HTTPError as e:
        return f"http {e.code}"
    except URLError as e:
        return f"url error {e.reason}"
    except Exception as e:
        return f"error {e}"

def main():
    print("Offline map tile downloader")
    print("Tile root:", TILE_ROOT)
    print("Centre:", CENTER_LAT, CENTER_LON)

    if not internet_available():
        print("No internet detected. Plug Ethernet into the Pi, then run again.")
        return

    total = downloaded = cached = failed = 0

    for z in ZOOMS:
        cx, cy = deg2num(CENTER_LAT, CENTER_LON, z)
        radius = RADIUS_BY_ZOOM.get(z, 5)
        print(f"Zoom {z}: centre tile {cx}/{cy}, radius {radius}")

        for x in range(cx - radius, cx + radius + 1):
            for y in range(cy - radius, cy + radius + 1):
                total += 1
                result = download_tile(z, x, y)
                if result == "downloaded":
                    downloaded += 1
                    print(f"DOWNLOADED z{z}/{x}/{y}")
                    time.sleep(0.12)
                elif result == "cached":
                    cached += 1
                else:
                    failed += 1
                    print(f"FAILED z{z}/{x}/{y}: {result}")
                    time.sleep(0.4)

    print()
    print("Done.")
    print("Total:", total)
    print("Downloaded:", downloaded)
    print("Cached:", cached)
    print("Failed:", failed)
    print("Restart dashboard with ./run_auto.sh")

if __name__ == "__main__":
    main()
