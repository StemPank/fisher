import sys, os
import re
from dotenv import load_dotenv, set_key, unset_key

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QLabel, QLineEdit, QComboBox, QFormLayout, QHBoxLayout, QHeaderView, QMessageBox
)
from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtCore import QSettings, QSize

import paths, config, global_variable, gui.texts as texts

from utils.logging import logger

# Загружаем переменные окружения из .env
ENV_FILE = os.path.join(paths.CONFIG_PATH, ".env")
load_dotenv(ENV_FILE)
"""
    os.path.join(paths.CONFIG_PATH, ".env") — формирует полный путь к .env файлу.
    load_dotenv(ENV_FILE) — загружает переменные окружения из .env в os.environ, после чего их можно получить через os.getenv("ПЕРЕМЕННАЯ").
"""


class ProviderTab(QWidget):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)
        self.parent = parent  
        self.language = language

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(texts.PROVIDER_TABLE_HEADERS[self.language])
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 40)
        self.table.horizontalHeader().setStretchLastSection(False) # Запрет изменения размеров колонок
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Запрет редактирования таблицы
        self.layout.addWidget(self.table)

        add_button = QPushButton()
        add_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus.png")))
        add_button.setIconSize(QSize(24, 24))
        # Изменяем иконку при нажатии
        add_button.pressed.connect(lambda: add_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus-pressed.png"))))
        add_button.released.connect(lambda: add_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus.png"))))
        add_button.clicked.connect(self.add_provider)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)

        self.layout.addLayout(button_layout)

        self.load_providers()

    def load_providers(self):
        """Загружает данные из .env в таблицу"""
        for key, value in os.environ.items():
            if key.startswith("PROVIDER_"):
                name, exchange, _, _ = value.split("|")
                self.add_to_table(name, exchange)

    def add_provider(self):
        """Добавляет нового поставщика"""
        logger.debug(f"Вызов диалогового окна создание поставщика")
        dialog = AddProviderDialog(self, self.language)
        if dialog.exec_():
            provider_name, exchange, api_key, secret_key = dialog.get_data()
            if provider_name:
                if self.is_unique_item(self.table, provider_name):
                    self.add_to_table(provider_name, exchange)
                    self.save_provider(provider_name, exchange, api_key, secret_key)
                    logger.info(f"Поставщик {provider_name} корректно создан")

    def is_unique_item(self, table_widget, text, column=0):
        """
        Проверяет, существует ли элемент с заданным текстом в указанной колонке таблицы.
        
        :param table_widget: QTableWidget - таблица для проверки
        :param text: str - текст для проверки на уникальность
        :param column: int - индекс колонки для проверки (по умолчанию 0)
        :return: (bool) - True, если текст уникален, False, если он уже есть в таблице
        """
        for row in range(table_widget.rowCount()):
            item = table_widget.item(row, column)
            if item and item.text() == text:
                logger.info("Поставщик с атким именем уже существует")
                QMessageBox.information(self, "Ошибка", "Поставщик с атким именем уже существует")
                return False  # Найден дубликат
        return True  # Уникально


    def add_to_table(self, provider_name, exchange):
        """Добавляет поставщика в таблицу"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(provider_name))
        self.table.setItem(row, 1, QTableWidgetItem(exchange))

        delete_button = QPushButton()
        delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash.png")))
        # Изменяем иконку при нажатии
        delete_button.pressed.connect(lambda: delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash-pressed.png"))))
        delete_button.released.connect(lambda: delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash.png"))))
        delete_button.clicked.connect(lambda: self.remove_provider(provider_name, row))
        self.table.setCellWidget(row, 2, delete_button)

    def save_provider(self, provider_name, exchange, api_key, secret_key):
        """Сохраняет поставщика в .env"""
        set_key(ENV_FILE, f"PROVIDER_{provider_name}", f"{provider_name}|{exchange}|{api_key}|{secret_key}")
        logger.debug("Данные поставщика сохранены")

    def remove_provider(self, provider_name, row):
        """Удаляет поставщика из .env и таблицы"""
        try:
            logger.debug(f"Нажата кнопка удаления агента {provider_name}")
            unset_key(ENV_FILE, f"PROVIDER_{provider_name}")
            self.table.removeRow(row)
            logger.info("Поставщик удален")
        except Exception as e:
            logger.warning(f"Ошибка удаления поставщика: {e}")

def validate_inputs(method):
    """Декоратор для валидации полей перед выполнением accept()."""
    def wrapper(self):
        name = self.name_input.text().strip()
        api_key = self.api_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()

        # Очистка ошибок перед проверкой
        self.name_error.setText("")
        self.api_error.setText("")

        # Валидация имени: Только латинские буквы, цифры и _
        if not name or not re.match(r"^[A-Za-z0-9_]+$", name):
            self.name_error.setText("Имя должно содержать только латинские буквы, цифры и _")
            self.name_error.show()
            return

        # Валидация API ключей: Только латинские буквы и цифры
        if not api_key or not secret_key or not re.match(r"^[A-Za-z0-9]+$", api_key) or not re.match(r"^[A-Za-z0-9]+$", secret_key):
            self.api_error.setText("API ключи должны содержать только латинские буквы и цифры")
            self.api_error.show()
            return

        
        self.name_error.hide()  # Если ошибок нет, скрываем ошибку
        self.api_error.hide()  # Если ошибок нет, скрываем ошибку
        return method(self)  # Вызываем оригинальный метод `accept`
    
    return wrapper

class AddProviderDialog(QDialog):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(texts.DIALOG_PROVIDERS_ADD[self.language])
        self.setFixedSize(400, 250)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.exchange_input = QComboBox()
        self.exchange_input.addItems(config.LIST_PROVIDERS)
        self.api_key_input = QLineEdit()
        self.secret_key_input = QLineEdit()

        # Метки ошибок
        self.name_error = QLabel("")
        self.name_error.setStyleSheet("color: red;")
        self.name_error.hide()
        self.api_error = QLabel("")
        self.api_error.setStyleSheet("color: red;")
        self.api_error.hide()

        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][0], self.name_input)
        form_layout.addRow(self.name_error)  # Ошибка под полем
        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][1], self.exchange_input)
        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][2], self.api_key_input)
        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][3], self.secret_key_input)
        form_layout.addRow(self.api_error)  # Ошибка под API ключами

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(texts.DIALOG_BUTTON[self.language][0])
        self.cancel_button = QPushButton(texts.DIALOG_BUTTON[self.language][1])

        self.ok_button.clicked.connect(self.validated_accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    @validate_inputs
    def validated_accept(self):
        """Вызывает accept(), если валидация пройдена."""
        return self.accept()

    def get_data(self):
        return (
            self.name_input.text(),
            self.exchange_input.currentText(),
            self.api_key_input.text(),
            self.secret_key_input.text(),
        )

    
    
    
