"""
Launch
"""

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui
from _code import Ui_Simulator
from items import CircuitScene

class SimulatorWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.ui = Ui_Simulator()

        self.ui.setupUi(self)

        self.scene = CircuitScene()

        self.ui.graphicsView.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 3000, 3000)
        self.ui.graphicsView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.ui.graphicsView.setDragMode(self.ui.graphicsView.RubberBandDrag)

        self.ui.listWidget.itemClicked.connect(
            self.select_tool
        )

        self.ui.actionCursor.triggered.connect(
            self.reset_tool
        )

    def select_tool(self, item):

        text = item.text()

        match text:
            case "NOT Gate":
                self.scene.current_tool = "NOT"

            case "BUF Gate":
                self.scene.current_tool = "BUF"

            case "AND Gate":
                self.scene.current_tool = "AND"

            case "OR Gate":
                self.scene.current_tool = "OR"

            case "NOR Gate":
                self.scene.current_tool = "NOR"

            case "XNOR Gate":
                self.scene.current_tool = "XNOR"

            case "XOR Gate":
                self.scene.current_tool = "XOR"

            case "NAND Gate":
                self.scene.current_tool = "NAND"

            case "Switch":
                self.scene.current_tool = "SWITCH"

            case "ZERO":
                self.scene.current_tool = "ZERO"

            case "ONE":
                self.scene.current_tool = "ONE"

            case "Bulb":
                self.scene.current_tool = "LED"

    def reset_tool(self):

        self.scene.current_tool = None

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = SimulatorWindow()

    window.show()

    sys.exit(app.exec_())
