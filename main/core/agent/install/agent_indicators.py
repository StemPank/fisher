import global_variable
import sqlite3, os
import core.agent.table_for_agent as table_for_agent
from utils.logging import logger_agent

class AgentIndicator():
    def __init__(self, agent_name, exchange, queue, backtest):
        """
            Инициализация, связь с индикаторами

            Аргументы:
                :agent_name - имя агента
                :exchange - имя биржи
                :queue - очедедь данных
        """
        self.setting_data = global_variable.setting_agent_file(agent_name) # Полечаем настройки агента по его имени
        self.setting_data['exchange'] = exchange
        self.agent_name = agent_name
        self.queue = queue

        self.table_for_agent = table_for_agent.TableForIndicator(agent_name)

    def sma(self, index_indicator, prices, period):
        """
            Вычисляет простую скользящую среднюю (SMA).
            
            Аргументы:
                :index_indicator (str) - Индекс индикаторов, для разделения индикаторов и одинаковым именем
                :prices (list) - список кортежей, где цена закрытия находится на 8 месте (индекс 7)
                :period (int) или (tipe(кортеж)) - период SMA, число или специальная переменная (кортеж) где берется первое значение
                return: список значений SMA (начиная с позиции, где хватает данных)
        """
        logger_agent.debug(f"Запроос на вычесление индикатора SMA с индексом {index_indicator}")

        # Если period - кортеж, берем первое значение
        if isinstance(period, tuple):
            period = int(period[0])
        else:
            period = int(period)
        
        # Проверка на валидность периода
        if not isinstance(period, (int, float))or period <= 0:
            logger_agent.warning("Период SMA должен быть положительным целым числом")
            return

        if len(prices) < period:
            logger_agent.info(f"SMA: Список переданных значений меньше периода вычесления")
            return []  # Если данных меньше, чем период, возвращаем пустой список

        sma_values = []
        
        db_entry = self.table_for_agent.creating_an_indicator_table("SMA", index_indicator)
        if db_entry:
            logger_agent.debug(f"SMA время начала расчета {db_entry[0][1]}, начальное время полученных данных + период = {prices[0+period-1][0]}")
            if db_entry[0][1] != prices[0+period-1][0]:
                self.table_for_agent.clear_table_indicator("SMA", index_indicator)
                db_entry = None
        last_db_time = db_entry[-1][1] if db_entry else None
            
        # Определяем, с какого момента начинать расчет
        start_index = 0
        if last_db_time:
            for i, row in enumerate(prices):
                if row[0] == last_db_time:  # Индекс 3 — это time в кортежах
                    start_index = i + 1  # Начинаем после найденного момента
                    break
        if start_index == 0:
            start_index = period
        else:
            start_index = start_index

        # Если start_index указывает за пределы списка, ничего не делаем
        if start_index >= len(prices):
            sma_values = db_entry
            return sma_values

        # Вычисляем SMA по формуле
        for i in range(start_index, len(prices) + 1):
            sum_prices = sum(row[4] for row in prices[i - period:i])  # Берем закрытия из кортежей
            sma = sum_prices / period  # Среднее значение
            time = prices[i - 1][0]  # Время последней свечи в окне
            sma_values.append((period, int(time), float(sma)))  # Добавляем кортеж (time, SMA)
        if sma_values is not []:
            logger_agent.debug(f"Полученые данные SMA, для записи в БД {sma_values[0]} {sma_values[-1]}")
        else:    
            logger_agent.debug(f"Новых данных SMA нет")

        self.table_for_agent.insert_data_indicator("SMA", index_indicator, sma_values)
        db_entry = self.table_for_agent.creating_an_indicator_table("SMA", index_indicator) # для получения данных и передачи в ответ
        return db_entry