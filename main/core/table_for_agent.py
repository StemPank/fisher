import os
import global_variable
import sqlite3

def create(name):
    """
        Создание sqlite файла для агента
        и необходимых таблиц

        :name - имя агента
    """
    # Создаем соединение с SQLite
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')

    # Подключаемся к базе данных (если не существует, создастся автоматически)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Удаляем таблицы, если они уже существуют (чтобы избежать ошибок при повторном выполнении)
    cursor.execute(f"DROP TABLE IF EXISTS '{name}';")
    cursor.execute(f"DROP TABLE IF EXISTS 'trade{name}';")

    # Создаем таблицу Searches
    cursor.execute(f"""
        CREATE TABLE '{name}' (
            market TEXT,
            name TEXT,
            interval TEXT,
            time INTEGER,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume FLOAT
        );
    """)
    cursor.execute(f"""
        CREATE TABLE 'trade{name}' (
            market TEXT,
            name TEXT,
            time INTEGER,
            buy FLOAT,
            sale FLOAT,
            identifier INTEGER
        );
    """)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def drop(name):
    """
        Удаление sqlite файла агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    # Проверяем, существует ли файл перед удалением
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Файл {db_path} успешно удален.")
    else:
        print(f"Файл {db_path} не найден.")

def insert_data(name, data):
    """
        Вставка данных в таблицу агента

        :name - имя агента
        :data - список кортежей с данными
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Отладочная часть
    # print(f"Длина первого кортежа: {len(data)}")

    print("\rЗагружаем данные -", end='', flush=True)

    cursor.executemany(f"""
        INSERT INTO '{name}' (market, name, interval, time, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, data)

    print("\rЗагружаем данные -", end='', flush=True)

    conn.commit()
    conn.close()

def clear_table(name):
    """
        Очистка данных в таблице агента
        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Очищаем таблицу
    cursor.execute(f"DELETE FROM '{name}';")
    # cursor.execute("VACUUM;")  # Опционально: сжимает базу после удаления

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    print(f"Таблица '{name}' очищена.")


def get_first_row(name):
    """
        Получает первую строку из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{name}' ORDER BY time ASC LIMIT 1;")
    first_row = cursor.fetchone()

    conn.close()
    return first_row

def get_last_row(name):
    """
        Получает последнюю строку из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{name}' ORDER BY time DESC LIMIT 1;")
    last_row = cursor.fetchone()

    conn.close()
    return last_row

def get_all_data(name):
    """
        Получает все данные из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{name}';")
    first_row = cursor.fetchall()

    conn.close()
    return first_row

def get_data_to_graph(name):
    """
        Получает все данные из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT time, open, high, low, close FROM '{name}';")
    first_row = cursor.fetchall()

    conn.close()
    return first_row

