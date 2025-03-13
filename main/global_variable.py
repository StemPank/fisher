import os, pickle, logging, inspect
from datetime import date
import paths 
from dotenv import load_dotenv, set_key, unset_key

from utils.logging import logger

# Настройка логгера
logger_global_variable = logging.getLogger("SETTING")
logger_global_variable.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(paths.LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d -> %(caller_filename)s:%(caller_lineno)d): %(message)s"
)
file_handler.setFormatter(formatter)
logger_global_variable.addHandler(file_handler)
def get_caller_info():
    frame = inspect.currentframe().f_back.f_back  # Два уровня вверх: (1) текущая функция, (2) вызывающая функция
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    return filename, lineno

def current_date():
    """
        Получение текущей даты
    """
    current_date = date.today()
    return current_date

_settings_cache = None  # Кеш настроек
_settings_mtime = 0  # Время последнего изменения файла

def setting_file(key=None, force_reload=False):
    """
        Получение данных из файла настроек с кешированием.
        Автоматически обновляет кэш, если файл был изменен.
        
        :param key: Ключ параметра для получения
        :param force_reload: Если True — сбрасывает кэш и перечитывает файл
        :return: Значение параметра
    """
    caller_filename, caller_lineno = get_caller_info()
    global _settings_cache, _settings_mtime
    settings_path = paths.SETTING_FILE  # Путь к файлу настроек
    
    # Проверяет, существует ли файл настроек
    if not os.path.exists(settings_path):
        return None
    # Проверяет, изменился ли файл настроек
    file_mtime = os.path.getmtime(settings_path)  # Время последнего изменения файла

    if force_reload or _settings_cache is None or file_mtime > _settings_mtime:
        try:
            with open(settings_path, "rb") as file:
                _settings_cache = pickle.load(file)
                logger_global_variable.debug(f"Данные в кэше настроек обновились", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
            _settings_mtime = file_mtime  # Обновляем время изменения
        except Exception as e:
            logger_global_variable.error(f"Ошибка чтения настроек: {e}", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
            return None
    
    # Если key=None, возвращает весь словарь настроек
    if key is None:
        return _settings_cache
    
    return _settings_cache.get(key)

def setting_agent_file(agent_name, key = None):
    """
        Получение данных из файла настроек агента
    """
    caller_filename, caller_lineno = get_caller_info()
    setting = setting_file()
    if setting.get("folder_path"):
        agent_path = setting.get("folder_path")
    setting_agent_path = f"{agent_path}/{agent_name}/{agent_name}_settings.pkl"
    if os.path.exists(setting_agent_path):
        with open(setting_agent_path, "rb") as file:
            state = pickle.load(file)
            if state.get(key):
                res = state.get(key)
                logger_global_variable.debug(f"Получение данных из файла настроек агента: Ключ:{key}, {res}", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
                return res
            else:
                logger_global_variable.debug(f"Получение данных из файла настроек агента: {state}", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
                return state

# LANGUAGE = setting_file("language")
# AGENTS_FOLDER = setting_file("folder_path")

def registered_data_providers(key=None, exc=None):
    """
        Получает список добавленных поставщиков данных со своими ключами

        Args:
            key (str) = None: имя добавленого поставщика
            exc (bool) = None: метка получения постащика по имени

        Returns:
            (key != None, exc = True) str: получает имя, поставшика и ключи. Пример: ('binance1', 'binance', '1223456api', '654321api')
            (key != None) str: получает имя, поставшика и ключи. Пример: ('binance1', 'binance', '1223456api', '654321api')
            (key = None) str: получает список имен добавленных поставщиков данных
    """
    caller_filename, caller_lineno = get_caller_info()
    names = []
    ENV_FILE = os.path.join(paths.CONFIG_PATH, ".env")
    load_dotenv(ENV_FILE)
    for clue, value in os.environ.items():
        if clue.startswith("PROVIDER_"):
            name, exchange, api_key, secret_key = value.split("|")
            if key == name and exc == None:
                logger_global_variable.debug(f"Получение данных поставщика по имени: {name}", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
                return name, exchange, api_key, secret_key
            if key == name and exc == True:
                logger_global_variable.debug(f"Получение названия поставщика по имени: {name}", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
                return exchange
            names.append(name)
    logger_global_variable.debug(f"Получение списка поставщиков: {names}", extra={"caller_filename": caller_filename, "caller_lineno": caller_lineno})
    return names


def record_warn(file, text):
    i=0
    while True:
        file_ = f"{paths.WARN_PATH}/warning_{file}.py"
        if not os.path.isfile(file_):
            with open(file_, "w", encoding="utf-8") as file:
                            file.write(text)
        else:
            file = f"{file}_{i}"
            i += 1

if __name__ == "__main__":
    print(registered_data_providers("by", exc = True))