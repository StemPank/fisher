import time
import socket
import global_variable
from core.agent.historical_data import HistoricalData
import core.agent.stream_kline as stream_kline

import core.agent.table_for_agent as table_for_agent
import core.agent.result_of_work as result_of_work

from utils.logging import logger_agent

def logger(key, text):
    """
        Логирование дуйствий агента, debug-пишется только в логи, остальное и в консоль и в логи

        Аргументы:
            :key (str) - ключ сообщения "debug", "info", "warning", "critical"
            :text (str) - текст сообщения
    """
    if key=="debug":
        logger_agent.debug(text)
    elif key=="info":
        logger_agent.info(text)
    elif key=="warning":
        logger_agent.warning(text)
    elif key=="critical":
        logger_agent.critical(text)

def check_internet(host="8.8.8.8", port=53, timeout=3):
    """
        Проверка доступа к интернету

        return (bool) 
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, port))
        return True
    except socket.error:
        return False

def key_proviger(agent_name):
    """
        Передает ключи для поставщика

        :agent_name (str) - Имя агента
        
        :return api_key, api_secret
    """
    setting_data = global_variable.setting_agent_file(agent_name)
    _, _, api_key, api_secret=global_variable.registered_data_providers(setting_data['exchange'])
    return api_key, api_secret

# Данные с поставщика
def historical_data(agent_name, coin, interval, backtest):
    """
        Запрашивает и записывает в БД исторические данные

        :agent_name (str) - Имя агента
        :coin (str) - Название валютной пары
        :interval - 
        :backtest (bool) - Флаг бэктеста
    """
    try:
        setting_data = global_variable.setting_agent_file(agent_name) # Полечаем настройки агента по его имени
        _, exc, _, _=global_variable.registered_data_providers(setting_data['exchange']) # Полечаем поставщика по его добавленному имени
        setting_data['exchange'] = exc
        load_his = HistoricalData(agent_name, setting_data, coin, interval, backtest)
        result = load_his.run()
        return result
    except Exception as e:
        logger_agent.warning(f"Ошибка получения исторических данных агента {agent_name} к API: {e}")
        return False

def get_data(agent_name):
    """
        Получает список кортежей данных валютной пары из БД

        :agent_name (str) - Имя агента
    """
    result = table_for_agent.get_data_main_table(agent_name)
    return result

def stream_kline_data(agent_name, coin, interval, queue):
    """
        Подключается к Вебсокету и передает данные в очередь, на закрытой свече добавляет данные к БД
        
        :agent_name (str) - Имя агента
        :coin (str) - Название валютной пары
        :interval - Интервал
        :queue (multiprocessing.Queue) - очередь мультипроцесса
    """
    try:
        setting_data = global_variable.setting_agent_file(agent_name) # Полечаем настройки агента по его имени
        _, exc, _, _=global_variable.registered_data_providers(setting_data['exchange']) # Полечаем поставщика по его добавленному имени
        setting_data['exchange'] = exc
        stream_kline.StreamKline(agent_name, setting_data["exchange"], setting_data["sub_option"], "start", coin, interval, queue)
        return True
    except Exception as e:
        logger_agent.warning(f"Ошибка подключения к потоку данных данных агента {agent_name} к API: {e}")
        return False

def stop_agent(agent_name):
    """
        Остановка Вебсокета

        :agent_name (str) - Имя агента
    """
    setting_data = global_variable.setting_agent_file(agent_name) # Полечаем настройки агента по его имени
    _, exc, _, _=global_variable.registered_data_providers(setting_data['exchange']) # Полечаем поставщика по его добавленному имени
    setting_data['exchange'] = exc
    stream_kline.StreamKline(agent_name, setting_data["exchange"], setting_data["sub_option"], "stop")

# Ордера
def new_order(agent_name, symbol, index_order, api_key, api_secret, time, price, side, type, quantity, commission, iteration_value, inform_bot=None):
    """
    Открывает новую позицию
    """
    logger_agent.debug(f"Запрос на публикацию нового ордера из агента {agent_name}")
    data = []
    # Информировать сообщением в боте, опционально даждаться подтверждения
    if inform_bot:
        inform = True
    else:
        inform = True

    # Запрос на новый ордер, опционально получить подтверждение
    if inform:
        order = True
    else:
        order = False

    # Записть в БД (index, time, price, side)
    if inform and order:
        data.append((index_order, time, price, quantity, side))
        record = table_for_agent.insert_data_order(agent_name, data)
        if record:
            logger_agent.debug(f"Нового ордер успешно опубликовон из агента {agent_name}")
        else:
            logger_agent.warning(f"Нового ордер успешно опубликовон, но запись не прошла из агента {agent_name}")
            # Создаем файл для испрвдления мелкой ошибки
            text = f"""
            import core.agent.table_for_agent as table_for_agent
            data[0] = {(index_order, time, price, quantity, side)}
            record = table_for_agent.insert_data_order(data)
            """
            global_variable.record_warn("insert_data_order", text)
            
    else:
        logger_agent.debug(f"Запрос на публикацию нового ордера отменен из агента {agent_name}")

    # Расчет результатов
    # table_for_agent.create_a_results_table_if_it_does_not_exist(agent_name)
    result_of_work.calculation_of_results(agent_name, iteration_value, commission)

def clear_order_table(agent_name):
    """
        Удалить данные о сделках (при новом запуске агента)
    
        :agent_name (str) - Имя агента
    """
    table_for_agent.clear_data_order_table(agent_name)




