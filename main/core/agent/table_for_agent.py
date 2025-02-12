import os
import global_variable
import sqlite3

# Основная таблица
def insert_data(name, data):
    """
        Вставка данных в основную таблицу агента 

        :name - имя агента
        :data - список кортежей с данными
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Отладочная часть
    # print(f"Длина первого кортежа: {len(data)}")

    cursor.executemany(f"""
        INSERT INTO '{name}' (market, name, interval, time, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, data)

    conn.commit()
    conn.close()

def clear_table(name):
    """
        Очистка данных в основной таблице агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Очищаем таблицу
    cursor.execute(f"DELETE FROM '{name}';")

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
        Получает данные для графика из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT time, open, high, low, close FROM '{name}';")
    first_row = cursor.fetchall()

    conn.close()
    return first_row

# таблица trade 
def insert_data_trade(name, data):
    """
        Вставка данных в основную таблицу агента 

        :name - имя агента
        :data - список кортежей с данными
        data=[(market(str) - "bybit", 
                name(str) - "BTCUSDT", 
                time(int) - 1739335140000, 
                side(str) - "Buy","Sell", 
                price(float) - 95332.7, 
                identifier(int) - 1
        ),]
    """
    db_path = os.path.join(os.path.join(global_variable.AGENTS_FOLDER, name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executemany(f"""
        INSERT INTO 'trade{name}' (market, name, time, side, price, identifier)
        VALUES (?, ?, ?, ?, ?, ?);
    """, data)

    conn.commit()
    conn.close()