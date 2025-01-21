import os, pickle
from datetime import date
from datetime import datetime
from PyQt5.QtCore import QDate

CHAPTER = os.path.dirname(__file__)
SETTING_FILE = os.path.join(os.path.join(CHAPTER, "../gui/setting"), "setting.pkl")
AGENT_FILE = os.path.join(os.path.join(CHAPTER, "../gui/agent"), "agent.pkl")
STATE_FILE = os.path.join(os.path.join(CHAPTER, "../gui"), "state.pkl")
OPERATIVE_STATE_FILE = os.path.join(os.path.join(CHAPTER, "../gui"), "operative_state.pkl")

ICONS_PATH = os.path.join(CHAPTER, "../gui/icons")


def language_check():
    """
        Запрос языка
    """
    if os.path.exists(SETTING_FILE):
            with open(SETTING_FILE, "rb") as file:
                state = pickle.load(file)
                if state.get("language"):
                    language = state.get("language")
                    return language

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
    if os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, "rb") as file:
            state = pickle.load(file)
            if state.get(key):
                res = state.get(key)
                return res
            else:
                return state

LANGUAGE = setting_file("language")
AGENTS_FOLDER = setting_file("folder_path")
           
def setting_agent_file(agent_name):
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
            return state
            #надо доработать
            start_date = state.get("start_date")
            end_date = state.get("end_date")
            current_date_enabled = state.get("current_date_enabled", False)
            return start_date, end_date, current_date_enabled

def agent_file():
    """
        Получение данных из файла настроек
    """
    if os.path.exists(AGENT_FILE):
        with open(AGENT_FILE, "rb") as file:
            state = pickle.load(file)
            return state

def state_file():
    """
        Получение данных из файла настроек
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "rb") as file:
            state = pickle.load(file)
            return state

if __name__ == "__main__":
    # print(setting_agent_file("123"))
    # print(setting_file())
    # print(language_check())
    # print(str(current_date()))
    # print(AGENT_TABLE_HEADERS.get('russian'))
    # print(AGENTS_FOLDER)

    print(agent_file())
    print("_______________")
    print(state_file())