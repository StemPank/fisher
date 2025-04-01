import os, sys, importlib
from datetime import datetime, date
from core.binance.spot import klines
from core.bybit.v5 import Market
import core.agent.table_for_agent as table_for_agent

from utils.logging import logger_agent


def split_range(start, end, interval, limit=1000):
    """
        Разбивает временной промежуток на равные части по 1000 через оптеделенный интервал

        :start - от какой даты в мс
        :end - до какого времени в мс
        :interval - промежуток в мс 
        :limit=1000 - лимит значений в промежутке, опционально может быть задана если биржа имеет другой лимит ответа API
    """
    parts = []
    current_start = start
    
    while current_start < end:
        current_end = min(current_start + interval * (limit), end)
        parts.append((current_start, current_end))
        current_start = current_end  # Начало следующего интервала
    
    return parts

def time_to_ms_binance(time_str):
    """
        Переводит интервал из текста в кол-во мс

        :time_str - строка: "1s", "1m"...
    """
    units = {"s": 1000, "m": 60000, "h": 3600000, "d": 86400000, "W": 604800000, "M": 2592000000}  # Минуты и часы в мс
    value, unit = int(time_str[:-1]), time_str[-1]  # Разделяем число и единицу измерения
    return value * units.get(unit, 0)  # Возвращаем значение в мс


def time_to_bybit(time_str):
    """
        Переводит интервал из текста в минуты

        :time_str - строка: "1s", "1m"...
    """
    units = {"1": 1, "3": 3, "5": 5, "15": 15, "30": 30, "60": 60, "120": 120, "240": 240, "360": 360, "720": 720, "D": "D", "W": "W", "M": "M"}
    unit = time_str
    return units.get(unit, 0)  # Возвращаем значение

def time_to_ms_bybit(time_str):
    """
        Переводит интервал из текста в кол-во мс

        :time_str - строка: "1s", "1m"...
    """
    units = {"1": 60000, "3": 180000, "5": 300000, "15": 900000, "30": 1800000, "60": 3600000, "120": 7200000, "240": 14400000, "360": 21600000, "720": 43200000, "D": 86400000, "W": 604800000, "M": 2592000000}  # Минуты и часы в мс
    unit = time_str
    return units.get(unit, 0)  # Возвращаем значение в мс

def clearT(name, table_for_agents):
    """Удаляет данные из основной таблицы"""
    table_for_agents.clear_table()
    table_for_agents.delete_unwanted_tables()


def filter_unique_and_second_occurrences(data):
    """
        Фильтр, оставляет кортежи с уникальным значением времени в списке и фторое вхождение повторов

        :data - список кортежей
    """
    seen = set()
    unique_prices = []

    for row in data:
        key = row[3]  # 3-й элемент кортежа (индекс 2)

        if key not in seen:  # Добавляем только первое вхождение
            unique_prices.append(row)
            seen.add(key)

    return unique_prices


class HistoricalData():
    def __init__(self, agent_name, setting_data, symbol, interval, backtest=None, table_for_agents=None):
        # С версии 0.0.1 не нужна ↓
        self.list_inter_binance = ["1s", "1m", "5m", "15m", "1h", "2h", "1d", "1W", "1M"] # Список разрешенных интервалов
        self.list_inter_bybit = ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"] # Список разрешенных интервалов

        self.setting_data = setting_data # Полечаем настройки агента по его имени
        self.symbol = symbol
        self.interval = interval
        self.backtest = backtest
        self.result = None  # Переменная для хранения результата
        self.setting_data_sub = setting_data["sub_option"] # Под опция, содержит значение конечной точки для биржи
        self.table_for_agent = table_for_agents


        # С версии 0.0.1 не нужна ↓
        if self.symbol == None:
            logger_agent.info(f"В агенте {agent_name}, название монеты не задано")
            self.result = False
            return 
        
        """
            hasattr(self, name): проверяет, есть ли у объекта метод с именем name.
            callable(getattr(self, name)): проверяет, является ли он вызываемым (т.е. функцией).
            getattr(self, name)(): если метод найден, он вызывается.
        """
        if hasattr(self, self.setting_data["exchange"]) and callable(getattr(self, self.setting_data["exchange"])):
            #              Вызываем метор с именем ↓,   передаем аргументы ↓
            self.result = getattr(self, self.setting_data["exchange"])(agent_name, self.setting_data["start_date"], self.setting_data["end_date"], self.setting_data["current_date_enabled"]) 
        else:
            exchange = self.setting_data["exchange"]
            logger_agent.info(f"Метод '{exchange}' не найден.")
            self.result = False

    def run(self):
        """Возвращает результат выполнения загрузки исторических данных."""
        return self.result

    def binance(self, agent_name, start_date, end_date=None, current_date_enabled=None):
        """
            Загружает исторические данные с биржи binance 
        """
        # С версии 0.0.1 не нужна ↓
        if self.interval not in self.list_inter_binance:
            logger_agent.info(f"Интерал введен не коректно, попробуйте использовать символы (1s, m, h, 1d, 1W, 1M)")
            return False

        # Устанавливаем параметры
        SYMBOL = self.symbol
        INTEVAL = self.interval
        START = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        if self.backtest == False or current_date_enabled == True:
            END = int(datetime.now().replace(microsecond=0).timestamp() * 1000)
        else:
            END = int(datetime.combine(end_date, datetime.min.time()).timestamp() * 1000)
        
        # Проверка коректоного времени
        if START>END:
            logger_agent.info(f"Проверьте заданное время: начальное время превышает конечное")
            return False

        first = self.table_for_agent.get_first_row() # Получает первую строку из таблицы агента. first[3] - время 
        last = self.table_for_agent.get_last_row() # Получает последнюю строку из таблицы агента. last[3] -
        
        logger_agent.debug(f"start {START}, end {END}, Первая строка: {first}, Последняя строка: {last}")

        if self.setting_data_sub == "test":
            self.setting_data_sub = "https://testnet.binance.vision"
        if self.setting_data_sub != "test":
            self.setting_data_sub = self.setting_data_sub

        """Проверяем если разница времени начала загруженых исторических данных не отличается больше чем на интервал в настройках и БД и интервал не изменился, 
        проверяем разницу времени конца загруженных данных отличается от настроек меньше чем на интервал то ничего не делаем, если больше то меняем START для подгрузки свежих данных 
        или стипраем все данные и записываем заново"""
        if first != None:
            if abs(START - first[0]) <= time_to_ms_binance(INTEVAL):
                if END - last[0] < time_to_ms_binance(INTEVAL):
                    return True
                else:
                    START = last[0]+time_to_ms_binance(INTEVAL)
            else:
                clearT(agent_name, self.table_for_agent)
        else:
            clearT(agent_name, self.table_for_agent)

        # Промежуток от начала до конца делим на части т.к. API биржи не дает больже 1000 значений
        try:
            for interval in split_range(START, END, time_to_ms_binance(INTEVAL)):
                kline = klines(self.setting_data_sub, SYMBOL, INTEVAL, limit=1000, startTime=int(interval[0]), endTime=int(interval[1]))
                data = []
                for k in kline:
                    # Собераем порцию данных в список кортежей
                    data.append((k[0], float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])))
                data = filter_unique_and_second_occurrences(data)
                self.table_for_agent.insert_data(data) # Запись данных в таблицу
            return True
        except Exception as e:
            logger_agent.warning(f"Ошибка загрузки исторических данных {e}")

    def bybit(self, agent_name, start_date, end_date=None, current_date_enabled=None):
        """
            Загружает исторические данные с биржи bybit 
        """  
        # С версии 0.0.1 не нужна ↓
        if self.interval not in self.list_inter_bybit:
            logger_agent.info(f"Интерал введен не коректно, Доступные интервалы: 1 3 5 15 30 60 120 240 360 720 (мин) D (день) W (неделя) M (месяц) указать строкой")
            return False

        # Устанавливаем параметры
        SYMBOL = self.symbol
        INTEVAL = time_to_ms_bybit(self.interval)
        INTEVAL_GET = time_to_bybit(self.interval)
        START = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        if self.backtest == False or current_date_enabled == True:
            END = int(datetime.now().replace(microsecond=0).timestamp() * 1000)
        else:
            END = int(datetime.combine(end_date, datetime.min.time()).timestamp() * 1000)
        
        if START>END:
            logger_agent.info(f"Проверьте заданное время: начальное время превышает конечное")
            return False
        
        first = self.table_for_agent.get_first_row()
        last = self.table_for_agent.get_last_row()
        
        # Для отладки
        logger_agent.debug(f"start {START}, end {END}, Первая строка: {first}, Последняя строка: {last}")
        
        if self.setting_data_sub == "test":
            self.setting_data_sub = True
        if self.setting_data_sub != "test":
            self.setting_data_sub = False

        """Проверяем если разница времени начала загруженых исторических данных не отличается больше чем на интервал в настройках и БД и интервал не изменился, 
        проверяем разницу времени конца загруженных данных отличается от настроек меньше чем на интервал то ничего не делаем, если  больше то меняем START для подгрузки свежих данных 
        или стипраем все данные и записываем заново"""
        if first != None:
            if abs(START - first[0]) <= INTEVAL:
                if END - last[0] < INTEVAL:
                    return True
                else:
                    START = last[0] + INTEVAL
            else:
                clearT(agent_name, self.table_for_agent)
        else:
            clearT(agent_name, self.table_for_agent)

        # Промежуток от начала до конца делим на части т.к. API биржи не дает больже 1000 значений
        try:
            for interval in split_range(START, END, time_to_ms_bybit(self.interval)):
                kline = Market(testnet=self.setting_data_sub).klines(SYMBOL, INTEVAL_GET, limit=1000, start=int(interval[0]), end=int(interval[1]))
                data = []
                for k in kline:
                    # Собераем порцию данных в список кортежей
                    data.append((int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])))
                data = filter_unique_and_second_occurrences(data)
                self.table_for_agent.insert_data(data[::-1]) # Запись данных в таблицу
            return True
        except Exception as e:
            logger_agent.warning(f"Ошибка загрузки исторических данных {e}")