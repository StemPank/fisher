import os, pickle
from PyQt5.QtWidgets import (QFileDialog, QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, QLabel, QComboBox,
                             QHeaderView, QLineEdit)

import paths, global_variable, gui.texts as texts, config

class SettingTab(QWidget):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)
        
        self.parent = parent  
        if language != None:
            self.language = language
        else:
            self.language = global_variable.LANGUAGE
        
        # Загрузка сохранённых данных
        # self.folder_path_text = ""
        # self.language_code = "english" # По умолчанию
        self.setting_load()

        # Макет
        self.Vlayout = QVBoxLayout()
        self.Vlayout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Выбор языка
        self.layout_language = QHBoxLayout()
        self.Vlayout.addLayout(self.layout_language)

        self.label_language = QLabel(texts.SETTING_LIST[self.language][0])
        self.layout_language.addWidget(self.label_language)

        self.language_select = QComboBox()
        self.language_select.addItems(config.LIST_LANGUAGE)
        self.language_select.setCurrentText(self.get_language_display_name(self.language_text))
        self.layout_language.addWidget(self.language_select)

        # Поле выбора папки
        self.layout_path = QHBoxLayout()
        self.Vlayout.addLayout(self.layout_path)
        
        self.label_path = QLabel(texts.SETTING_LIST[self.language][1])
        self.layout_path.addWidget(self.label_path)

            # Текстовое поле
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Выберите папку...")
        self.folder_path.setPlaceholderText(self.folder_path_text)
        self.layout_path.addWidget(self.folder_path)

            # Кнопка
        self.browse_button = QPushButton("...")
        self.browse_button.setFixedWidth(30)  # Фиксированная ширина кнопки
        self.browse_button.clicked.connect(self.select_folder)
        self.layout_path.addWidget(self.browse_button)
        
        # Кнопка сохранения
        self.layout_button = QHBoxLayout()
        self.Vlayout.addLayout(self.layout_button)

        add_agent_button = QPushButton(texts.SETTING_BUTTON[self.language])
        add_agent_button.clicked.connect(self.setting_save)
        self.layout_button.addStretch()
        self.layout_button.addWidget(add_agent_button)

        self.setLayout(self.Vlayout)

    def select_folder(self):
        """Открывает диалоговое окно для выбора папки."""
        folder = QFileDialog.getExistingDirectory(self, texts.DIALOG_SETTING[self.language])
        if folder:  # Если пользователь выбрал папку
            self.folder_path.setText(folder)
    
    def setting_save(self):
        """Созраняет настройки"""
        language_code = self.get_language_code(self.language_select.currentText())
        state = {
            "language": language_code,
            "folder_path": self.folder_path.text(),
        }
        with open(paths.SETTING_FILE, "wb") as file:
            pickle.dump(state, file)

    def setting_load(self):
        """Загрузка видимости выбранных настроек"""
        if os.path.exists(paths.SETTING_FILE):
            with open(paths.SETTING_FILE, "rb") as file:
                state = pickle.load(file)
                self.language_text = state.get("language")
                self.folder_path_text = state.get("folder_path")

    @staticmethod
    def get_language_code(display_name):
        """
        Возвращает код языка по его отображаемому названию.
        """
        language_map = {
            "English": "english",
            "Русский": "russian"
        }
        
        return language_map.get(display_name, "russian")  # Если язык не найден, используем "english" по умолчанию

    @staticmethod
    def get_language_display_name(language_code):
        """
        Возвращает отображаемое название языка по его коду.
        """
        language_map = {
            "english": "English",
            "russian": "Русский"
        }
        
        return language_map.get(language_code, "Русский")  # Если код не найден, используем "English" по умолчанию