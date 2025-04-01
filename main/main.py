import os
import sys
import subprocess
import time
import shutil
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

import paths, global_variable
from core.gui.defot_file import create_defolt_file_setting
from gui.bot.telegram_bot import start_telegram_bot

from utils.logging import clean_old_logs, logger

def clear_cache():
    """Удаляет кэш-файлы перед перезапуском."""
    cache_dirs = ["__pycache__"]  # Укажи папки с кэшем

    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)  # Удаляем папку со всем содержимым

def restart_program():
    """Перезапускает программу, удаляя кэш."""
    logger.info("Очищаем кэш...")
    clear_cache()
    
    logger.info("Перезапуск программы...")
    time.sleep(1)  # Небольшая пауза для безопасности

    python = sys.executable  # Получаем путь к Python
    script = sys.argv[0]  # Получаем путь к текущему скрипту

    subprocess.Popen([python, script], close_fds=True)  # Запускаем новый процесс
    sys.exit()  # Завершаем текущий процесс

def install_packages():
    """Проверяет и устанавливает `bind_agents` и `agent_indicators` при первом запуске."""
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

def install_program():
    """
    Начальная установка
        - была ошибка, после создания файла настроек, программа могла получить информацию только после перезапуска, добавлен перезапуск
    """
    res, path = create_defolt_file_setting(paths.HOME_REPOSITORY) 
    time.sleep(1)
    if res:
        try:
            if global_variable.setting_file("folder_path") != path:
                restart_program()
        except:
            restart_program()

def main():
    """
        Точка входа
    """
    # install_packages()  # Проверяем и устанавливаем модули, раскоментировать по готовности

    # создание дефолтного файла настроек приложения
    install_program()
    # Запуск телеграмм бота 
    start_telegram_bot()

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
        