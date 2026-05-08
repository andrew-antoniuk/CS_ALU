"""
Launch
"""

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtGui
from _code import Ui_Simulator
from items import (
    CircuitScene,
    SwitchItem,
    AndGateItem,
    OrGateItem,
    NotGateItem,
    BufGateItem,
    NandGateItem,
    NorGateItem,
    XorGateItem,
    XnorGateItem,
    SwitchItem,
    ZeroItem,
    OneItem,
    ALUItem
)
from data import Circuit

class SimulatorWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.ui = Ui_Simulator()
        self.ui.setupUi(self)

        self.elements = Circuit()
        self.scene = CircuitScene(self.elements)

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

        self.ui.actionSave.triggered.connect(
            self.save_circuit
        )

        self.ui.actionOpen.triggered.connect(
            self.load_circuit
        )

    def save_circuit(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Circuit",
            "",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        self.elements.save(filename)

    def load_circuit(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Circuit",
            "",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        data = self.elements.load(filename)

        self.scene.clear()
        self.elements.clear()

        created = {}

        for comp in data["components"]:

            item = None

            match comp["type"]:

                case "AND":
                    item = AndGateItem()

                case "OR":
                    item = OrGateItem()

                case "NOT":
                    item = NotGateItem()

                case "BUF":
                    item = BufGateItem()

                case "NAND":
                    item = NandGateItem()

                case "NOR":
                    item = NorGateItem()

                case "XOR":
                    item = XorGateItem()

                case "XNOR":
                    item = XnorGateItem()

                case "SWITCH":
                    item = SwitchItem()

                case "ONE":
                    item = OneItem()

                case "ZERO":
                    item = ZeroItem()

                case "ALU":
                    item = ALUItem()

            if item:

                x, y = comp["position"]

                item.setPos(x, y)

                self.scene.addItem(item)

                if hasattr(item, "gate") and item.gate:

                    item.gate.position = (x, y)
                    item.gate.id = comp["id"]

                    self.elements.add_component(item.gate)

                    created[comp["id"]] = item

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

            case "ALU":
                self.scene.current_tool = "ALU"


            case "Bulb":
                self.scene.current_tool = "LED"

    def reset_tool(self):

        self.scene.current_tool = None

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = SimulatorWindow()

    window.show()

    sys.exit(app.exec_())
