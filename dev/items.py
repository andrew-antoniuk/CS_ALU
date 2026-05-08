"""
Docstring for dev.items
"""

# pylint: skip-file

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
from data import Wire, AND, OR, NAND, XOR, NOT, BUF, NOR, XNOR, Switch

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
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
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

        if not self.is_output and hasattr(self.parent_gate, "gate") and self.parent_gate.gate:
            self.parent_gate.gate.update()

        if not self.is_output and hasattr(self.parent_gate, "output_pins"):
            for pin in self.parent_gate.output_pins:
                if pin.logic_wire:
                    pin.state = pin.logic_wire.status
                    pin.update_color()

    def mousePressEvent(self, event):

        scene = self.scene()

        if scene.start_pin is None:

            if not self.is_output:
                return

            scene.start_wire(self)

        else:

            scene.finish_wire(self)

        super().mousePressEvent(event)

class WireItem(QGraphicsLineItem):

    def __init__(self, start_pin, end_pin=None):

        super().__init__()

        self.start_pin = start_pin
        self.end_pin = end_pin
        self.setZValue(-1)

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

    def __init__(self, gate, image_path, label=""):

        super().__init__()

        self.gate = gate

        pixmap = QPixmap(image_path)

        self.setPixmap(pixmap)
        self.label_item = QGraphicsTextItem(label, self)

        self.label_item.setDefaultTextColor(Qt.black)
        self.input_pins = []
        self.output_pins = []

        self.create_pins()

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)

        text_width = self.label_item.boundingRect().width()

        pixmap_width = self.pixmap().width()

        self.label_item.setPos(
            (pixmap_width - text_width) / 2,
            self.pixmap().height()
        )

    def create_pins(self):
        pass

    def itemChange(self, change, value):

        if change == self.ItemPositionHasChanged:

            for pin in self.input_pins + self.output_pins:

                for wire in pin.connected_wires:
                    wire.update_position()

        return super().itemChange(change, value)

class NotGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-not-96.png",
            "NOT"
        )

    def create_pins(self):

        in1 = PinItem(self)

        wire1 = Wire()
        wire_out = Wire()

        self.gate = NOT(
            [wire1],
            wire_out
        )

        out = PinItem(self, is_output=True)

        in1.logic_wire = wire1
        out.logic_wire = wire_out

        in1.setPos(0, 15)

        out.setPos(self.pixmap().width(), 30)

        self.input_pins = [in1]
        self.output_pins = [out]

class BufGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-buffer-96.png",
            "BUF"
        )

    def create_pins(self):

        in1 = PinItem(self)

        wire1 = Wire()
        wire_out = Wire()

        self.gate = BUF(
            [wire1],
            wire_out
        )

        out = PinItem(self, is_output=True)

        in1.logic_wire = wire1
        out.logic_wire = wire_out

        in1.setPos(0, 15)

        out.setPos(self.pixmap().width(), 30)

        self.input_pins = [in1]
        self.output_pins = [out]

class AndGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-and-96.png",
            "AND"
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

class OrGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-or-96.png",
            "OR"
        )

    def create_pins(self):

        in1 = PinItem(self)
        in2 = PinItem(self)

        wire1 = Wire()
        wire2 = Wire()
        wire_out = Wire()

        self.gate = OR(
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

class NorGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-nor-96.png",
            "NOR"
        )

    def create_pins(self):

        in1 = PinItem(self)
        in2 = PinItem(self)

        wire1 = Wire()
        wire2 = Wire()
        wire_out = Wire()

        self.gate = NOR(
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

class XnorGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-xnor-96.png",
            "XNOR"
        )

    def create_pins(self):

        in1 = PinItem(self)
        in2 = PinItem(self)

        wire1 = Wire()
        wire2 = Wire()
        wire_out = Wire()

        self.gate = XNOR(
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

class XorGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-xor-96.png",
            "XOR"
        )

    def create_pins(self):

        in1 = PinItem(self)
        in2 = PinItem(self)

        wire1 = Wire()
        wire2 = Wire()
        wire_out = Wire()

        self.gate = XOR(
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

class NandGateItem(GateItem):

    def __init__(self):

        super().__init__(
            None,
            "images/icons8-logic-gate-nand-96.png",
            "NAND"
        )

    def create_pins(self):

        in1 = PinItem(self)
        in2 = PinItem(self)

        wire1 = Wire()
        wire2 = Wire()
        wire_out = Wire()

        self.gate = NAND(
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

class SwitchItem(GateItem):

    def __init__(self):

        self.wire = Wire()
        self.logic = Switch(False, self.wire)

        super().__init__(
            None,
            "images/icons8-toggle-off-90.png"
        )

        # self.update_visual()

        self.state = 0

    def create_pins(self):

        out = PinItem(self, is_output=True)
        out.logic_wire = self.wire

        out.setPos(self.pixmap().width(), 20)

        self.output_pins = [out]


    def mousePressEvent(self, event):

        self.state ^= 1

        self.output_pins[0].set_state(self.state)

        if self.state:
            self.setPixmap(QPixmap("images/icons8-toggle-on-90.png"))
        else:
            self.setPixmap(QPixmap("images/icons8-toggle-off-90.png"))

        super().mousePressEvent(event)

class LedItem(GateItem):
    def __init__(self):
        # Initialize with the "off" image by default
        super().__init__(
            None,
            "images/icons8-light-96.png",
            "LED"
        )
        self.state = 0
        self.refresh()

    def create_pins(self):
        # LEDs only have an input pin
        in1 = PinItem(self, is_output=False)

        self.input_wire = Wire()
        in1.logic_wire = self.input_wire

        in1.setPos(-6, self.pixmap().height() / 2 - 6)
        self.input_pins = [in1]
        self.output_pins = []

    def refresh(self):
        """
        Updates the visual representation based on the input pin's state.
        """
        # Get state from the input pin
        new_state = self.input_pins[0].state

        if self.state != new_state:
            self.state = new_state
            image_path = "images/icons8-light-on-96.png" if self.state else "images/icons8-light-96.png"
            self.setPixmap(QPixmap(image_path))

    def set_state(self, value):
        """
        Explicitly set state and refresh visual.
        """
        if self.input_pins:
            self.input_pins[0].state = value
        self.refresh()

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

        match self.current_tool:
            case "NOT":
                item = NotGateItem()

            case "BUF" | "BUFFER":
                item = BufGateItem()

            case "AND":
                item = AndGateItem()

            case "OR":
                item = OrGateItem()

            case "NOR":
                item = NorGateItem()

            case "XNOR":
                item = XnorGateItem()

            case "XOR":
                item = XorGateItem()

            case "NAND":
                item = NandGateItem()

            case "SWITCH":
                item = SwitchItem()

            case "LED":
                item = LedItem()

            case _:
                super().mousePressEvent(event)
                return

        item.setPos(event.scenePos())

        self.addItem(item)
        self.current_tool = None

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.temp_wire:
            self.temp_wire.update_end(event.scenePos())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        super().mouseReleaseEvent(event)

    def cancel_wire(self):

        self.removeItem(self.temp_wire)

        self.temp_wire = None
        self.start_pin = None

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                pins = []
                if hasattr(item, "input_pins"):
                    pins.extend(item.input_pins)

                if hasattr(item, "output_pins"):
                    pins.extend(item.output_pins)

                if hasattr(item, "input_pin"): # For the original LedItem structure
                    pins.append(item.input_pin)

                # Remove all wires connected to these pins from the scene
                for pin in pins:
                    for wire in pin.connected_wires[:]:
                        if wire.scene():
                            self.removeItem(wire)

                        other_pin = wire.end_pin if wire.start_pin == pin else wire.start_pin

                        if other_pin and wire in other_pin.connected_wires:
                            other_pin.connected_wires.remove(wire)

                # remove the gate or the selected wire itself
                self.removeItem(item)

    def update_simulation(self):

        for item in self.items():
            # Handle Gates and LEDs (since LedItem now inherits from GateItem)

            if isinstance(item, GateItem):

                for pin in item.input_pins + item.output_pins:
                    if pin.logic_wire:
                        pin.state = pin.logic_wire.status
                        pin.update_color()

                if isinstance(item, LedItem):
                    item.refresh()

            elif isinstance(item, WireItem):
                item.update_state()

    def finish_wire(self, end_pin):

        # if not self.start_pin:
            # return

        # if end_pin == self.start_pin:
        #     self.cancel_wire()
        #     return

        # if end_pin.is_output == self.start_pin.is_output:
        #     self.cancel_wire()
        #     return

        # wire = WireItem(self.start_pin, end_pin)

        # end_pin.logic_wire = self.start_pin.logic_wire

        # self.addItem(wire)

        # self.removeItem(self.temp_wire)

        # self.temp_wire = None
        # self.start_pin = None

        if not self.start_pin:
            return

        wire = WireItem(self.start_pin, end_pin)
        end_pin.logic_wire = self.start_pin.logic_wire

        if hasattr(end_pin.parent_gate, "gate") and end_pin.parent_gate.gate:
            logic_gate = end_pin.parent_gate.gate

            # Find which input index this pin represents (0, 1, etc.)
            if end_pin in end_pin.parent_gate.input_pins:
                idx = end_pin.parent_gate.input_pins.index(end_pin)

                # Update the logic gate's wire reference
                logic_gate.input_w[idx] = self.start_pin.logic_wire

                # Register the gate to listen for updates on the new wire
                self.start_pin.logic_wire.destinations.append(logic_gate)

                # Trigger an immediate update to reflect the current state
                logic_gate.update()

        self.addItem(wire)
        self.removeItem(self.temp_wire)
        self.temp_wire = None
        self.start_pin = None
