import os, sys, importlib
from multiprocessing import Process, Queue
import global_variable, paths

class AgentManager:
    def __init__(self):
        self.agents = {}  # Хранит процессы агентов
        self.queues = {}  # Хранит очереди агентов

    def start_agent(self, name):
        """
            Запуск процессов агента со своими очередями данных

            :name - имя агента
        """
        if name in self.agents and self.agents[name].is_alive():
            print(f"Агент {name} уже запущен!")
            return

        try:
            # Определяем путь к агенту и загружаем модуль
            module_name = f"run_{name}"
            module_dir = os.path.join(global_variable.AGENTS_FOLDER, name)
            sys.path.append(module_dir)
            module = importlib.import_module(module_name)

            # Создаем очередь и запускаем процесс
            queue = Queue()
            process = Process(target=module.Agent().agent, args=(name, queue, paths.RUN_AGENT_PATH), daemon=True)
            process.start()

            self.agents[name] = process
            self.queues[name] = queue

            # print(f"Агент {name} запущен.")
        except Exception as e:
            print(f"Ошибка запуска агента {name}: {e}")

    def stop_agent(self, name):
        """
            Останавливает конкретного агента.
        """

        # Для отладки 
        print("Запущенные агенты:", list(self.agents.keys()))

        if name not in self.agents:
            print(f"Агент {name} не найден!")
            return

        try:
            self.queues[name].put("STOP")  # Посылаем сигнал остановки
            self.agents[name].join(timeout=7)  # Ждем завершения

            # Для отладки
            # if self.agents[name].exitcode is not None:  # Если процесс уже завершился
            #     print(f"Агент {name} уже завершился сам.")

            if self.agents[name].is_alive():  # Если процесс завис, убиваем принудительно
                self.agents[name].terminate()
                print(f"Агент {name} был принудительно остановлен.")

            del self.agents[name]
            del self.queues[name]
            print(f"Агент {name} остановлен.")
        except Exception as e:
            print(f"Ошибка остановки агента {name}: {e}")

    def backtest_agent(self, name):
        """
            Запуск процессов агента со своими очередями данных

            :name - имя агента
        """
        if name in self.agents and self.agents[name].is_alive():
            print(f"Агент {name} уже запущен!")
            return

        try:
            # Определяем путь к агенту и загружаем модуль
            module_name = f"run_{name}"
            module_dir = os.path.join(global_variable.AGENTS_FOLDER, name)
            sys.path.append(module_dir)
            module = importlib.import_module(module_name)
            mod = module.Agent()

            # Создаем очередь и запускаем процесс
            backtest = True
            queue = Queue()
            process = Process(target=mod.agent, args=(name, queue, os.path.dirname(__file__), backtest), daemon=True)
            process.start()

            self.agents[name] = process
            self.queues[name] = queue

            # print(f"Агент {name} запущен.")
        except Exception as e:
            print(f"Ошибка запуска агента {name}: {e}")


    def get_queue(self, name):
        return self.queues.get(name, None)

    def stop_all(self):
        for name in list(self.agents.keys()):
            self.stop_agent(name)