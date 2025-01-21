import os
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt  
import gui.global_variable as global_variable
import gui.texts as texts


class AgentSpecificTab(QWidget):
    def __init__(self, parent=None, agent_name=None):
        super().__init__(parent)
        self.parent = parent 
        self.agent_name = agent_name

        # Макет
        self.Vlayout = QVBoxLayout()
        self.Vlayout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        self.layout_path = QHBoxLayout()
        self.Vlayout.addLayout(self.layout_path)
        
        self.layout_button = QHBoxLayout()
        button = QPushButton(f"Welcome to {agent_name}'s Tab!")
        self.layout_button.addStretch()
        self.layout_button.addWidget(button)
        
        self.setLayout(self.Vlayout)