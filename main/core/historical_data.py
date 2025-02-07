import os, sys, importlib
from datetime import datetime, date
from core.binance.spot import klines
from core.bybit.v5 import Market
import core.table_for_agent as table_for_agent


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

def clearT(name):
    """Удаляет данные из основной таблицы"""
    table_for_agent.clear_table(name)



class HistoricalData():
    def __init__(self, agent_name, setting_data, coin, interval, backtest):
        self.list_inter_binance = ["1s", "1m", "5m", "15m", "1h", "2h", "1d", "1W", "1M"] # Список разрешенных интервалов
        self.list_inter_bybit = ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"] # Список разрешенных интервалов
        self.setting_data = setting_data # Полечаем настройки агента по его имени
        self.coin = coin
        self.interval = interval
        self.backtest = backtest
        self.result = None  # Переменная для хранения результата

        # Проверяем корректность
        if self.coin == None:
            print(f"В агенте {agent_name}, название монеты не задано")
            return False
        
        """
            hasattr(self, name): проверяет, есть ли у объекта метод с именем name.
            callable(getattr(self, name)): проверяет, является ли он вызываемым (т.е. функцией).
            getattr(self, name)(): если метод найден, он вызывается.
        """
        if hasattr(self, self.setting_data["exchange"]) and callable(getattr(self, self.setting_data["exchange"])):
            #              Вызываем метор с именем ↓,   передаем аргументы ↓
            self.result = getattr(self, self.setting_data["exchange"])(agent_name, self.setting_data["start_date"], self.setting_data["end_date"], self.setting_data["current_date_enabled"]) 
        else:
            print(f"Метод '{self.setting_data["exchange"]}' не найден.")
            self.result = False

    def run(self):
        """Возвращает результат выполнения загрузки исторических данных."""
        return self.result

    def binance(self, agent_name, start_date, end_date=None, current_date_enabled=None):
        """
            Загружает исторические данные с биржи binance 
        """
        
        if self.interval not in self.list_inter_binance:
            print(f"Интерал введен не коректно, попробуйте использовать символы (1s, m, h, 1d, 1W, 1M)")
            return False

        # Устанавливаем параметры
        COIN = self.coin
        INTEVAL = self.interval
        START = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        if self.backtest == False or current_date_enabled == True:
            END = int(datetime.now().replace(microsecond=0).timestamp() * 1000)
        else:
            END = int(datetime.combine(end_date, datetime.min.time()).timestamp() * 1000)
        
        first = table_for_agent.get_first_row(agent_name) # Получает первую строку из таблицы агента. first[3] - время 
        last = table_for_agent.get_last_row(agent_name) # Получает последнюю строку из таблицы агента. last[3] -
        
        # print(f"start {START}")
        # print(f"end {END}")
        # print("Первая строка:", first[3])
        # print("Последняя строка:", last[3])
        # print(time_to_ms("1d"))
        # print("Интервал:", first[2])

        """Проверяем если разница времени начала загруженых исторических данных не отличается больше чем на интервал в настройках и БД и интервал не изменился, 
        проверяем разницу времени конца загруженных данных отличается от настроек меньше чем на интервал то ничего не делаем, если  больше то меняем START для подгрузки свежих данных 
        или стипраем все данные и записываем заново"""
        if first != None:
            if abs(START - first[3]) <= time_to_ms_binance(INTEVAL) and first[2] == INTEVAL:
                if END - last[3] < time_to_ms_binance(INTEVAL):
                    return True
                else:
                    START = last[3]+time_to_ms_binance(INTEVAL)
            else:
                clearT(agent_name)
        else:
            clearT(agent_name)

        # Промежуток от начала до конца делим на части т.к. API биржи не дает больже 1000 значений
        try:
            for interval in split_range(START, END, time_to_ms_binance(INTEVAL)):
                # print(f"start {interval[0]}")
                # print(f"end {interval[1]}")
                kline = klines(COIN, INTEVAL, limit=1000, startTime=int(interval[0]), endTime=int(interval[1]))
                print("\rЗагружаем данные |", end='', flush=True) # Имитация загрузки
                data = []
                for k in kline:
                    # Собераем порцию данных в список кортежей
                    data.append((self.setting_data["exchange"], COIN, INTEVAL, k[0], float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])))
                print("\rЗагружаем данные /", end='', flush=True) # Имитация загрузки
                table_for_agent.insert_data(agent_name, data) # Запись данных в таблицу
            print("\rЗагружаем данные OK", end='', flush=True) # Имитация загрузки
            return True
        except:
            print("Ошибка")

    def bybit(self, agent_name, start_date, end_date=None, current_date_enabled=None):
        """
            Загружает исторические данные с биржи bybit 
        """  

        if self.interval not in self.list_inter_bybit:
            print(f"Интерал введен не коректно, Доступные интервалы: 1 3 5 15 30 60 120 240 360 720 (мин) D (день) W (неделя) M (месяц) указать строкой")
            return False

        # Устанавливаем параметры
        COIN = self.coin
        INTEVAL = time_to_ms_bybit(self.interval)
        INTEVAL_GET = time_to_bybit(self.interval)
        START = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        if self.backtest == False or current_date_enabled == True:
            END = int(datetime.now().replace(microsecond=0).timestamp() * 1000)
        else:
            END = int(datetime.combine(end_date, datetime.min.time()).timestamp() * 1000)
        
        first = table_for_agent.get_first_row(agent_name)
        last = table_for_agent.get_last_row(agent_name)
        
        # Для отладки
        # print(f"start {START}")
        # print(f"end {END}")
        # print("Первая строка:", first)
        # print("Последняя строка:", last[3])
        # print(time_to_ms("1d"))
        # print("Интервал:", first[2])
        
        """Проверяем если разница времени начала загруженых исторических данных не отличается больше чем на интервал в настройках и БД и интервал не изменился, 
        проверяем разницу времени конца загруженных данных отличается от настроек меньше чем на интервал то ничего не делаем, если  больше то меняем START для подгрузки свежих данных 
        или стипраем все данные и записываем заново"""
        if first != None:
            if abs(START - first[3]) <= INTEVAL and first[2] == self.interval:
                if END - last[3] < INTEVAL:
                    return True
                else:
                    START = last[3] + INTEVAL
            else:
                clearT(agent_name)
        else:
            clearT(agent_name)

        # Промежуток от начала до конца делим на части т.к. API биржи не дает больже 1000 значений
        try:
            for interval in split_range(START, END, time_to_ms_bybit(self.interval)):
                kline = Market().klines(COIN, INTEVAL_GET, limit=1000, start=int(interval[0]), end=int(interval[1]))
                print("\rЗагружаем данные |", end='', flush=True) # Имитация загрузки
                data = []
                for k in kline:
                    # Собераем порцию данных в список кортежей
                    data.append((self.setting_data["exchange"], COIN, self.interval, int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])))
                # print(data[::-1])
                print("\rЗагружаем данные /", end='', flush=True) # Имитация загрузки
                table_for_agent.insert_data(agent_name, data[::-1]) # Запись данных в таблицу
            print("\rЗагружаем данные OK \n", end='', flush=True) # Имитация загрузки
            return True
        except:
            print("\n Ошибка")