
import global_variable
from historical_data import HistoricalData
import stream_kline

import core.table_for_agent as table_for_agent

# _, exc, _, _=global_variable.registered_data_providers()


def run_agent(agent_name, coin, interval, queue, backtest):
    setting_data = global_variable.setting_agent_file(agent_name) # Полечаем настройки агента по его имени
    _, exc, _, _=global_variable.registered_data_providers(setting_data['exchange']) # Полечаем поставщика по его добавленному имени
    setting_data['exchange'] = exc
    # print(setting_data)

    load_his = HistoricalData(agent_name, setting_data, coin, interval, backtest)
    result = load_his.run()
    if result==True and backtest==False:
        print("\nЗагрузка исторических данных прошла усрешно")
        stream_kline.StreamKline(agent_name, setting_data["exchange"], "start", coin, interval, queue)
    else:
        print("\nЗагрузка исторических данных не завершилась")

def stop_agent(agent_name):
    setting_data = global_variable.setting_agent_file(agent_name) # Полечаем настройки агента по его имени
    _, exc, _, _=global_variable.registered_data_providers(setting_data['exchange']) # Полечаем поставщика по его добавленному имени
    setting_data['exchange'] = exc
    stream_kline.StreamKline(agent_name, setting_data["exchange"], "stop")

def get_data(agent_name):
    print(table_for_agent.get_all_data(agent_name))
