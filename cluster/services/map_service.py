import math
import os
from PyQt5.QtGui import QImage, QPainter, QColor, QPen, QFont, QPixmap
from config import MAP_TILE_ZOOM, MAP_TILE_ROOT, MAP_DEFAULT_CENTER_LAT, MAP_DEFAULT_CENTER_LON

class MapService:
    def __init__(self, zoom=MAP_TILE_ZOOM, tile_root=MAP_TILE_ROOT):
        self.zoom = zoom
        self.tile_root = tile_root
        os.makedirs(self.tile_root, exist_ok=True)

    def set_zoom(self, zoom):
        self.zoom = max(3, min(18, int(zoom)))

    def _deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        return xtile, ytile

    def _num2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    def _tile_path(self, z, x, y):
        return os.path.join(self.tile_root, str(z), str(x), f"{y}.png")

    def _find_tile_or_lower_zoom(self, z, x, y):
        path = self._tile_path(z, x, y)
        if os.path.exists(path):
            return path, z
        for fallback_z in range(z - 1, 2, -1):
            factor = 2 ** (z - fallback_z)
            fallback_path = self._tile_path(fallback_z, x // factor, y // factor)
            if os.path.exists(fallback_path):
                return fallback_path, fallback_z
        return None, z

    def pan(self, center_lat, center_lon, dx_pixels, dy_pixels):
        tile_size = 256
        xtile_f, ytile_f = self._deg2num(center_lat, center_lon, self.zoom)
        xtile_f -= dx_pixels / tile_size
        ytile_f -= dy_pixels / tile_size
        return self._num2deg(xtile_f, ytile_f, self.zoom)

    def render(self, lat, lon, width, height):
        if abs(lat) < 0.0001 and abs(lon) < 0.0001:
            lat = MAP_DEFAULT_CENTER_LAT
            lon = MAP_DEFAULT_CENTER_LON

        tile_size = 256
        xtile_f, ytile_f = self._deg2num(lat, lon, self.zoom)
        xtile = int(xtile_f)
        ytile = int(ytile_f)
        px = int((xtile_f - xtile) * tile_size)
        py = int((ytile_f - ytile) * tile_size)

        image = QImage(width, height, QImage.Format_RGB32)
        image.fill(QColor(15, 18, 24))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)

        start_x = width // 2 - px - tile_size
        start_y = height // 2 - py - tile_size

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                tx = xtile + dx
                ty = ytile + dy
                draw_x = start_x + (dx + 1) * tile_size
                draw_y = start_y + (dy + 1) * tile_size
                path, used_z = self._find_tile_or_lower_zoom(self.zoom, tx, ty)

                if path:
                    pix = QPixmap(path)
                    painter.drawPixmap(draw_x, draw_y, tile_size, tile_size, pix)
                    if used_z != self.zoom:
                        painter.fillRect(draw_x, draw_y, tile_size, 24, QColor(0, 0, 0, 120))
                        painter.setPen(QColor(255, 210, 120))
                        painter.setFont(QFont("Arial", 9))
                        painter.drawText(draw_x + 8, draw_y + 17, f"fallback z{used_z}")
                else:
                    painter.fillRect(draw_x, draw_y, tile_size, tile_size, QColor(28, 32, 40))
                    painter.setPen(QColor(70, 76, 88))
                    painter.drawRect(draw_x, draw_y, tile_size, tile_size)
                    painter.setFont(QFont("Arial", 10))
                    painter.drawText(draw_x + 12, draw_y + 22, f"z{self.zoom}/{tx}/{ty}")
                    painter.drawText(draw_x + 12, draw_y + 42, "tile missing")
                    painter.drawText(draw_x + 12, draw_y + 62, "run download_tiles.py")

        cx = width // 2
        cy = height // 2
        painter.setBrush(QColor(0, 180, 255, 220))
        painter.setPen(QPen(QColor(255, 255, 255, 140), 1))
        painter.drawEllipse(cx - 8, cy - 8, 16, 16)
        painter.drawLine(cx - 18, cy, cx + 18, cy)
        painter.drawLine(cx, cy - 18, cx, cy + 18)

        painter.fillRect(16, 16, 390, 58, QColor(10, 14, 20, 190))
        painter.setPen(QColor(240, 245, 250))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(28, 38, "Offline Map")
        painter.setPen(QColor(185, 192, 202))
        painter.setFont(QFont("Arial", 11))
        painter.drawText(28, 58, f"{lat:.5f}, {lon:.5f}  z{self.zoom}")

        painter.fillRect(16, height - 42, 500, 28, QColor(10, 14, 20, 170))
        painter.setPen(QColor(185, 192, 202))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(28, height - 22, "Ethernet internet: run ./run_download_maps.sh to fill missing tiles")
        painter.end()
        return image
