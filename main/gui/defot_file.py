import os, pickle
import gui.global_variable as global_variable

CODE_RUN_FILE = """
class WorkerThread(QThread):
    new_data_signal = pyqtSignal(dict)
    new_order_book_signal = pyqtSignal(dict)

    def __init__(self, queue_kline: Queue, queue_depth: Queue):
        super().__init__()
        self.queue_kline = queue_kline
        self.queue_depth = queue_depth
        self.running = True

    def run(self):
        while self.running:
            print('Работает')

            time.sleep(1)  # simulate waiting for new data

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
"""

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
        setting = global_variable.setting_file()
        if setting.get("folder_path"):
            self.agent_path = setting.get("folder_path")

    def create_new_file(self, name_agent):
        """
            Создание папки с именем агента
            Создание дефолтного файла агента со скриптом 
            Сздание дефолтного файла настроек агента
        """
        os.mkdir(f"{self.agent_path}/{name_agent}")
        with open(f"{self.agent_path}/{name_agent}/run_{name_agent}.py", "w") as file:
            file.write(CODE_RUN_FILE)

        settings = {
            "start_date": global_variable.current_date(),
            "end_date": global_variable.current_date(),
            "current_date_enabled": True,
        }
        with open(f"{self.agent_path}/{name_agent}/{name_agent}_settings.pkl", "wb") as file:
            pickle.dump(settings, file)

    def del_file_agent(self, name_agent):
        """
            Удаление файлов при удалении агента
        """
        try:
            os.remove(f"{self.agent_path}/{name_agent}/run_{name_agent}.py")
            os.remove(f"{self.agent_path}/{name_agent}/{name_agent}_settings.pkl")
            os.rmdir(f"{self.agent_path}/{name_agent}")
        except: pass

def create_defolt_file_setting():
    """
        Создание основного файла настроек исли его не существует
    """
    if not os.path.exists(global_variable.SETTING_FILE):
        state = {
            "language": "russian",
            "folder_path": "C:/PY/fisher/agents",
        }
        with open(global_variable.SETTING_FILE, "wb") as file:
            pickle.dump(state, file)