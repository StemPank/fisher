import os
import global_variable
import sqlite3

from utils.logging import logger_agent

def delete_unwanted_tables(name):

    """
        Удаление всех таблиц кроме основных 

        :name - имя агента
    """
    try:
        logger_agent.debug(f"Запрос на удаление таблиц кроме основных.")
        # Подключаемся к базе данных
        db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получаем список всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        keep_tables = [f'{name}', f'trade{name}', 'results']
        # Итерируем по таблицам
        for table in tables:
            table_name = table[0]
            if table_name not in keep_tables:
                # Если таблица не в списке исключений, удаляем ее
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                logger_agent.info(f"Таблица {table_name} удалена.")

        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger_agent.critical(f"Ошибка удаления таблиц БД (table_for_agent.py:7): {e}")
        return False

# Основная таблица
def insert_data(name, data):
    """
        Вставка данных в основную таблицу агента 

        :name - имя агента
        :data - список кортежей с данными
    """
    logger_agent.debug(f"Запрос на добавление данных в основную таблицу '{name}'.")
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
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

def insert_data_stream(name, data):
    """
        Вставка данных в основную таблицу агента с вебсокета.
        Если значение 'time' последней строки совпадает с входящими данными, строка обновляется.
        Иначе данные добавляются как новая запись.

        :name - имя агента
        :data - список кортежей с данными
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем последнюю строку
    cursor.execute(f"SELECT time FROM '{name}' ORDER BY time DESC LIMIT 1;")
    last_row = cursor.fetchone()  # Получаем кортеж (time,)

    new_time = data[0][3]  # Индекс 3, так как 'time' находится на 4-м месте в кортеже

    if last_row and last_row[0] == new_time:
        # Обновляем последнюю строку, если 'time' совпадает
        cursor.execute(f"""
            UPDATE '{name}'
            SET market = ?, name = ?, interval = ?, open = ?, high = ?, low = ?, close = ?, volume = ?
            WHERE time = ?;
        """, (*data[0][:3], *data[0][4:], new_time))
    else:
        # Вставляем новую строку, если 'time' отличается
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
    logger_agent.debug(f"Запрос на отчистку основной таблицы '{name}'.")
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Очищаем таблицу
    cursor.execute(f"DELETE FROM '{name}';")

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    logger_agent.debug(f"Таблица '{name}' очищена.")

def get_data_main_table(name):
    """
        Получает все данные из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{name}';")
    first_row = cursor.fetchall()

    conn.close()
    return first_row

def get_first_row(name):
    """
        Получает первую строку из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
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
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM '{name}' ORDER BY time DESC LIMIT 1;")
    last_row = cursor.fetchone()

    conn.close()
    return last_row

# Таблица ордеров
def insert_data_order(name, data):
    """
    Запись данных в таблицу ордеров
    """
    try:
        logger_agent.debug(f"Запрос на добавление данных в таблицу ордеров '{name}'.")
        db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Отладочная часть
        # print(f"Длина первого кортежа: {len(data)}")

        cursor.executemany(f"""
            INSERT INTO 'trade{name}' (identifier, time, price, quantity, side)
            VALUES (?, ?, ?, ?, ?);
        """, data)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger_agent.critical(f"Ошибка добавление данных: {e}")
        return False
    
def clear_data_order_table(name):
    """
        Очистка данных в таблице ордеров агента

        :name - имя агента
    """
    logger_agent.debug(f"Запрос на отчистку таблице ордеров агента 'trade{name}'.")
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Очищаем таблицу
    cursor.execute(f"DELETE FROM 'trade{name}';")

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    logger_agent.debug(f"Таблица 'trade{name}' очищена.")

def get_data_trade_table(name):
    """
        Получает все данные из таблицы торговли агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT identifier, time, price, quantity, side FROM 'trade{name}';")
    result = cursor.fetchall()

    conn.close()
    return result

# Результаты
def create_a_results_table(name):
    """
        Создание таблицы результатов

        :name - имя агента
    """
    logger_agent.debug(f"Запрос на создание таблицы результатов агента: {name}")
    
    # Создаем путь к базе данных
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')

    # Подключаемся к базе данных (если не существует, создастся автоматически)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Удаляем таблицы, если они уже существуют (чтобы избежать ошибок при повторном выполнении)
    cursor.execute(f"DROP TABLE IF EXISTS results;")

    # Создаем таблицу Searches
    cursor.execute(f"""
        CREATE TABLE results (
                    ideniteration INTEGER,
                    total_transactions INTEGER,
                    profitable_trades INTEGER,
                    unprofitable_trades INTEGER,
                    total_profit FLOAT,
                    total_loss FLOAT,
                    net_profit FLOAT,
                    avg_profit_per_trade FLOAT,
                    win_rate FLOAT,
                    profit_factor FLOAT,
                    expectancy FLOAT,
                    max_drawdown FLOAT,
                    recovery_factor FLOAT,
                    sharpe_ratio FLOAT,
                    calmar_ratio FLOAT,
                    roi FLOAT,
                    roe FLOAT,
                    std_dev FLOAT,
                    avg_trade_duration FLOAT,
                    purchase_transaction INTEGER,
                    buy_profitable_trades INTEGER,
                    buy_unprofitable_trades INTEGER,
                    buy_total_profit FLOAT,
                    buy_total_loss FLOAT,
                    buy_net_profit FLOAT,
                    buy_avg_profit_per_trade FLOAT,
                    buy_win_rate FLOAT,
                    buy_profit_factor FLOAT,
                    buy_expectancy FLOAT,
                    buy_max_drawdown FLOAT,
                    buy_recovery_factor FLOAT,
                    buy_sharpe_ratio FLOAT,
                    buy_calmar_ratio FLOAT,
                    buy_roi FLOAT,
                    buy_roe FLOAT,
                    buy_std_dev FLOAT,
                    buy_avg_trade_duration FLOAT,
                    sales_transaction INTEGER,
                    sell_profitable_trades INTEGER,
                    sell_unprofitable_trades INTEGER,
                    sell_total_profit FLOAT,
                    sell_total_loss FLOAT,
                    sell_net_profit FLOAT,
                    sell_avg_profit_per_trade FLOAT,
                    sell_win_rate FLOAT,
                    sell_profit_factor FLOAT,
                    sell_expectancy FLOAT,
                    sell_max_drawdown FLOAT,
                    sell_recovery_factor FLOAT,
                    sell_sharpe_ratio FLOAT,
                    sell_calmar_ratio FLOAT,
                    sell_roi FLOAT,
                    sell_roe FLOAT,
                    sell_std_dev FLOAT,
                    sell_avg_trade_duration FLOAT,
               
        );
    """)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def create_a_results_table_if_it_does_not_exist(name):
    """
    Создание таблицы результатов, если она не существует.

    :name - имя агента
    """
    logger_agent.debug(f"Запрос на создание таблицы результатов агента: {name}, если она не существует.")
    
    # Создаем путь к базе данных
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')

    # Подключаемся к базе данных (если не существует, создастся автоматически)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу, если ее нет
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS results (
                    ideniteration INTEGER,
                    total_transactions INTEGER,
                    profitable_trades INTEGER,
                    unprofitable_trades INTEGER,
                    total_profit FLOAT,
                    total_loss FLOAT,
                    net_profit FLOAT,
                    avg_profit_per_trade FLOAT,
                    win_rate FLOAT,
                    profit_factor FLOAT,
                    expectancy FLOAT,
                    max_drawdown FLOAT,
                    recovery_factor FLOAT,
                    sharpe_ratio FLOAT,
                    calmar_ratio FLOAT,
                    roi FLOAT,
                    roe FLOAT,
                    std_dev FLOAT,
                    avg_trade_duration FLOAT,
                    purchase_transaction INTEGER,
                    buy_profitable_trades INTEGER,
                    buy_unprofitable_trades INTEGER,
                    buy_total_profit FLOAT,
                    buy_total_loss FLOAT,
                    buy_net_profit FLOAT,
                    buy_avg_profit_per_trade FLOAT,
                    buy_win_rate FLOAT,
                    buy_profit_factor FLOAT,
                    buy_expectancy FLOAT,
                    buy_max_drawdown FLOAT,
                    buy_recovery_factor FLOAT,
                    buy_sharpe_ratio FLOAT,
                    buy_calmar_ratio FLOAT,
                    buy_roi FLOAT,
                    buy_roe FLOAT,
                    buy_std_dev FLOAT,
                    buy_avg_trade_duration FLOAT,
                    sales_transaction INTEGER,
                    sell_profitable_trades INTEGER,
                    sell_unprofitable_trades INTEGER,
                    sell_total_profit FLOAT,
                    sell_total_loss FLOAT,
                    sell_net_profit FLOAT,
                    sell_avg_profit_per_trade FLOAT,
                    sell_win_rate FLOAT,
                    sell_profit_factor FLOAT,
                    sell_expectancy FLOAT,
                    sell_max_drawdown FLOAT,
                    sell_recovery_factor FLOAT,
                    sell_sharpe_ratio FLOAT,
                    sell_calmar_ratio FLOAT,
                    sell_roi FLOAT,
                    sell_roe FLOAT,
                    sell_std_dev FLOAT,
                    sell_avg_trade_duration FLOAT
        );
    """)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def insert_data_to_results_table(name, data):
    """
    Вставка данных в таблицу results с проверкой ideniteration

    :name - имя агента
    :data - данные для вставки в виде кортежа (например, (ideniteration, total_transactions, ...))
    """
    logger_agent.debug(f"Запрос на вставку данных в таблицу результатов агента: {name}")
    
    # Создаем путь к базе данных
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')

    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Извлекаем ideniteration из кортежа (предполагаем, что он первый элемент)
    ideniteration = data[0]

    # Если ideniteration = 1, удаляем все записи
    if ideniteration == 1:
        cursor.execute("DELETE FROM results")

    # Если ideniteration > 1, оставляем только записи с ideniteration = ideniteration - 1 и удаляем все остальные
    elif ideniteration > 1:
        cursor.execute(f"DELETE FROM results WHERE ideniteration > {ideniteration - 1}")

    # Формируем SQL-запрос для вставки данных
    # Список столбцов в таблице, если он фиксированный
    columns = ("ideniteration", "total_transactions", "profitable_trades", "unprofitable_trades", "total_profit", 
               "total_loss", "net_profit", "avg_profit_per_trade", "win_rate", "profit_factor", "expectancy", 
               "max_drawdown", "recovery_factor", "sharpe_ratio", "calmar_ratio", "roi", "roe", "std_dev", 
               "avg_trade_duration", "purchase_transaction", "buy_profitable_trades", "buy_unprofitable_trades", 
               "buy_total_profit", "buy_total_loss", "buy_net_profit", "buy_avg_profit_per_trade", 
               "buy_win_rate", "buy_profit_factor", "buy_expectancy", "buy_max_drawdown", "buy_recovery_factor", 
               "buy_sharpe_ratio", "buy_calmar_ratio", "buy_roi", "buy_roe", "buy_std_dev", "buy_avg_trade_duration", 
               "sales_transaction", "sell_profitable_trades", "sell_unprofitable_trades", "sell_total_profit", 
               "sell_total_loss", "sell_net_profit", "sell_avg_profit_per_trade", "sell_win_rate", 
               "sell_profit_factor", "sell_expectancy", "sell_max_drawdown", "sell_recovery_factor", 
               "sell_sharpe_ratio", "sell_calmar_ratio", "sell_roi", "sell_roe", "sell_std_dev", 
               "sell_avg_trade_duration")
    
    # Формируем SQL-запрос для вставки данных
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO results ({', '.join(columns)}) VALUES ({placeholders})"

    # Выполняем вставку
    cursor.execute(sql, data)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

# Индикаторы
def create_indicator(name, name_indicator, index_indicator):
    """
        Создание таблицы индикатора

        :name - имя агента
    """
    path = global_variable.setting_file("folder_path")
    logger_agent.debug(f"Запрос на создание таблицы индикатора, путь к файлу БД агента: {path}")
    # Создаем соединение с SQLite
    db_path = os.path.join(path, f'agent_data_{name}.sqlite')

    # Подключаемся к базе данных (если не существует, создастся автоматически)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Удаляем таблицы, если они уже существуют (чтобы избежать ошибок при повторном выполнении)
    cursor.execute(f"DROP TABLE IF EXISTS '{name_indicator}''{index_indicator}';")

    # Создаем таблицу Searches
    cursor.execute(f"""
        CREATE TABLE '{name_indicator}''{index_indicator}' (
            period FLOAT,
            time INTEGER,
            value FLOAT
        );
    """)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def checking_the_creation_of_the_indicator_table(name, name_indicator, index_indicator):
    """
        Создание таблицы индикатора

        :name - имя агента
    """
    path = global_variable.setting_file("folder_path")
    logger_agent.debug(f"Запрос на создание таблицы индикатора, если ее нет, путь к файлу БД агента: {os.path.join(path, name)}")
    # Создаем соединение с SQLite
    db_path = os.path.join(os.path.join(path, name), f'agent_data_{name}.sqlite')

    # Подключаемся к базе данных (если не существует, создастся автоматически)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем, существует ли таблица
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {name_indicator}{str(index_indicator)} (
            period FLOAT,
            time INTEGER,
            value FLOAT
        )
    """)
    conn.commit()

    cursor.execute(f"SELECT * FROM {name_indicator}{str(index_indicator)}")
    last_db_entry = cursor.fetchall()
    last_db_time = last_db_entry if last_db_entry else None

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    return last_db_time

def clear_table_indicator(name, name_indicator, index_indicator):
    """
        Очистка данных в таблице индикатора

        :name - имя агента
    """
    logger_agent.debug(f"Запрос на отчистку таблицы {name_indicator}{str(index_indicator)}")
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    
    # Подключаемся к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Очищаем таблицу
    cursor.execute(f"DELETE FROM {name_indicator}{str(index_indicator)};")

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    logger_agent.debug(f"Таблица {name_indicator}{index_indicator} очищена.")

def insert_data_indicator(name, name_indicator, index_indicator, data):
    """
        Вставка данных в основную таблицу агента 

        :name - имя агента
        :data - список кортежей с данными
    """
    logger_agent.debug(f"Запрос на добавление данных в таблицу {name_indicator}{index_indicator}.")
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Отладочная часть
    # print(f"Длина первого кортежа: {len(data)}")

    cursor.executemany(f"""
        INSERT INTO {name_indicator}{str(index_indicator)} (period, time, value)
        VALUES (?, ?, ?);
    """, data)

    conn.commit()
    conn.close()

