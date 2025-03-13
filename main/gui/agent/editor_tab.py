import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla, QsciLexerPython

import paths, global_variable

from utils.logging import logger

class AdvancedEditor(QsciScintilla):
    def __init__(self):
        super().__init__()

        # Подсветка синтаксиса Python
        self.lexer = QsciLexerPython()
        self.lexer.setDefaultFont(QFont("Courier", 12))
        self.setLexer(self.lexer)

        # Настройки нумерации строк
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")  # Автоопределение ширины номеров строк
        self.setMarginsForegroundColor(QColor("#555"))
        self.setMarginsBackgroundColor(QColor("#EEE"))

        # Автоотступы
        self.setAutoIndent(True)

        # Подсветка текущей строки
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#E0E0E0"))

        # Скобочное выделение
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Сворачивание кода
        self.setFolding(QsciScintilla.PlainFoldStyle)

        # Прокрутка
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

class EditorTab(QWidget):
    """Редактор кода с подсветкой синтаксиса"""
    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        self.file_path = f"{global_variable.setting_file("folder_path")}/{agent_name}/run_{agent_name}.py"
        self.layout = QVBoxLayout(self)

        # Создаём редактор с подсветкой синтаксиса
        self.editor = AdvancedEditor()
        
        self.layout.addWidget(self.editor)

        self.load_file()

    def load_file(self):
        """Загружает файл в редактор"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.editor.setText(file.read())

    def save_file(self):
        """Сохраняет изменения в файл"""
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(self.editor.text())  # Сохраняем текст из редактора в файл
        logger.info("Файл сохранен")