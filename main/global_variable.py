import os, pickle
from datetime import date
import paths 
from dotenv import load_dotenv, set_key, unset_key

def current_date():
    """
        Получение текущей даты
    """
    current_date = date.today()
    return current_date

def setting_file(key = None):
    """
        Получение данных из файла настроек
    """
    if os.path.exists(paths.SETTING_FILE):
        with open(paths.SETTING_FILE, "rb") as file:
            state = pickle.load(file)
            if state.get(key):
                res = state.get(key)
                return res
            else:
                return state

           
def setting_agent_file(agent_name, key = None):
    """
        Получение данных из файла настроек агента
    """
    setting = setting_file()
    if setting.get("folder_path"):
        agent_path = setting.get("folder_path")
    setting_agent_path = f"{agent_path}/{agent_name}/{agent_name}_settings.pkl"
    if os.path.exists(setting_agent_path):
        with open(setting_agent_path, "rb") as file:
            state = pickle.load(file)
            if state.get(key):
                res = state.get(key)
                return res
            else:
                return state

LANGUAGE = setting_file("language")
AGENTS_FOLDER = setting_file("folder_path")

def registered_data_providers(key=None):
    """
        Получает список добавленных поставщиков данных со своими ключами

        Args:
            key (str) = None: имя добавленого поставщика

        Returns:
            (key != None) str: получает имя, поставшика и ключи. Пример: ('binance1', 'binance', '1223456api', '654321api')
            (key = None) str: получает список имен добавленных поставщиков данных
    """
    names = []
    ENV_FILE = os.path.join(paths.CONFIG_PATH, ".env")
    load_dotenv(ENV_FILE)
    for clue, value in os.environ.items():
        if clue.startswith("PROVIDER_"):
            name, exchange, api_key, secret_key = value.split("|")
            if key == name:
                return name, exchange, api_key, secret_key
            names.append(name)
    return names


if __name__ == "__main__":
    print(registered_data_providers("binance1"))