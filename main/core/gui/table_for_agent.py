import os
import global_variable
import sqlite3
import paths
from utils.logging import logger

class Main_database_for_gui():
    _instance = None  # Храним единственный экземпляр

    def __new__(cls):
        if cls._instance is None:
            logger.info("Создание соединения с основной БД")
            cls._instance = super().__new__(cls) # Создаём объект один раз
            db_path = os.path.join(f"{paths.MAIN_REPOSITORY}", f'fisher_data.sqlite')
            cls._instance.connection = sqlite3.connect(db_path) # Открываем одно соединение
            cls._instance.cursor = cls._instance.connection.cursor()
            cls._instance.connection.execute("PRAGMA foreign_keys = ON")  # Включаем поддержку внешних ключей

        return cls._instance  # Возвращаем тот же объект

    def create_table_list_agents(self):
        """Создаёт таблицу, если ее нет"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS list_agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                version FLOAT,
                reserv FLOAT,
            )
        ''')
         
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                setting_name TEXT NOT NULL,
                setting_value TEXT,
                FOREIGN KEY (agent_id) REFERENCES list_agents(id) ON DELETE CASCADE
            )
        ''')

        self.connection.commit()
        logger.info("Таблица 'Список агентов' (list_agents) создана")
    
    # Методы для агентов
    def add_agent(self, name, version, reserv=0):
        """Добавляет нового агента"""
        try:
            self.cursor.execute(
                "INSERT INTO list_agents (name, version, reserv) VALUES (?, ?, ?)",
                (name, version, reserv)
            )
            self.connection.commit()
            logger.info(f"Агент '{name}' добавлен.")
        except sqlite3.IntegrityError:
            logger.error(f"Агент с именем '{name}' уже существует!")

    def update_agent(self, name, version=None, reserv=None):
        """Обновляет информацию об агенте по имени"""
        query = "UPDATE list_agents SET "
        params = []
        
        if version is not None:
            query += "version = ?, "
            params.append(version)
        
        if reserv is not None:
            query += "reserv = ?, "
            params.append(reserv)

        query = query.rstrip(", ")  # Убираем лишнюю запятую
        query += " WHERE name = ?"
        params.append(name)

        self.cursor.execute(query, params)
        self.connection.commit()
        logger.info(f"Агент '{name}' обновлён.")

    def delete_agent(self, name):
        """Удаляет агента по имени"""
        self.cursor.execute("DELETE FROM list_agents WHERE name = ?", (name,))
        self.connection.commit()
        logger.info(f"Агент '{name}' удалён.")

    def get_agent_id(self, name):
        """Получает ID агента по имени"""
        self.cursor.execute("SELECT id FROM list_agents WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # Методы для настроек агента
    def add_agent_setting(self, agent_name, setting_name, setting_value):
        """Добавляет настройку для агента"""
        agent_id = self.get_agent_id(agent_name)
        if agent_id:
            self.cursor.execute(
                "INSERT INTO agent_settings (agent_id, setting_name, setting_value) VALUES (?, ?, ?)",
                (agent_id, setting_name, setting_value)
            )
            self.connection.commit()
            logger.info(f"Настройка '{setting_name}' добавлена для агента '{agent_name}'.")
        else:
            logger.error(f"Агент '{agent_name}' не найден!")

    def update_agent_setting(self, agent_name, setting_name, new_value):
        """Обновляет настройку агента"""
        agent_id = self.get_agent_id(agent_name)
        if agent_id:
            self.cursor.execute(
                "UPDATE agent_settings SET setting_value = ? WHERE agent_id = ? AND setting_name = ?",
                (new_value, agent_id, setting_name)
            )
            self.connection.commit()
            logger.info(f"Настройка '{setting_name}' обновлена для агента '{agent_name}'.")
        else:
            logger.error(f"Агент '{agent_name}' не найден!")

    def delete_agent_setting(self, agent_name, setting_name):
        """Удаляет настройку агента"""
        agent_id = self.get_agent_id(agent_name)
        if agent_id:
            self.cursor.execute(
                "DELETE FROM agent_settings WHERE agent_id = ? AND setting_name = ?",
                (agent_id, setting_name)
            )
            self.connection.commit()
            logger.info(f"Настройка '{setting_name}' удалена для агента '{agent_name}'.")
        else:
            logger.error(f"Агент '{agent_name}' не найден!")

    def get_agent_settings(self, agent_name):
        """Получает все настройки для агента"""
        agent_id = self.get_agent_id(agent_name)
        if agent_id:
            self.cursor.execute(
                "SELECT setting_name, setting_value FROM agent_settings WHERE agent_id = ?",
                (agent_id,)
            )
            return self.cursor.fetchall()
        else:
            logger.error(f"Агент '{agent_name}' не найден!")
            return []
        
    def close(self):
        """Закрывает соединение с базой данных"""
        self.connection.close()
        Main_database_for_gui._instance = None  # Позволяет создать новый экземпляр, если нужно

class Table_for_gui():
    def __init__(self, agent_name, path):
        """
            Инициализация управления таблицами из gui

            Аргументы:
                :agent_name - имя агента
        """
        self.db_path = os.path.join(f"{path}/{agent_name}", f'agent_data_{agent_name}.sqlite')
        self.agent_name = agent_name
        self.exchange = global_variable.registered_data_providers(global_variable.setting_agent_file(self.agent_name, "exchange"), True)

    def get_data_main_table(self):
        f"""
            Запрос данных таблицы '{self.agent_name}', параметры агента

            Результат: Список с одним кортежем [(market, name, interval, commission)]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT market, name, interval, commission FROM '{self.agent_name}' LIMIT 1")
        result = cursor.fetchall()

        conn.close()
        return result
    
    def record_data_main_table(self, symbol, interval, commission):
        f"""
            Запись в таблицу '{self.agent_name}', параметры агента

            Аргументы:
                :symbol - символ торговой пары
                :interval - интервал
                :commission - коммисия
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM '{self.agent_name}'")
        cursor.execute(f"DELETE FROM 'kline'")
        cursor.execute(f"DELETE FROM 'trade'")
        cursor.execute(f"DELETE FROM 'results'")
        cursor.executemany(f"""
            INSERT INTO {self.agent_name} (market, name, interval, commission)
            VALUES (?, ?, ?, ?);
        """, [(self.exchange, symbol, interval, commission)])
        
        conn.commit()
        conn.close()

    def get_all_variables(self):
        """
            Запрос данных таблицы 'variable', специальные переменные агента

            Результат: Список кортежей [(name, input), (name, input)]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT name, input FROM variable")
        result = cursor.fetchall()

        conn.close()
        return result
    
    def record_variable_data(self, variable_name, variable_value):
        """
            Запись в таблицу 'variable', специальные переменные агента

            Аргументы:
                :variable_name - имя переменной
                :variable_value - значение переменной
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.executemany(f"""
            INSERT INTO variable (name, input)
            VALUES (?, ?);
        """, [(variable_name, variable_value)])
        
        conn.commit()
        conn.close()

    def drop_variable_data(self):
        """
            Отчистка данных таблицы 'variable', специальные переменные агента
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM variable;")
        conn.commit()
        conn.close()



def create(name, path):
    """
        Создание sqlite файла для агента
        и необходимых таблиц

        Аргументы:
            :name - имя агента
    """
    try:
        # Создаем соединение с SQLite
        db_path = os.path.join(path, f'agent_data_{name}.sqlite')

        # Подключаемся к базе данных (если не существует, создастся автоматически)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Удаляем таблицы, если они уже существуют (чтобы избежать ошибок при повторном выполнении)
        cursor.execute(f"DROP TABLE IF EXISTS '{name}';")
        cursor.execute(f"DROP TABLE IF EXISTS 'variable';")
        cursor.execute(f"DROP TABLE IF EXISTS 'kline';")
        cursor.execute(f"DROP TABLE IF EXISTS 'trade';")
        cursor.execute(f"DROP TABLE IF EXISTS results;")
        cursor.execute(f"DROP TABLE IF EXISTS optimization;")

        # Создаем таблицу Searches
        cursor.execute(f"""
            CREATE TABLE '{name}' (
                market TEXT,
                name TEXT,
                interval TEXT,
                commission FLOAT
            );
        """)
        cursor.execute(f"""
            CREATE TABLE 'variable' (
                name TEXT,
                input FLOAT
            );
        """)
        cursor.execute(f"""
            CREATE TABLE 'kline' (
                time INTEGER,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume FLOAT
            );
        """)
        cursor.execute(f"""
            CREATE TABLE 'trade' (
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
        cursor.execute(f"""
            CREATE TABLE optimization (
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

    cursor.execute(f"SELECT time, open, high, low, close FROM 'kline';")
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

    cursor.execute(f"SELECT identifier, time, price, quantity, side FROM 'trade';")
    result = cursor.fetchall()

    conn.close()
    return result

def get_list_indicator_table(name):
    """
        Получает все названия таблиц агента кроме основных

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
    keep_tables = [f'{name}', 'variable', 'kline', 'trade', 'results', 'optimization']
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
        Получает все данные таблицы индикатора агента

        :name - имя агента
        :table - имя таблицы индикатора
    """
    db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), name), f'agent_data_{name}.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT period, time, value FROM '{table}';")
    result = cursor.fetchall()

    conn.close()
    return result


