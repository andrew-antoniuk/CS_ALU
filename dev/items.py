"""
Docstring for dev.items
"""

from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem
)

from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtCore import Qt, QLineF, QTimer
from data import AND, Wire

class PinItem(QGraphicsEllipseItem):

    RADIUS = 6

    def __init__(self, parent_gate, is_output=False):
        super().__init__(
            0,
            0,
            self.RADIUS * 2,
            self.RADIUS * 2,
            parent_gate
        )

        self.parent_gate = parent_gate
        self.is_output = is_output

        self.connected_wires = []

        self.state = 0
        self.logic_wire = None
        self.setPen(QPen(Qt.black, 1))
        self.update_color()

    def update_color(self):

        color = Qt.green if self.state else Qt.red

        self.setBrush(QBrush(color))

    def set_state(self, value):

        self.state = value

        self.update_color()

        if self.logic_wire:
            self.logic_wire.status = value

        for wire in self.connected_wires:
            wire.update_state()

    def mousePressEvent(self, event):

        if not self.is_output:
            return

        scene = self.scene()

        scene.start_wire(self)

        super().mousePressEvent(event)

class WireItem(QGraphicsLineItem):

    def __init__(self, start_pin, end_pin=None):

        super().__init__()

        self.start_pin = start_pin
        self.end_pin = end_pin

        self.start_pin.connected_wires.append(self)

        if self.end_pin:
            self.end_pin.connected_wires.append(self)

        self.update_position()
        self.update_state()

    def update_position(self):

        p1 = self.start_pin.sceneBoundingRect().center()

        if self.end_pin:
            p2 = self.end_pin.sceneBoundingRect().center()
        else:
            p2 = p1

        self.setLine(QLineF(p1, p2))

    def update_state(self):

        signal = self.start_pin.state

        color = Qt.green if signal else Qt.red

        self.setPen(QPen(color, 3))

        if self.end_pin and self.end_pin.state != signal:
            self.end_pin.set_state(signal)

class GateItem(QGraphicsPixmapItem):

    def __init__(self, gate, image_path):

        super().__init__()

        self.gate = gate

        pixmap = QPixmap(image_path)

        self.setPixmap(pixmap)

        self.input_pins = []
        self.output_pins = []

        self.create_pins()

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)

    def create_pins(self):
        pass

    def itemChange(self, change, value):

        if change == self.ItemPositionHasChanged:

            for pin in self.input_pins + self.output_pins:

                for wire in pin.connected_wires:
                    wire.update_position()

        return super().itemChange(change, value)

class AndGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-and-96.png"
        )

    def create_pins(self):

        in1 = PinItem(self)
        in2 = PinItem(self)

        wire1 = Wire()
        wire2 = Wire()
        wire_out = Wire()

        self.gate = AND(
            [wire1, wire2],
            wire_out
        )

        out = PinItem(self, is_output=True)

        in1.logic_wire = wire1
        in2.logic_wire = wire2
        out.logic_wire = wire_out

        in1.setPos(0, 15)
        in2.setPos(0, 45)

        out.setPos(self.pixmap().width(), 30)

        self.input_pins = [in1, in2]
        self.output_pins = [out]

class TempWire(QGraphicsLineItem):

    def __init__(self, start_pos):

        super().__init__()

        self.start_pos = start_pos

        self.setPen(QPen(Qt.gray, 2, Qt.DashLine))

    def update_end(self, end_pos):

        self.setLine(
            self.start_pos.x(),
            self.start_pos.y(),
            end_pos.x(),
            end_pos.y()
        )

class CircuitScene(QGraphicsScene):

    def __init__(self):

        super().__init__()

        self.temp_wire = None
        self.start_pin = None
        self.current_tool = None

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_simulation
        )

        self.timer.start(50)


    def start_wire(self, pin):

        self.start_pin = pin

        pos = pin.sceneBoundingRect().center()

        self.temp_wire = TempWire(pos)

        self.addItem(self.temp_wire)

    def mousePressEvent(self, event):

        if self.current_tool == "AND":

            item = AndGateItem()

            item.setPos(event.scenePos())

            self.addItem(item)

            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.temp_wire:

            self.temp_wire.update_end(event.scenePos())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        if self.temp_wire:

            item = self.itemAt(
                event.scenePos(),
                self.views()[0].transform()
            )

            if isinstance(item, PinItem):

                if item == self.start_pin:
                    self.removeItem(self.temp_wire)

                    self.temp_wire = None
                    self.start_pin = None

                    return

                if item.is_output == self.start_pin.is_output:
                    self.removeItem(self.temp_wire)

                    self.temp_wire = None
                    self.start_pin = None

                    return

                wire = WireItem(self.start_pin, item)
                item.logic_wire = self.start_pin.logic_wire
                self.addItem(wire)

            self.removeItem(self.temp_wire)

            self.temp_wire = None
            self.start_pin = None

        super().mouseReleaseEvent(event)

    def update_simulation(self):

        for item in self.items():

            if isinstance(item, GateItem):

                for pin in item.input_pins + item.output_pins:

                    if pin.logic_wire:

                        pin.state = pin.logic_wire.status

                        pin.update_color()

            elif isinstance(item, LedItem):

                item.refresh()

class SwitchItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/toggle.png"
        )

        self.state = 0

    def create_pins(self):

        out = PinItem(self, is_output=True)

        out.setPos(self.pixmap().width(), 20)

        self.output_pins = [out]

    def mousePressEvent(self, event):

        self.state ^= 1

        self.output_pins[0].set_state(self.state)

        super().mousePressEvent(event)

class LedItem(QGraphicsEllipseItem):

    def __init__(self):

        super().__init__(0, 0, 30, 30)

        self.input_pin = PinItem(self)

        self.input_pin.setPos(-10, 10)

        self.refresh()

    def refresh(self):

        signal = self.input_pin.state

        color = Qt.green if signal else Qt.darkRed

        self.setBrush(QBrush(color))

    def set_state(self, value):

        self.input_pin.state = value

        self.refresh()
