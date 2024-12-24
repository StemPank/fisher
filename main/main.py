import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QTabWidget
from agent_tab import AgentTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Программа на PyQt5")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        # Меню бар
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Меню "Инструменты"
        tools_menu = QMenu("Инструменты", self)
        menu_bar.addMenu(tools_menu)

        self.agent_action = QAction("Агент", self, checkable=True)
        self.agent_action.toggled.connect(self.toggle_agent_tab)
        tools_menu.addAction(self.agent_action)

        # Меню "Действия"
        actions_menu = QMenu("Действия", self)
        menu_bar.addMenu(actions_menu)

        # Центральный виджет
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    def toggle_agent_tab(self, checked):
        if checked:
            self.add_agent_tab()
        else:
            self.remove_agent_tab()

    def add_agent_tab(self):
        if not hasattr(self, "agent_tab"):
            self.agent_tab = AgentTab(self)
            self.tabs.addTab(self.agent_tab, "Агент")

    def remove_agent_tab(self):
        index = self.tabs.indexOf(self.agent_tab)
        if index != -1:
            self.tabs.removeTab(index)
            del self.agent_tab

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
