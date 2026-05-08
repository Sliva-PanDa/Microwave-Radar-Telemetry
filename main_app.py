# Файл: main_app.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from data_engine import DataEngine
from radar_canvas import RadarAnimation

BG_APP = "#121212"
BG_PANEL = "#1E1E1E"
TEXT_LIGHT = "#CCCCCC"
ACCENT_BLUE = "#007acc"
ACCENT_RED = "#D32F2F"


class RadarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаборатория Радиофизики 2.0 (СВЧ 24 ГГц)")
        self.setGeometry(50, 50, 1400, 900)
        self.setStyleSheet(f"background-color: {BG_APP}; color: {TEXT_LIGHT};")

        self.engine = DataEngine()
        self.current_material = "ВСЕ ЗАМЕРЫ"

        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- ЛЕВАЯ ПАНЕЛЬ ---
        left_panel = QFrame()
        left_panel.setFixedWidth(260)
        left_panel.setStyleSheet(f"background-color: {BG_PANEL}; border-radius: 8px;")
        left_layout = QVBoxLayout(left_panel)

        title_lbl = QLabel("СВЧ-АНАЛИЗАТОР\nHLK-LD2410")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(f"color: {ACCENT_BLUE}; padding: 10px 0px;")
        left_layout.addWidget(title_lbl)

        # Кнопка "ОБЩИЙ СПИСОК"
        self.btn_all = QPushButton("ОБЩИЙ СПИСОК")
        self.btn_all.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_all.setCursor(Qt.PointingHandCursor)
        self.btn_all.setStyleSheet(f"background-color: {ACCENT_BLUE}; color: white; padding: 12px; border-radius: 5px;")
        self.btn_all.clicked.connect(lambda: self.change_material("ВСЕ ЗАМЕРЫ"))
        left_layout.addWidget(self.btn_all)

        self.buttons_layout = QVBoxLayout()
        left_layout.addLayout(self.buttons_layout)
        left_layout.addStretch()

        # НОВАЯ ФИЧА: Кнопка ЭКСПОРТ ГРАФИКА
        export_btn = QPushButton("💾 Экспорт Графика (PNG)")
        export_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("background-color: #8E44AD; color: white; padding: 10px; border-radius: 5px;")
        export_btn.clicked.connect(self.export_chart)
        left_layout.addWidget(export_btn)

        refresh_btn = QPushButton("⟳ ОБНОВИТЬ БАЗУ")
        refresh_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(
            "background-color: #2ea043; color: white; padding: 12px; border-radius: 5px; margin-top: 10px;")
        refresh_btn.clicked.connect(self.refresh_data)
        left_layout.addWidget(refresh_btn)

        main_layout.addWidget(left_panel)

        # --- ПРАВАЯ ПАНЕЛЬ ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # ВЕРХ: График
        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"background-color: {BG_PANEL}; border-radius: 8px;")
        chart_layout = QVBoxLayout(chart_frame)

        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.fig.patch.set_facecolor(BG_PANEL)
        self.ax.set_facecolor(BG_PANEL)
        self.canvas = FigureCanvas(self.fig)
        chart_layout.addWidget(self.canvas)
        right_layout.addWidget(chart_frame, stretch=4)

        # СРЕДИНА: Карточка аналитики (УВЕЛИЧЕН ШРИФТ И ДОБАВЛЕН ФИЗИЧЕСКИЙ ВЫВОД)
        self.stat_frame = QFrame()
        self.stat_frame.setStyleSheet(f"background-color: #2A2A2A; border-radius: 8px;")
        stat_layout = QHBoxLayout(self.stat_frame)
        self.stat_text = QLabel("Режим общего обзора. Выберите материал слева для глубокого анализа.")
        self.stat_text.setFont(QFont("Segoe UI", 12))
        self.stat_text.setStyleSheet("color: #E0E0E0; padding: 10px;")
        stat_layout.addWidget(self.stat_text)
        right_layout.addWidget(self.stat_frame, stretch=1)

        # НИЗ: Разделен пополам
        bottom_layout = QHBoxLayout()

        # Анимация
        anim_frame = QFrame()
        anim_frame.setStyleSheet(f"background-color: {BG_PANEL}; border-radius: 8px;")
        anim_layout = QVBoxLayout(anim_frame)
        anim_title = QLabel("Живая симуляция (Real-time)")
        anim_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        anim_layout.addWidget(anim_title, alignment=Qt.AlignCenter)

        self.radar_anim = RadarAnimation()
        anim_layout.addWidget(self.radar_anim)
        bottom_layout.addWidget(anim_frame, stretch=1)

        # Таблица (Все 6 колонок)
        table_frame = QFrame()
        table_frame.setStyleSheet(f"background-color: {BG_PANEL}; border-radius: 8px;")
        table_layout = QVBoxLayout(table_frame)

        self.table_title = QLabel("Журнал измерений (Все)")
        self.table_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        table_layout.addWidget(self.table_title, alignment=Qt.AlignCenter)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["№", "Материал", "e", "Толщина", "Дистанция", "Энергия"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: #161A1E; color: #D4D4D4; border: 1px solid #333; gridline-color: #333; }}
            QHeaderView::section {{ background-color: #2D2D30; color: white; padding: 6px; font-weight: bold; border: 1px solid #1e1e1e; }}
            QTableWidget::item:selected {{ background-color: #007acc; }}
        """)
        table_layout.addWidget(self.table)
        bottom_layout.addWidget(table_frame, stretch=1)

        right_layout.addLayout(bottom_layout, stretch=4)
        main_layout.addWidget(right_panel)

    def change_material(self, mat):
        self.current_material = mat
        self.refresh_data()

    def refresh_data(self):
        data_dict = self.engine.get_summary_data()
        raw_data = self.engine.get_raw_history(self.current_material)

        self.build_buttons(data_dict)
        self.update_table(raw_data)
        self.update_chart(data_dict)
        self.update_analytics()

        energy = data_dict.get(self.current_material, 100) if self.current_material != "ВСЕ ЗАМЕРЫ" else 100
        self.radar_anim.set_data(self.current_material, energy)

    def build_buttons(self, data_dict):
        for i in reversed(range(self.buttons_layout.count())):
            self.buttons_layout.itemAt(i).widget().setParent(None)

        if not data_dict:
            return

        for mat in data_dict.keys():
            btn = QPushButton(mat.upper())
            btn.setFont(QFont("Segoe UI", 10))
            btn.setCursor(Qt.PointingHandCursor)
            if mat == self.current_material:
                btn.setStyleSheet("background-color: #e51400; color: white; padding: 10px; border-radius: 5px;")
            else:
                btn.setStyleSheet("background-color: #333337; color: white; padding: 10px; border-radius: 5px;")

            btn.clicked.connect(lambda checked, m=mat: self.change_material(m))
            self.buttons_layout.addWidget(btn)

    def update_table(self, raw_data):
        self.table_title.setText(f"Журнал измерений ({self.current_material})")
        self.table.setRowCount(len(raw_data))
        for row_idx, row_data in enumerate(raw_data):
            for col_idx, value in enumerate(row_data[:6]):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def update_chart(self, data_dict):
        self.ax.clear()
        if not data_dict: return

        materials = list(data_dict.keys())
        energies = list(data_dict.values())

        colors = [ACCENT_RED if m == self.current_material else ACCENT_BLUE for m in materials]
        bars = self.ax.bar(materials, energies, color=colors, width=0.4)

        for bar in bars:
            yval = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 2, f"{yval:.1f}",
                         ha='center', va='bottom', color='white', fontweight='bold', fontsize=11)

        self.ax.set_ylim(0, 110)
        self.ax.grid(axis='y', linestyle=':', alpha=0.2)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#444')
        self.ax.spines['bottom'].set_color('#444')
        self.ax.tick_params(colors=TEXT_LIGHT)
        self.ax.set_title(f"Спектр отражения 24 ГГц", color='white', fontsize=14, fontweight='bold', pad=10)
        self.fig.tight_layout()
        self.canvas.draw()

    def update_analytics(self):
        if self.current_material == "ВСЕ ЗАМЕРЫ":
            self.stat_text.setText(
                "Режим общего обзора. В таблице показаны все замеры.\nВыберите материал слева для получения физических расчетов.")
            return

        stats = self.engine.get_material_stats(self.current_material)
        if stats:
            loss = 100 - stats['avg_energy']

            # ИИ-советник (Физический вывод)
            if stats['avg_energy'] > 85:
                conclusion = "Материал является РАДИОПРОЗРАЧНЫМ (СВЧ-линза)."
            elif stats['avg_energy'] > 30:
                conclusion = "Материал обладает СРЕДНИМ ПОГЛОЩЕНИЕМ СВЧ-волн."
            else:
                conclusion = "ПОЛНАЯ РАДИОБЛОКИРОВКА. Сильное затухание сигнала (СВЧ-щит)."

            text = (f" АНАЛИТИКА МАТЕРИАЛА: {self.current_material.upper()} \n"
                    f"Диэлектрическая проницаемость (e): {stats['epsilon']}   |   Толщина преграды: {stats['thickness']} мм   |   Затухание СВЧ-сигнала: {loss:.1f}%\n"
                    f"Физический вывод: {conclusion}")
            self.stat_text.setText(text)

    def export_chart(self):
        """НОВАЯ ФИЧА: Сохранение графика в PNG для курсовой"""
        try:
            filename = f"Graph_{self.current_material}.png"
            self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=BG_PANEL)
            QMessageBox.information(self, "Успех!",
                                    f"График сохранен в высоком качестве (300 DPI)\nв папку проекта как:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить график: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RadarApp()
    window.show()
    sys.exit(app.exec_())