import os, pickle
import shutil

import paths, global_variable, gui.texts as texts
import core.table_for_agent as table_for_agent

"""
    Файл отвечает за создание и удаление файлов
"""

def create_defolt_file_setting():
    """
        Создание основного файла настроек исли его не существует
    """
    if not os.path.exists(paths.SETTING_FILE):
        state = {
            "language": "russian",                  # язык интерфейса
            "folder_path": "C:/PY/fisher/agents",   # путь до агентов
        } 
        with open(paths.SETTING_FILE, "wb") as file:
            pickle.dump(state, file)


CODE_RUN_FILE = '''
import os, sys, importlib
import random
import time

"""
    Подсказки:
        !!!Блоки кода class Agent(): и def __init__(self): не изменяйте и не удаляйте!!!
        На объявленный класс Agent() можете не обращать внимание если не понимаете как он работает
        Переменные COIN и INTEVAL необходимо заполнить необходимыми вам значениями. !!!Не изменяйте названия переменных!!!
        Если хотите объявить новую функцию, в параметрах первое значение поставьте self
        Чтобы получить доступ к переменным объявленным в __init__ из функций. Пример: self.COIN
        Доступные интервалы, смотрите в документации
"""

class Agent():
    def __init__(self):
        # Название монеты
        self.COIN = "BTCUSDT"
        # Интервал 
        self.INTEVAL = "1"

    def agent(self, name, queue, path, backtest=False):
        """Функция агента, обрабатывающего данные."""
        print(f"Агент {name} запущен. \nВыбраная пара {self.COIN} и интервал {self.INTEVAL}")
        
        module_name = "run_agents"
        module_dir = path
        sys.path.append(module_dir)
        module = importlib.import_module(module_name)
        module.run_agent(name, self.COIN, self.INTEVAL, queue, backtest)

        while True:
            """ Внутри лигической проверки, скрипт будет стабатывать при появлении новых данных с биржи
             вне оператора лучше использовать time.sleep(1) """
            if not queue.empty(): # 
                msg = queue.get()
                if msg == "STOP":
                    module.stop_agent(name)
                    print(f"Агент {name} завершает работу.")
                    break  # Выходим из цикла и процесс завершается

                """ ↓ Место для твоего кода ↓ """
            
                
                print(f"Агент работает\n{msg}\n")


            # data = random.random()  # Генерация случайного значения
            # print(f"Агент работает\n{data}\n")
            # time.sleep(1)  # Имитируем выполнение задачи
'''


class New_file():
    """
        Создание необходимых файлов для работы агента
            -центральный скрипт +
            -файл параметров
            -раздел в БД
    """
    def __init__(self):
        """
            Запрос расположения файлов агента
        """
        self.agent_path = global_variable.setting_file("folder_path")

    def create_new_file(self, name_agent, exchange):
        """
            Создание папки с именем агента
            Создание дефолтного файла агента со скриптом 
            Сздание дефолтного файла настроек агента
        """

        # Пути
        agent_dir = f"{self.agent_path}/{name_agent}"
        python_file_path = f"{agent_dir}/run_{name_agent}.py"
        settings_file_path = f"{agent_dir}/{name_agent}_settings.pkl"

        # Проверка, существует ли папка
        if not os.path.exists(agent_dir):
            os.mkdir(agent_dir)
        
        # Проверка, существует ли файл Python
        if not os.path.isfile(python_file_path):
            with open(python_file_path, "w", encoding="utf-8") as file:
                file.write(CODE_RUN_FILE)

        settings = {
            "exchange": exchange,
            "start_date": global_variable.current_date(),
            "end_date": global_variable.current_date(),
            "current_date_enabled": True,
        }
        # Проверка, существует ли файл .pkl
        if os.path.isfile(settings_file_path):
            # Если файл существует, пересоздаем его
            with open(settings_file_path, "wb") as file:
                pickle.dump(settings, file)
        else:
            # Если файла нет, создаем новый
            with open(settings_file_path, "wb") as file:
                pickle.dump(settings, file)
        
        # Создаем БД
        table_for_agent.create(name_agent)

    def del_file_agent(self, name_agent):
        """
            Удаление файлов при удалении агента
        """
        try:
            os.remove(f"{self.agent_path}/{name_agent}/run_{name_agent}.py")
            os.remove(f"{self.agent_path}/{name_agent}/{name_agent}_settings.pkl")
            table_for_agent.drop(name_agent)
            shutil.rmtree(f"{self.agent_path}/{name_agent}")
        except: pass

