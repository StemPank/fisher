import os
import pickle
import threading
import time
import telebot
import requests

from gui.bot.reques_processing import register_handlers  
from utils.logging import logger
import paths

SETTING_FILE = paths.SETTING_BOT_FILE
CHECK_INTERVAL = 10  # Интервал проверки сети (в секундах)
TELEGRAM_API_URL = "https://api.telegram.org"  # URL для проверки соединения с Telegram

class TelegramBot:
    """Telegram-бот с обработкой команд с авто-восстановлением и защитой от зависания"""
    
    _instance = None  # Статическая переменная для хранения единственного экземпляра

    def __new__(cls, *args, **kwargs):
        """Реализация Singleton (единственного экземпляра)."""
        if cls._instance is None:
            cls._instance = super(TelegramBot, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "initialized"):  # Чтобы __init__ не вызывался повторно
            self.bot = None # Объект Telegram-бота
            self.bot_thread = None # Поток для бота
            self.monitor_thread = None
            self.chat_id = None
            self.token = None
            self.running = False  # Флаг работы бота
            self.last_error_logged = None  # Последняя ошибка (чтобы не спамить логами)
            self.initialized = True  # Пометка, что init уже был выполнен

    def load_settings(self, manual_start=None):
        """Загружает настройки бота из файла"""
        if os.path.exists(SETTING_FILE):
            with open(SETTING_FILE, "rb") as file:
                settings = pickle.load(file)

            self.token = settings.get("token")
            self.chat_id = settings.get("chat_id")
            auto_start = settings.get("auto_start", False)

            if auto_start:
                self.start_bot()
            elif manual_start:
                self.start_bot()

    def check_internet(self):
        """Проверяет наличие интернета и доступность Telegram API"""
        try:
            response = requests.get(TELEGRAM_API_URL, timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def start_bot(self):
        """Запускает Telegram-бота в отдельном потоке"""
        if not self.check_internet():
            logger.error("Интернет недоступен.")
            # self.needs_restart = True
            return

        if not self.token or not self.chat_id:
            # logger.error("Некорректные настройки бота.")
            return

        if self.running:
            # logger.error("Бот уже запущен!")
            return

        self.running = True  # Устанавливаем флаг работы бота
        self.bot = telebot.TeleBot(self.token)

        register_handlers(self.bot)  # Подключаем обработчики команд

        logger.info("Запуск Telegram-бота...")
        self.bot_thread = threading.Thread(target=self.run_polling, daemon=True)
        self.bot_thread.start()
    
    def run_polling(self):
        """Обёртка для безопасного запуска polling"""
        while self.running:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True, logger_level=0)
            except Exception as e:
                if self.last_error_logged != str(e):
                    logger.warning(f"Неизвестная ошибка: {e}")
                    self.last_error_logged = str(e)
                time.sleep(5)

    
    @staticmethod
    def send_message(text):
        """Глобальный метод для отправки сообщений в Telegram из любого места кода."""
        
        instance = TelegramBot._instance
        if instance and instance.bot and instance.chat_id:
            try:
                instance.bot.send_message(instance.chat_id, text)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения в Telegram: {e}")

# Функция для запуска при старте программы
def start_telegram_bot(manual_start=None):
    bot_instance = TelegramBot()
    bot_instance.load_settings(manual_start)

"""
Как использовать глобальную отправку сообщений?
Теперь можно отправлять сообщения в Telegram из любого места в коде:

from gui.bot.telegram_bot import TelegramBot

TelegramBot.send_message("Сообщение")
"""