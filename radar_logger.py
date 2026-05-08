import serial
import time
import csv
import os

COM_PORT = 'COM6'  # Проверь свой порт!
BAUD_RATE = 115200
FILE_NAME = 'radar_physics_data.csv'

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ ---

def get_next_experiment_id():
    """Читает файл и находит следующий свободный номер эксперимента"""
    if not os.path.exists(FILE_NAME):
        return 1
    
    max_id = 0
    with open(FILE_NAME, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader, None)  # Пропускаем заголовки
        for row in reader:
            if row and row[0].isdigit():
                max_id = max(max_id, int(row[0]))
    return max_id + 1

def delete_experiment(exp_id):
    """Удаляет строку с указанным номером эксперимента из CSV"""
    if not os.path.exists(FILE_NAME):
        return False
        
    rows = []
    deleted = False
    with open(FILE_NAME, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=';')
        header = next(reader, None)
        if header:
            rows.append(header)
        for row in reader:
            if row and row[0] == str(exp_id):
                deleted = True
                continue  # Пропускаем эту строку (удаляем)
            rows.append(row)
            
    if deleted:
        with open(FILE_NAME, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(rows)
    return deleted

# --- ИНИЦИАЛИЗАЦИЯ ---

# Создаем файл с заголовками, если его нет
try:
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Эксперимент', 'Материал', 'e_Проницаемость', 
                             'Толщина(мм)', 'Дистанция(см)', 'Энергия'])
except Exception:
    pass

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Подключение к радару на {COM_PORT} УСПЕШНО")
    time.sleep(2) 
    ser.reset_input_buffer()
except Exception:
    print("\nОШИБКА COM-ПОРТА! Закрой Монитор порта в Arduino IDE!")
    exit()

print("\n" + "="*55)
print("   ЛАБОРАТОРНЫЙ КОМПЛЕКС СВЧ-ИЗЛУЧЕНИЯ ГОТОВ")
print("="*55)

# --- ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ ---

while True:
    next_id = get_next_experiment_id()
    print(f"\nТекущий номер для записи: [ {next_id} ]")
    print("  [ENTER] - Начать новый замер")
    print("  [ d ]   - Удалить ошибочный замер")
    print("  [ q ]   - Выйти из программы")
    
    action = input("Твой выбор: ").strip().lower()
    
    if action == 'q':
        print("Работа завершена. Данные сохранены.")
        break
        
    elif action == 'd':
        del_id = input("Введи НОМЕР эксперимента, который нужно удалить: ").strip()
        if del_id.isdigit():
            if delete_experiment(del_id):
                print(f"[*] Эксперимент №{del_id} УСПЕШНО УДАЛЕН из базы!")
            else:
                print(f"[!] ОШИБКА: Эксперимент №{del_id} не найден.")
        else:
            print("[!] ОШИБКА: Номер должен быть числом.")
        continue
        
    elif action == '':
        # Нажали ENTER - начинаем замер!
        exp_name = str(next_id)
        
        print(f"\n--- НАСТРОЙКА ЭКСПЕРИМЕНТА №{exp_name} ---")
        material = input("Материал (Воздух, Пластик, Вода): ")
        epsilon = input("Проницаемость (1, 2.5, 80): ")
        thickness = input("Толщина (мм): ")
        
        print("\n[ОЖИДАНИЕ] Махни рукой -> Сядь -> ДЕРГНИ НИТКУ!")
        
        ser.reset_input_buffer() 
        measurements = []
        
        # СЛУШАЕМ РАДАР
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if "[ТРИГГЕР]" in line:
                        print(" > Триггер сработал! Дергай нитку...")
                        
                    if "ЗАМЕР | Дистанция:" in line:
                        parts = line.split('|')
                        dist = int(parts[1].replace("Дистанция:", "").replace("см", "").strip())
                        energy = int(parts[2].replace("Энергия:", "").strip())
                        
                        measurements.append((dist, energy))
                        print(f"   Выстрел {len(measurements)}/4: Дальность {dist} см, Энергия {energy}")
                    
                    # Если собрали 4 замера или радар не нашел цель
                    if len(measurements) >= 4 or ("Цель не найдена" in line and len(measurements) > 0):
                        time.sleep(0.5) 
                        break
                except Exception:
                    pass 
                    
        # ЗАПИСЬ РЕЗУЛЬТАТОВ
        if len(measurements) > 0:
            avg_dist = round(sum(d for d, e in measurements) / len(measurements), 1)
            avg_energy = round(sum(e for d, e in measurements) / len(measurements), 1)
            
            print(f"\n[ИТОГ] Мишень: {avg_dist} см | Мощность (P): {avg_energy}/100")
            
            with open(FILE_NAME, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow([exp_name, material, epsilon, thickness, avg_dist, avg_energy])
            print(f"[*] Данные Эксперимента №{exp_name} успешно сохранены в CSV!")
        else:
            print("\n[ОШИБКА] Радар не увидел мишень. (Возможно, сигнал заблокирован водой!)")