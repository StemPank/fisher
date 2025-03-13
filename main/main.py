import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

import gui.texts as texts, paths
from core.gui.defot_file import create_defolt_file_setting

from utils.logging import clean_old_logs, logger

def install_agents():
    """Проверяет и устанавливает `bind_agents` при первом запуске."""
    try:
        import bind_agents  # Пробуем импортировать
        import agent_indicators
        logger.info("Модуль bind_agents и agent_indicators уже установлен")
    except ImportError:
        
        agent_folder = paths.INSTALL_BIND
        if not agent_folder or not os.path.exists(agent_folder):
            logger.debug("Папка с агентами не найдена, установка пропущена.")
            return
        

        logger.info(f"Устанавливаем модуль из {agent_folder}")

        pip_command = [sys.executable, "-m", "pip", "install", agent_folder]

        # Если работаем в `venv`, не используем `--user`
        if not hasattr(sys, 'real_prefix') and sys.base_prefix == sys.prefix:
            pip_command.append("--user")

        try:
            subprocess.run(pip_command, check=True)
            logger.info("Модуль успешно установлен!")
        except subprocess.CalledProcessError as e:
            logger.info(f"Ошибка установки: {e}")

def main():
    """
        Точка входа
    """
    # install_agents()  # Проверяем и устанавливаем модули

    # создание дефолтного файла настроек приложения
    create_defolt_file_setting() 

    # Создание экземпляра приложения
    app = QApplication(sys.argv)

    # Инициализация главного окна
    main_window = MainWindow()
    main_window.show()

    # Логирование, отчистка старых логов
    clean_old_logs()
    logger.info("Приложение запущено")

    # Запуск основного цикла приложения
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()