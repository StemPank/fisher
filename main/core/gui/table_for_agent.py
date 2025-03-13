import os
import global_variable
import sqlite3

from utils.logging import logger

def create(name, path):
    """
        Создание sqlite файла для агента
        и необходимых таблиц

        :name - имя агента
    """
    try:
        # logger.debug(f"Путь к файлу БД агента: {path}")
        # Создаем соединение с SQLite
        db_path = os.path.join(path, f'agent_data_{name}.sqlite')

        # Подключаемся к базе данных (если не существует, создастся автоматически)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Удаляем таблицы, если они уже существуют (чтобы избежать ошибок при повторном выполнении)
        cursor.execute(f"DROP TABLE IF EXISTS '{name}';")
        cursor.execute(f"DROP TABLE IF EXISTS 'trade{name}';")
        cursor.execute(f"DROP TABLE IF EXISTS results;")

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
                identifier INTEGER,
                time INTEGER,
                price FLOAT,
                quantity FLOAT,
                side TEXT
            );
        """)
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
                        sell_avg_trade_duration FLOAT
            );
        """)

        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.critical(f"Ошибка создания таблиц и БД (table_for_agent.py:7): {e}")
        return False

def drop(name, path):
    """
        Удаление sqlite файла агента

        :name - имя агента
    """
    # try:
    db_path = os.path.join(path, f'agent_data_{name}.sqlite')
    # Проверяем, существует ли файл перед удалением
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.debug(f"Файл {db_path} успешно удален.")
        return True
    else:
        logger.debug(f"Файл {db_path} не найден.")
        return False
    # except Exception as e:
    #     logger.critical(f"Ошибка удаления БД (table_for_agent.py:117): {e}")
    #     return False

# Для графика
def get_data_main_table(name):
    """
        Получает все данные из таблицы агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT time, open, high, low, close FROM '{name}';")
    result = cursor.fetchall()

    conn.close()
    return result

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

def get_list_indicator_table(name):
    """
        Получает все данные из таблицы агента

        :name - имя агента
    """
    logger.debug(f"Запрос списка таблиц кроме основных у агента {name}.")
    # Подключаемся к базе данных
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    result = []
    keep_tables = [f'{name}', f'trade{name}', 'results']
    # Итерируем по таблицам
    for table in tables:
        table_name = table[0]
        if table_name not in keep_tables:
            result.append(table_name)
            

    # Сохраняем изменения и закрываем соединение
    conn.close()
    return result

def get_data_indicator_table(name, table):
    """
        Получает все данные из таблицы торговли агента

        :name - имя агента
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT period, time, value FROM '{table}';")
    result = cursor.fetchall()

    conn.close()
    return result


