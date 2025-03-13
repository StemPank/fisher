
import os, sys, importlib
import random
import time

class Agent():
    def __init__(self, optimization=None, name=None, queue=None, path=None):
        # Название монеты
        self.COIN = "BTCUSDT"
        # Интервал 
        self.INTEVAL = "1m"
        self.COMMISSION = 0.002

        self.variable_sma1 = (140, 145, 150, 1)
        self.variable_sma2 = (105, 95, 100, 1)
        # self.variable_sma3 = (10, 0, 10, 2)
        self.variables = {k: v for k, v in self.__dict__.items() if k.startswith("variable_")}  # Список переменных
        self.max_tuple = max({k: v for k, v in vars(self).items() if k.startswith("variable_") and isinstance(v, tuple)}.values(), key=lambda x: x[0])
        if optimization != None and name!=None and queue!=None and path!=None:
            self.iteration_count = 0
            self.start_optimization = self.run_dynamic_loops(list(self.variables.keys()), name, queue, path) 
        

    def agent(self, name, queue, path, backtest=None):
        """Функция агента, обрабатывающего данные."""
        activate = False
        reconnect_timeout=0
        data = []

        sys.path.append(path)
        module = importlib.import_module("bind_agents")
        indicators = importlib.import_module("agent_indicators")

        module.logger("info", f"Выбраная пара {self.COIN} и интервал {self.INTEVAL}")
        module.clear_order_table(name)
        api_key, api_secret = module.key_proviger(name)

        while True:

            if activate==False and module.check_internet():
                historical_data = module.historical_data(name, self.COIN, self.INTEVAL, backtest)
                if historical_data and backtest == None:
                    activate = module.stream_kline_data(name, self.COIN, self.INTEVAL, queue)
                elif historical_data and backtest != None:
                    activate = True
                    module.logger("debug", "Агент запущен в режиме backtest, activate=True")
                data = module.get_data(name)
                reconnect_timeout=0
                module.logger("info", f"Полученые данные {data[0]} {data[1]} ... {data[-1]}")
            if reconnect_timeout == 20 and module.check_internet() == False:
                activate = False
                reconnect_timeout=0
                module.logger("warning", f"Нет подключения к сети, возможно подключен VPN")
                time.sleep(10)
            
            if backtest != None or not queue.empty(): 
                reconnect_timeout=0
                try:
                    msg = queue.get(timeout=2)
                except:
                    msg = None
                if msg == "STOP":
                    if backtest == None:
                        module.stop_agent(name)
                    module.logger("info", f"Агент {name} завершает работу.")
                    break  # Выходим из цикла и процесс завершается

                if backtest != None or msg['x'] == 'true':
                    try:
                        if activate and backtest == None and data[-1][3] == msg["t"]:
                            data[-1] = ("binance", self.COIN, self.INTEVAL, int(msg["t"]), float(msg["o"]), float(msg["h"]), float(msg["l"]), float(msg["c"]), float(msg["v"]))
                        elif activate and backtest == None and data[-1][3] != msg["t"]:
                            data.append(("binance", self.COIN, self.INTEVAL, int(msg["t"]), float(msg["o"]), float(msg["h"]), float(msg["l"]), float(msg["c"]), float(msg["v"])))
                    except Exception as e:
                        module.logger("info", f"Ошибка, попробуйте выключить VPN: {e}")
                        module.logger("info", f"Агент {name} завершает работу.")
                        break

                    if data != []:
                        """ ↓ Место для твоего кода, если его необходисо исполнять на каждой закрытой свече ↓ """
                        print(f"Свеча закрыта {data[0]} {data[1]} ... {data[-1]}")
                


                """ ↓ Место для твоего кода, если его необходисо исполнять при каждом изменении ↓ """
                print(msg)



                if backtest != None:
                    queue.put("STOP")

            # Если данных нет 60 секунд переподключение
            else:
                # if activate == True:
                reconnect_timeout += 1
                if reconnect_timeout > 60:
                    module.logger("info", "Данные нет слишком долго")
                    activate = False
                time.sleep(1)

    def run_dynamic_loops(self, keys, name, queue, path, current_index=0, current_values=None):
        if current_values is None:
            current_values = []

        if current_index == len(keys):
            self.iteration_count += 1
            self.update_variables(keys, current_values)
            print(f"Итерация {self.iteration_count}: {self.variables}")

            self.agent(name, queue, path, True, self.iteration_count)
            return

        key = keys[current_index]
        _, start, end, step = self.variables[key]  # Берем min, max, шаг

        for value in range(start, end + 1, step):
            self.run_dynamic_loops(keys, name, queue, path, current_index + 1, current_values + [value])

    def update_variables(self, keys, values):
        """Обновляет переменные в __dict__."""
        for key, value in zip(keys, values):
            _, min_val, max_val, step = self.variables[key]
            self.__dict__[key] = (value, min_val, max_val, step)
