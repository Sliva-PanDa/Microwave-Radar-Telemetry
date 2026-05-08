from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont


class RadarAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        self.material = "ВСЕ ЗАМЕРЫ"
        self.energy = 100.0
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def set_data(self, material, energy):
        self.material = material
        self.energy = energy

    def update_animation(self):
        self.phase += 6
        if self.phase > 100:
            self.phase = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width, height = self.width(), self.height()
        mid_y = height // 2
        radar_x, obstacle_x, foil_x = 50, width // 2, width - 80

        # Фон
        painter.fillRect(0, 0, width, height, QColor("#161A1E"))

        # Радар
        painter.setBrush(QBrush(QColor("#E51400")))
        painter.setPen(Qt.NoPen)
        painter.drawRect(radar_x - 20, mid_y - 20, 40, 40)
        painter.setBrush(QBrush(QColor("#FFD700")))
        painter.drawRect(radar_x, mid_y - 10, 10, 20)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.drawText(radar_x - 22, mid_y + 35, "РАДАР")

        if self.material == "ВСЕ ЗАМЕРЫ":
            # Режим сканирования (просто радар и длинные волны)
            self.draw_waves(painter, radar_x, width, width, mid_y, True)
            painter.setPen(QColor("#888888"))
            painter.drawText(width // 2 - 50, mid_y, "РЕЖИМ ОБЗОРА")
            return

        # Фольга
        painter.setPen(QPen(QColor("#CCCCCC"), 4))
        painter.drawLine(foil_x, mid_y - 60, foil_x, mid_y + 60)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(foil_x - 25, mid_y - 70, "МИШЕНЬ")

        # Преграда и Волны
        self.draw_obstacle(painter, obstacle_x, mid_y)
        self.draw_waves(painter, radar_x, obstacle_x, foil_x, mid_y, False)

    def draw_obstacle(self, painter, x, y):
        mat_lower = self.material.lower()
        if "воздух" in mat_lower: return

        if "пластик" in mat_lower:
            painter.setBrush(QBrush(QColor(100, 200, 255, 60)))
            painter.setPen(QPen(QColor(100, 200, 255, 150), 2))
        elif "вод" in mat_lower:
            painter.setBrush(QBrush(QColor(10, 100, 200, 200)))
            painter.setPen(QPen(QColor(50, 150, 255), 2))
        else:
            painter.setBrush(QBrush(QColor(150, 150, 150, 100)))
            painter.setPen(QPen(QColor(200, 200, 200), 2))

        painter.drawRoundedRect(x - 20, y - 70, 40, 140, 10, 10)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(x - 30, y - 80, self.material)

    def draw_waves(self, painter, start_x, mid_x, end_x, y, is_all_mode):
        max_radius = end_x - start_x if (self.energy > 30 or is_all_mode) else mid_x - start_x

        for i in range(4):
            radius = ((self.phase + i * 25) % 100) / 100.0 * max_radius
            if radius <= 0: continue

            alpha = int(255 * (1 - (radius / max_radius)))

            if is_all_mode:
                color = QColor(100, 150, 255, alpha)
            elif self.energy > 30:
                color = QColor(0, 255, 150, alpha)
            else:
                color = QColor(255, 50, 50, alpha)

            painter.setPen(QPen(color, 3))
            rect = QRectF(start_x - radius, y - radius, radius * 2, radius * 2)
            painter.drawArc(rect, -30 * 16, 60 * 16)

        if self.energy <= 30 and not is_all_mode:
            painter.setPen(QPen(QColor(255, 0, 0, 150), 4, Qt.DotLine))
            painter.drawLine(mid_x - 25, y - 50, mid_x - 25, y + 50)