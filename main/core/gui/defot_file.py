import os, pickle
import shutil

import paths, global_variable, gui.texts as texts, config
import core.gui.table_for_agent as table_for_agent
import core.gui.text_file_agent as text_file_agent

from utils.logging import logger

"""
    Файл отвечает за создание и удаление файлов
"""

def create_defolt_file_setting():
    """
        Создание основного файла настроек если его не существует
    """
    if not os.path.exists(paths.SETTING_FILE):
        state = {
            "language": "russian",                  # язык интерфейса
            "folder_path": "C:/PY/fisher/agents",   # путь до агентов
        } 
        with open(paths.SETTING_FILE, "wb") as file:
            pickle.dump(state, file)

        logger.debug(f"Создание основного файла настроек: {state}")

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
            Создание папки, центрального файла, файла настроек и БД агента

            :name_agent (str) - имя агента
            :exchange (str) - название поставщика данных
        """
                
        self.exchange_options = config.LIST_OF_AVAILABLE_BASE_ENDPOINTS
        self.selected_exchange = global_variable.registered_data_providers(exchange, exc=True)

        # Пути
        result={}
        agent_dir = f"{self.agent_path}/{name_agent}"
        python_file_path = f"{agent_dir}/run_{name_agent}.py"
        settings_file_path = f"{agent_dir}/{name_agent}_settings.pkl"
        
        try: 
            # Проверка, существует ли папка
            if not os.path.exists(agent_dir):
                os.mkdir(agent_dir)
                logger.debug(f"Папка агента создана")
            else:
                logger.debug(f"Папка агента существует")
            result["folder"] = True
        except Exception as e:
            logger.warning(f"Ошибка создания папки агента: {e}")

        

        try:    
            exchange_ = self.selected_exchange.upper()
            # logger.debug(f"Поставщик данных: {exchange}")
            # logger.debug(f"Поставщик в верхнем регистре: {exchange_}")
            text_content = getattr(text_file_agent, exchange_, "")
            # Проверка, существует ли файл Python
            if not os.path.isfile(python_file_path):
                with open(python_file_path, "w", encoding="utf-8") as file:
                    file.write(text_content)
                logger.debug(f"Файл агента созданы")
            else:
                logger.debug(f"Файл агента существует")
            result["main_file"] = True
            
        except Exception as e:
            logger.warning(f"Ошибка создания файда py агента: {e}")

        try:
            if self.selected_exchange in self.exchange_options:
                sub_option = self.exchange_options[self.selected_exchange]
            settings = {
                "exchange": exchange,
                "sub_option": sub_option[0],
                "start_date": global_variable.current_date(),
                "end_date": global_variable.current_date(),
                "current_date_enabled": True,
            }
            
            with open(settings_file_path, "wb") as file:
                pickle.dump(settings, file)
                
            result["setting_file"] = True
            logger.debug(f"Файл настроек агента созданы {settings}")
        except Exception as e:
            logger.warning(f"Ошибка создания файда настроек агнета: {e}")

        try:    
            # Создаем БД
            table_for_agent.create(name_agent, agent_dir)
            result["db_file"] = True
            logger.debug(f"Файл БД агента создан")
        except Exception as e:
            logger.warning(f"Ошибка создания БД: {e}")
        
        logger.debug(f"Результат создания файлов агента {result}")
        if result["folder"] and result["main_file"] and result["setting_file"] and result["db_file"]:
            logger.info(f"Агент {name_agent} корректно создан")
            return True
        else:
            self.del_file_agent_if_defect(name_agent, result)
            return False
    
    def del_file_agent_if_defect(self, name_agent, result):
        """
            Удаляет файлы при некоректном создании агента
        
            :name_agent (str) - имя агента
        """
        agent_dir = f"{self.agent_path}/{name_agent}"
        try:
            if not result["db_file"]:
                os.remove(f"{self.agent_path}/{name_agent}/run_{name_agent}.py")
                os.remove(f"{self.agent_path}/{name_agent}/{name_agent}_settings.pkl")
                shutil.rmtree(f"{self.agent_path}/{name_agent}")
                logger.info(f"Файлы агента {name_agent} удалены")
            elif not result["setting_file"]:
                os.remove(f"{self.agent_path}/{name_agent}/run_{name_agent}.py")
                table_for_agent.drop(name_agent, agent_dir)
                shutil.rmtree(f"{self.agent_path}/{name_agent}")
                logger.info(f"Файлы агента {name_agent} удалены")
        except Exception as e:
            logger.warning(f"Ошибка удаления файлов или файлов не уже не существует: {e}")
    
    def del_file_agent(self, name_agent):
        """
            Удаляет файлы агента
        
            :name_agent (str) - имя агента
        """
        
        agent_dir = f"{self.agent_path}/{name_agent}"
        # try:
        try:
            os.remove(f"{self.agent_path}/{name_agent}/run_{name_agent}.py")
        except:pass
        try:
            os.remove(f"{self.agent_path}/{name_agent}/{name_agent}_settings.pkl")
        except:pass
        try:
            table_for_agent.drop(name_agent, agent_dir)
        except:pass
        try:
            shutil.rmtree(f"{self.agent_path}/{name_agent}")
        except:pass
        #     logger.info(f"Файлы агента {name_agent} удалены")
        # except Exception as e:
        #     logger.warning(f"Ошибка удаления файлов или файлов не уже не существует: {e}")

