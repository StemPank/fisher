import os, sys, importlib
from multiprocessing import Process, Queue
import global_variable, paths

from utils.logging import logger

class AgentManager:
    def __init__(self):
        self.agents = {}  # Хранит процессы агентов
        self.queues = {}  # Хранит очереди агентов

    def start_agent(self, name, exchange, symbol, intervall, commission, variable_data):
        """
            Запуск процессов агента со своими очередями данных

            :name - имя агента
        """

        # if symbol or intervall or commission

        if name in self.agents and self.agents[name].is_alive():
            logger.info(f"Агент {name} уже запущен!")
            return False

        try:

            # Определяем путь к агенту и загружаем модуль
            module_name = f"code_agent"
            module_dir = os.path.join(paths.MAIN_REPOSITORY, f"core/{exchange}")
            sys.path.append(module_dir)

            # Удаляем модуль из кэша перед импортом (перезагрузка), Это заставляет Python заново загрузить код при новом запуске.
            if module_name in sys.modules:
                del sys.modules[module_name]

            module = importlib.import_module(module_name)

            # Создаем очередь и запускаем процесс
            queue = Queue()
            
            process = Process(target=module.Agent, args=(symbol, intervall, commission, variable_data, name, exchange, queue, paths.RUN_AGENT_PATH), daemon=True)
            process.start()

            self.agents[name] = process
            self.queues[name] = queue

            logger.info(f"Агент {name} запущен. {self.agents[name]}")
            return True
        except Exception as e:
            logger.warning(f"Ошибка запуска агента {name}: {e}")
            return False

    def start_agent_backtest(self, name, exchange, symbol, intervall, commission, variable_data):
        """
            Запуск процессов агента со своими очередями данных

            :name - имя агента
        """

        if name in self.agents and self.agents[name].is_alive():
            logger.info(f"Агент {name} уже запущен!")
            return False

        try:
            # Определяем путь к агенту и загружаем модуль
            module_name = f"code_agent"
            module_dir = os.path.join(paths.MAIN_REPOSITORY, f"core/{exchange}")
            sys.path.append(module_dir)

            # Удаляем модуль из кэша перед импортом (перезагрузка), Это заставляет Python заново загрузить код при новом запуске.
            if module_name in sys.modules:
                del sys.modules[module_name]

            module = importlib.import_module(module_name)

            # Создаем очередь и запускаем процесс
            queue = Queue()
            
            process = Process(target=module.Agent, args=(symbol, intervall, commission, variable_data, name, exchange, queue, paths.RUN_AGENT_PATH, False), daemon=True)
            process.start()

            self.agents[name] = process
            self.queues[name] = queue

            logger.info(f"Агент {name} запущен.")
            return True
        except Exception as e:
            logger.warning(f"Ошибка запуска агента {name}: {e}")
            return False

    def stop_agent(self, name):
        """
            Останавливает конкретного агента.

            :name - имя агента
        """

        # Для отладки 
        logger.debug(f"Запущенные агенты: {list(self.agents.keys())}")

        if name not in self.agents:
            logger.info(f"Агент {name} не найден!")
            return False

        try:
            self.queues[name].put("STOP")  # Посылаем сигнал остановки
            self.agents[name].join(timeout=7)  # Ждем завершения

            # Для отладки
            # if self.agents[name].exitcode is not None:  # Если процесс уже завершился
            #     print(f"Агент {name} уже завершился сам.")

            if self.agents[name].is_alive():  # Если процесс завис, убиваем принудительно
                self.agents[name].terminate()
                logger.info(f"Агент {name} был принудительно остановлен.")

            del self.agents[name]
            del self.queues[name]
            logger.info(f"Агент {name} остановлен.")
            return True
            
        except Exception as e:
            logger.warning(f"Ошибка остановки агента {name}: {e}")
            return False

    def optimization_agent_backtest(self, name, exchange, symbol, intervall, commission, variable_data):
        """
            Запуск процессов агента со своими очередями данных

            :name - имя агента
        """

        if name in self.agents and self.agents[name].is_alive():
            logger.info(f"Оптимизация {name} уже запущена!")
            return False

        try:
            # Определяем путь к агенту и загружаем модуль
            module_name = f"code_agent"
            module_dir = os.path.join(paths.MAIN_REPOSITORY, f"core/{exchange}")
            sys.path.append(module_dir)

            # Удаляем модуль из кэша перед импортом (перезагрузка), Это заставляет Python заново загрузить код при новом запуске.
            if module_name in sys.modules:
                del sys.modules[module_name]

            module = importlib.import_module(module_name)

            # Создаем очередь и запускаем процесс
            queue = Queue()
            
            process = Process(target=module.Agent, args=(symbol, intervall, commission, variable_data, name, exchange, queue, paths.RUN_AGENT_PATH, True), daemon=True)
            process.start()

            self.agents[name] = process
            self.queues[name] = queue

            logger.info(f"Оптимизация {name} запущена.")
            return True
        except Exception as e:
            logger.warning(f"Ошибка запуска оптимизации агента {name}: {e}")
            return False

    