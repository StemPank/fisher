import os, sys, importlib
import random
import time

import global_variable, paths

import core.agent.install.bind_agents as bind_agents
import core.agent.install.agent_indicators as agent_indicators
from utils.logging import logger_agent

class Agent():
    def __init__(self, symbol, intervall, commission, variable_data, name, exchange, queue, path, optimization=None):
        
        self.COIN = str(symbol)
        self.INTEVAL = str(intervall)
        self.COMMISSION = float(commission)

        self.VARIABLE_DATA = variable_data

        print("Переменные на момент запуска", self.VARIABLE_DATA)

        self.variables = {}
        if optimization==None or optimization==False:
            for name_variable, value in variable_data:
                num_value = int(value)
                setattr(self, name_variable, num_value)
                self.variables[name_variable] = num_value  # Сохраняем в словаре
            
            self.max_tuple = max(self.variables.values())
        else:
            for name_variable, value in variable_data:
                setattr(self, name_variable, value)
                self.variables[name_variable] = value  # Сохраняем в словаре
        
        if optimization==None:
            self.agent(name, exchange, queue, path)
        elif optimization == False:
            self.agent(name, exchange, queue, path, True)
        elif optimization == True:
            self.iteration_count = 0
            self.start_optimization = self.run_dynamic_loops(list(self.variables.keys()), name, exchange, queue, path) 
        else:
            print("Проверь данные")


    def agent(self, agent_name, exchange, queue, path, backtest=None, optimization=None, iteration_value=1):
        """Функция агента, обрабатывающего данные."""
        
        activate = False
        reconnect_timeout=0

        if optimization:
            # self.VARIABLE_DATA = [(name, self.variables[name]) for name in self.variables]
            # self.variables = {}
            # for name_variable, value in self.VARIABLE_DATA:
            #     # num_value = int(value)
            #     setattr(self, name_variable, value[0])
            #     self.variables[name_variable] = value  # Сохраняем в словаре

            self.variable_data_for_start = [(name, self.variables[name][0]) for name in self.variables]
            self.variables_for_start = {}
            for name_variable, value in self.variable_data_for_start:
                num_value = int(value)
                setattr(self, name_variable, num_value)
                self.variables_for_start[name_variable] = num_value  # Сохраняем в словаре
            self.max_tuple = max(self.variables_for_start.values())
            print("Переменные на текущую итерацию", self.variable_data_for_start)
        else:
            self.variable_data_for_start = self.VARIABLE_DATA

        contact_agent = bind_agents.ContactAgent(agent_name, exchange, queue, backtest, optimization, self.VARIABLE_DATA)
        contact_indicators = agent_indicators.AgentIndicator(agent_name, exchange, queue, backtest)

        module_name = f"run_{agent_name}"
        module_dir = os.path.join(global_variable.setting_file("folder_path"), agent_name)
        sys.path.append(module_dir)
        if module_name in sys.modules: # Удаляем модуль из кэша перед импортом (перезагрузка), Это заставляет Python заново загрузить код при новом запуске.
            del sys.modules[module_name]
        module = importlib.import_module(module_name)

        logger_agent.info(f"Выбраная пара {self.COIN} и интервал {self.INTEVAL}")
        contact_agent.clear_order_table()
        api_key, api_secret = contact_agent.key_proviger()
        data = []

        while True:

            if activate==False and bind_agents.check_internet():
                historical_data = contact_agent.historical_data(self.COIN, self.INTEVAL, backtest)
                if historical_data and backtest == None:
                    activate = contact_agent.stream_kline_data(self.COIN, self.INTEVAL, queue)
                elif historical_data and backtest != None:
                    activate = True
                    logger_agent.debug("Агент запущен в режиме backtest, activate=True")
                data = contact_agent.get_data()
                reconnect_timeout=0
                logger_agent.info(f"Полученые данные {data[0]} {data[1]} ... {data[-1]}")
            
            elif backtest != None and bind_agents.check_internet() == False:
                logger_agent.debug("Агент запущен в режиме backtest, без сети")
                data = contact_agent.get_data()
                # if data == []:
                #     logger_agent.warning("Список данных пустой")

            elif reconnect_timeout == 20 and bind_agents.check_internet() == False:
                activate = False
                reconnect_timeout=0
                logger_agent.warning(f"Нет подключения к сети, возможно подключен VPN")
                time.sleep(10)
            
            if backtest != None or not queue.empty(): 
                reconnect_timeout=0
                try:
                    msg = queue.get(timeout=2)
                except:
                    msg = None
                if msg == "STOP":
                    if backtest == None:
                        contact_agent.stop_agent()
                    logger_agent.info(f"Агент {agent_name} завершает работу.")
                    break  # Выходим из цикла и процесс завершается

                if backtest != None or msg['confirm'] == True:
                    try:
                        if activate and backtest == None and data[-1][3] == msg["start"]:
                            data[-1] = (int(msg["start"]), float(msg["open"]), float(msg["high"]), float(msg["low"]), float(msg["close"]), float(msg["volume"]))
                        elif activate and backtest == None and data[-1][3] != msg["start"]:
                            data.append((int(msg["start"]), float(msg["open"]), float(msg["high"]), float(msg["low"]), float(msg["close"]), float(msg["volume"])))
                    except Exception as e:
                        logger_agent.info(f"Ошибка, попробуйте выключить VPN: {e}")
                        logger_agent.info(f"Агент {agent_name} завершает работу.")
                        break
                    
                    if data != []:

                        connect = module.Agent(self.COIN, self.INTEVAL, self.COMMISSION, self.variable_data_for_start, iteration_value, data, contact_agent, contact_indicators)
                        if backtest != None:
                            for i, row in enumerate(data):
                                if i > self.max_tuple:
                                    connect.script(i)
                        else:
                            connect.script(len(data))
                        
                if backtest != None:
                    if data == []:
                        logger_agent.warning("Список данных пустой, возможно нет подключения к сети или подключен VPN")
                    elif len(data) < self.max_tuple:
                        logger_agent.warning("Список данных слишком мал")
                    queue.put("STOP")
                else:
                    print(msg)

            # Если данных нет 60 секунд переподключение
            else:
                # if activate == True:
                reconnect_timeout += 1
                if reconnect_timeout > 60:
                    logger_agent.info("Данные нет слишком долго")
                    activate = False
                time.sleep(1)

    def run_dynamic_loops(self, keys, name, exchange, queue, path, current_index=0, current_values=None): # (self, keys, name, exchange, queue, path, current_index=0, current_values=None)
        if current_values is None:
            current_values = []

        if current_index == len(keys):
            self.iteration_count += 1
            self.update_variables(keys, current_values)  # Обновляем переменные

            print(f"Итерация {self.iteration_count}, Текущие переменные: {self.variables}")

            # Перед запуском агента, обновим self.VARIABLE_DATA из self.variables
            self.VARIABLE_DATA = [(key, self.variables[key][0]) for key in keys]
            
            start_time = time.time()
            self.agent(name, exchange, queue, path, True, True, self.iteration_count)
            logger_agent.info(f"Итерация {self.iteration_count} завершена за {(time.time() - start_time):.3f} секунд")
            return
        
        key = keys[current_index]
        _, min_val, max_val, step = self.variables[key]

        for value in range(min_val, max_val + 1, step):
            # Запускаем следующую итерацию
            self.run_dynamic_loops(keys, name, exchange, queue, path, current_index + 1, current_values + [value])

    def update_variables(self, keys, values):
        """Обновляет переменные в __dict__."""
        for key, value in zip(keys, values):
            if isinstance(self.variables[key], tuple):
                min_val, max_val, step = self.variables[key][1:]  # Берем min, max, step
                self.variables[key] = (value, min_val, max_val, step)
            else:
                raise ValueError(f"Ошибка: self.variables['{key}'] стало int: {self.variables[key]}")