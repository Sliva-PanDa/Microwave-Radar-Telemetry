import pandas as pd
import os


class DataEngine:
    def __init__(self, filename='radar_physics_data.csv'):
        self.filename = filename

    def get_summary_data(self):
        """Читает CSV и возвращает усредненные данные для графика"""
        if not os.path.exists(self.filename):
            return {}

        try:
            df = pd.read_csv(self.filename, sep=';', encoding='utf-8-sig')
            df['Материал'] = df['Материал'].astype(str).str.strip().str.capitalize()

            summary = df.groupby('Материал')['Энергия'].mean().reset_index()
            summary = summary.sort_values(by='Энергия', ascending=False)

            return dict(zip(summary['Материал'], summary['Энергия']))
        except Exception as e:
            print(f"Ошибка в data_engine (summary): {e}")
            return {}

    def get_raw_history(self, material_filter="ВСЕ ЗАМЕРЫ"):
        """Возвращает данные для таблицы (все 6 колонок) с фильтрацией"""
        if not os.path.exists(self.filename):
            return []
        try:
            df = pd.read_csv(self.filename, sep=';', encoding='utf-8-sig')
            df['Материал'] = df['Материал'].astype(str).str.strip().str.capitalize()

            # Фильтруем, если выбран конкретный материал
            if material_filter != "ВСЕ ЗАМЕРЫ":
                df = df[df['Материал'] == material_filter]

            # Сортируем по номеру эксперимента (новые сверху)
            df = df.sort_values(by='Эксперимент', ascending=False)

            return df.values.tolist()
        except Exception as e:
            print(f"Ошибка в data_engine (history): {e}")
            return []

    def get_material_stats(self, material):
        """Считает глубокую аналитику для выбранного материала"""
        if not os.path.exists(self.filename) or material == "ВСЕ ЗАМЕРЫ":
            return None

        try:
            df = pd.read_csv(self.filename, sep=';', encoding='utf-8-sig')
            df['Материал'] = df['Материал'].astype(str).str.strip().str.capitalize()
            df_mat = df[df['Материал'] == material]

            if df_mat.empty: return None

            stats = {
                "count": len(df_mat),
                "avg_dist": round(df_mat['Дистанция(см)'].mean(), 1),
                "avg_energy": round(df_mat['Энергия'].mean(), 1),
                "epsilon": df_mat['e_Проницаемость'].iloc[0],
                "thickness": df_mat['Толщина(мм)'].iloc[0]
            }
            return stats
        except:
            return None