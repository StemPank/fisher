import os
import pickle
import threading
import telebot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QTextEdit

from utils.logging import logger
import paths
from gui.bot.telegram_bot import start_telegram_bot

SETTING_FILE = paths.SETTING_BOT_FILE

class SettingBotTab(QWidget):
    """Вкладка настроек Telegram-бота"""
    def __init__(self, parent=None, language=None):
        super().__init__()
        self.parent = parent  
        self.language = language
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Создаёт UI"""
        layout = QVBoxLayout()

        # API Token
        self.token_label = QLabel("API Token:")
        self.token_input = QLineEdit()
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_input)

        # Chat ID
        self.chat_id_label = QLabel("Chat ID:")
        self.chat_id_input = QLineEdit()
        layout.addWidget(self.chat_id_label)
        layout.addWidget(self.chat_id_input)

        # Флаг автозапуска бота
        self.auto_start_checkbox = QCheckBox("Запускать бота при старте программы")
        layout.addWidget(self.auto_start_checkbox)

        # Кнопки
        self.save_button = QPushButton("Сохранить")
        self.load_button = QPushButton("Загрузить")
        self.start_button = QPushButton("Запустить")

        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)
        self.start_button.clicked.connect(lambda: start_telegram_bot(True))

        layout.addWidget(self.save_button)
        layout.addWidget(self.load_button)
        layout.addWidget(self.start_button)

        # Кнопка для показа/скрытия инструкции
        self.toggle_instruction_button = QPushButton("Показать инструкцию")
        self.toggle_instruction_button.clicked.connect(self.toggle_instruction)
        layout.addWidget(self.toggle_instruction_button)

        # Текстовая инструкция
        self.instruction_text = QTextEdit()
        self.instruction_text.setReadOnly(True)
        self.instruction_text.setText(self.get_instruction_text())
        self.instruction_text.setVisible(False)
        layout.addWidget(self.instruction_text)

        self.setLayout(layout)

    def get_instruction_text(self):
        """Возвращает текст инструкции"""
        return """Как создать бота и получить API Token:
1 Открой Telegram и найди @BotFather.
2 Отправь команду `/newbot` и следуй инструкциям.
3 Полученный API Token вставьте в поле "API Token".

Как получить Chat ID:
1 Найди @userinfobot в Telegram.
2 Отправь команду `/start`, бот покажет твой `chat_id`.
3 Скопируйте ID и вставьте в поле "Chat ID".

Если используете группу:
1 Добавьте бота в группу.
2 Назначьте его администратором.
3 Отправьте `/start`, чтобы активировать бота.
"""

    def toggle_instruction(self):
        """Разворачивает/сворачивает инструкцию"""
        if self.instruction_text.isVisible():
            self.instruction_text.setVisible(False)
            self.toggle_instruction_button.setText("Показать инструкцию")
        else:
            self.instruction_text.setVisible(True)
            self.toggle_instruction_button.setText("Скрыть инструкцию")

    def save_settings(self):
        """Сохраняет настройки в файл"""
        settings = {
            "token": self.token_input.text().strip(),
            "chat_id": self.chat_id_input.text().strip(),
            "auto_start": self.auto_start_checkbox.isChecked()
        }

        with open(SETTING_FILE, "wb") as file:
            pickle.dump(settings, file)
        logger.info("Настройки телеграмм бота сохранены!")
        QMessageBox.information(self, "Успех", "Настройки сохранены!")

    def load_settings(self):
        """Загружает настройки из файла"""
        if os.path.exists(SETTING_FILE):
            with open(SETTING_FILE, "rb") as file:
                settings = pickle.load(file)

            self.token_input.setText(settings.get("token", ""))
            self.chat_id_input.setText(settings.get("chat_id", ""))
            self.auto_start_checkbox.setChecked(settings.get("auto_start", False))