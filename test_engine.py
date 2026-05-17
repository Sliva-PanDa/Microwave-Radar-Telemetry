import unittest
import pandas as pd
import os
import csv
from data_engine import DataEngine

# Имя временного файла для безопасного тестирования (чтобы не сломать твою реальную базу)
TEST_FILE = 'test_radar_data.csv'


class TestDataEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Создается перед запуском ВСЕХ тестов. Делаем фейковую базу данных."""
        with open(TEST_FILE, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Эксперимент', 'Материал', 'e_Проницаемость', 'Толщина(мм)', 'Дистанция(см)', 'Энергия'])
            # Идеальные данные (Воздух)
            writer.writerow(['1', 'Воздух', '1', '0', '108.0', '100.0'])
            writer.writerow(['2', 'воздух', '1', '0', '110.0', '100.0'])
            # Пластик
            writer.writerow(['3', 'Пластик', '2.5', '2', '106.0', '100.0'])
            # Вода с разбросом (Проверка усреднения)
            writer.writerow(['4', 'Вода', '80', '160', '99.0', '63.0'])
            writer.writerow(['5', 'вода', '80', '160', '90.0', '45.0'])

    @classmethod
    def tearDownClass(cls):
        """Удаляет фейковую базу после завершения всех тестов"""
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def setUp(self):
        """Инициализация движка перед каждым тестом"""
        self.engine = DataEngine(filename=TEST_FILE)

    # --- ТЕСТ 1: Проверка загрузки данных ---
    def test_file_exists_handling(self):
        """Проверка, как система ведет себя, если файла нет"""
        bad_engine = DataEngine("fake_file.csv")
        self.assertEqual(bad_engine.get_summary_data(), {})
        self.assertEqual(bad_engine.get_raw_history(), [])

    # --- ТЕСТ 2: Очистка текста (Регистр) ---
    def test_data_cleaning_capitalization(self):
        """Проверка, что 'воздух' и 'Воздух' сливаются в одну категорию"""
        summary = self.engine.get_summary_data()
        self.assertIn("Воздух", summary)
        self.assertNotIn("воздух", summary)  # Маленькой буквы быть не должно

    # --- ТЕСТ 3: Математическое усреднение (Воздух) ---
    def test_math_averaging_air(self):
        """Проверка правильности усреднения энергии для Воздуха (100 + 100) / 2"""
        summary = self.engine.get_summary_data()
        self.assertEqual(summary["Воздух"], 100.0)

    # --- ТЕСТ 4: Математическое усреднение (Вода) ---
    def test_math_averaging_water(self):
        """Проверка правильности усреднения энергии для Воды (63 + 45) / 2 = 54"""
        summary = self.engine.get_summary_data()
        self.assertEqual(summary["Вода"], 54.0)

    # --- ТЕСТ 5: Проверка сортировки графика ---
    def test_sorting_order(self):
        """Проверка, что данные для графика отсортированы по убыванию энергии"""
        summary = self.engine.get_summary_data()
        keys = list(summary.keys())
        # Воздух/Пластик (100) должны быть первее Воды (54)
        self.assertLess(summary[keys[-1]], summary[keys[0]])

    # --- ТЕСТ 6: Чтение сырой истории ---
    def test_raw_history_length(self):
        """Проверка, что история возвращает правильное количество строк"""
        history = self.engine.get_raw_history()
        self.assertEqual(len(history), 5)  # 5 фейковых записей

    # --- ТЕСТ 7: Фильтрация таблицы по материалу ---
    def test_history_filtering(self):
        """Проверка работы фильтра таблицы (выбираем только 'Вода')"""
        water_history = self.engine.get_raw_history(material_filter="Вода")
        self.assertEqual(len(water_history), 2)  # У нас 2 записи воды
        self.assertEqual(water_history[0][1], "Вода")  # Проверяем колонку 'Материал'

    # --- ТЕСТ 8: Сортировка таблицы (Новые сверху) ---
    def test_history_reverse_sorting(self):
        """Проверка, что последняя запись (Эксперимент 5) идет первой в таблице"""
        history = self.engine.get_raw_history()
        self.assertEqual(int(history[0][0]), 5)

        # --- ТЕСТ 9: Аналитика (ИИ-советник) для Воздуха ---

    def test_analytics_air(self):
        """Проверка генерации детальной статистики для Воздуха"""
        stats = self.engine.get_material_stats("Воздух")
        self.assertIsNotNone(stats)
        self.assertEqual(stats['count'], 2)
        self.assertEqual(stats['epsilon'], 1.0)
        self.assertEqual(stats['avg_dist'], 109.0)  # (108+110)/2

    # --- ТЕСТ 10: Защита от дурака в аналитике ---
    def test_analytics_bad_input(self):
        """Проверка, что система не падает при запросе несуществующего материала"""
        stats = self.engine.get_material_stats("Криптонит")
        self.assertIsNone(stats)


if __name__ == '__main__':
    unittest.main(verbosity=2)