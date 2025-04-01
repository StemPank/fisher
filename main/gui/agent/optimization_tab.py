from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSpinBox, QMessageBox
)

import paths, global_variable, gui.texts as texts
from utils.logging import logger


class OptimizationTab(QWidget):
    """Окно оптимизации параметров"""
    
    def __init__(self, parent=None, agent_name=None, table_agent=None, agent_manager=None, language=None):
        super().__init__(parent)
        self.parent = parent 
        self.agent_name = agent_name
        self.table_agent = table_agent
        self.agent_manager = agent_manager
        if language != None:
            self.language = language
        else:
            self.language = global_variable.setting_file("language")

        self.layout = QVBoxLayout(self)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Загрузить переменные")
        self.start_button = QPushButton("Старт оптимизации")
        
        self.load_button.clicked.connect(self.load_variables)
        self.start_button.clicked.connect(self.start_optimization)

        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.start_button)
        self.layout.addLayout(button_layout)

        # Таблица переменных
        self.variable_table = QTableWidget()
        self.variable_table.setColumnCount(5)
        self.variable_table.setHorizontalHeaderLabels(["Переменная", "Значение", "Мин", "Макс", "Шаг"])
        self.variable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.variable_table)

        self.load_variables()  # Автоматическая загрузка при открытии

    def load_variables(self):
        """Загружает переменные из базы данных"""
        variables = self.table_agent.get_all_variables()  # Получаем переменные

        self.variable_table.setRowCount(len(variables))

        for row, (name, value) in enumerate(variables):
            # Название переменной (не редактируемое)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~2)  # Делаем ячейку нередактируемой
            self.variable_table.setItem(row, 0, name_item)

            # Поле для текущего значения переменной
            value_spin = QSpinBox()
            value_spin.setMinimum(-999999)
            value_spin.setMaximum(999999)
            value_spin.setValue(int(value))  # Устанавливаем текущее значение
            
            # Поля для диапазонов и шага
            min_spin = QSpinBox()
            min_spin.setMinimum(-999999)
            min_spin.setMaximum(999999)
            min_spin.setValue(int(value))  # Устанавливаем текущее значение

            max_spin = QSpinBox()
            max_spin.setMinimum(-999999)
            max_spin.setMaximum(999999)
            max_spin.setValue(int(value))  # Устанавливаем текущее значение

            step_spin = QSpinBox()
            step_spin.setMinimum(1)
            step_spin.setMaximum(999999)
            step_spin.setValue(1)

            self.variable_table.setCellWidget(row, 1, value_spin)
            self.variable_table.setCellWidget(row, 2, min_spin)
            self.variable_table.setCellWidget(row, 3, max_spin)
            self.variable_table.setCellWidget(row, 4, step_spin)

    def start_optimization(self):
        """Собирает данные и передает их для оптимизации"""
        variable_data = []

        for row in range(self.variable_table.rowCount()):
            name = self.variable_table.item(row, 0).text()
            value = self.variable_table.cellWidget(row, 1).value()
            min_val = self.variable_table.cellWidget(row, 2).value()
            max_val = self.variable_table.cellWidget(row, 3).value()
            step = self.variable_table.cellWidget(row, 4).value()

            if min_val >= max_val:
                QMessageBox.warning(self, "Ошибка", f"Ошибка в {name}: мин >= макс!")
                return
            
            variable_data.append((name, (value, min_val, max_val, step)))
        
        row = self.table_agent.get_data_main_table()
        if row == []:
            logger.error(f"Параметры агента не настроены (Зайдите в агента и сохраните начальные параметры)")
            return False
        logger.debug(f"Переданные параметры {(row[0][0], row[0][1], row[0][2], row[0][3])} переменные {variable_data}")
        res = self.agent_manager.optimization_agent_backtest(self.agent_name, 
                                                            row[0][0], 
                                                            row[0][1], 
                                                            row[0][2],  
                                                            row[0][3], 
                                                            variable_data)
        
        self.parent.optimization_agent_backtest()