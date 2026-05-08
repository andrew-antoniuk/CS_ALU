"""
Main classes for ALU dev.data
"""

from uuid import uuid4
import json

class Circuit:

    def __init__(self):

        self.components = []
        self.wires = []

    def add_component(self, comp):

        if comp not in self.components:
            self.components.append(comp)

    def add_wire(self, wire):

        if wire not in self.wires:
            self.wires.append(wire)

    def clear(self):

        self.components.clear()
        self.wires.clear()

    def to_dict(self):

        return {
            "components": [
                comp.to_dict()
                for comp in self.components
            ],
            "wires": [
                wire.to_dict()
                for wire in self.wires
                if wire.to_dict() is not None
            ]
        }

    def save(self, filename):

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                self.to_dict(),
                file,
                indent=4
            )

    @staticmethod
    def load(filename):

        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    def simulate(self):

        """
        Run and update
        """

        for comp in self.components:
            if hasattr(comp, "update"):
                comp.update()

class Component:

    """
    IDs store
    """

    def __init__(self):
        self.id = str(uuid4())
        self.position = (0, 0)
        self.label = "COMP"

    def to_dict(self):

        """
        Serializer for saving the circuit into the file
        """

        x, y = self.position

        return {"type": self.label, "id": self.id, "position": [x, y]}

class Wire(Component):

    """
    Docstring for Wire
    """

    def __init__(self):
        super().__init__()
        # For propagation
        self.destinations = []
        self._status = False
        self.label = "WIRE"

    @property
    def status(self):

        """
        Getter for status
        """

        return self._status

    @status.setter
    def status(self, new_signal):
        # If the signal has not changed, we do nothing
        if self._status == new_signal:
            return

        self._status = new_signal

        # Notify all connected gates that the signal has changed
        for gate in self.destinations:
            gate.update()

    def to_dict(self):

        data = {"id": self.id, "destinations": []}

        for gate in self.destinations:
            data["destinations"].append(gate.id)

        return data

class Gate(Component):

    """
    Gate Father Class
    """

    def __init__(self, w_in: list, w_out = None):
        super().__init__()
        # Save a reference to the input wires(list of objects)
        self.input_w = w_in
        # Save a reference to the output wire where will pass the result
        self.output_w = w_out

        # Register this gate in the input conductors
        # Now, when the signal changes on any of these Wires, it will know
        # to trigger an update on that particular gate.
        for wire in self.input_w:
            wire.destinations.append(self)
        # Perform the initial logic gate evaluation (evaluate)
        # and write the result to the output conductor status (output_w.status).
        # We also store a copy of the result in self.out for internal use.
        self.out = False
        self.label = "GATE"

    def __repr__(self):
        return f"input_wires={self.input_w}, output_wire={self.output_w}, out_value={self.out}"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        return False

    def update(self):
        """
        The method that is called by the conductor when the signal changes
        """
        new_val = self.evaluate()
        # We update the output conductor - this will start the next wave of propagation
        if self.output_w:
            self.output_w.status = new_val

    def to_dict(self):

        x, y = self.position

        return {
            "type": self.label,
            "id": self.id,
            "position": [x, y]
        }

class Switch(Component):

    """
    Switcher, beginning of the logical chain
    """

    def __init__(self, value = False, wire = None):
        super().__init__()
        self._status = value
        self.wire = wire
        self.label = "SWITCH"
        # Initialize the conductor with an initial value
        if self.wire:
            self.wire.status = self._status

    def turn_on(self):
        """
        Turn on a Signal(True)
        """
        self._status = True
        if self.wire:
            self.wire.status = self._status

    def turn_off(self):
        """
        Turns off a Signal(False)
        """
        self._status = False
        if self.wire:
            self.wire.status = self._status

    def flip(self):

        """
        Flip to opposite status
        """

        new_val = not self._status
        self._status = new_val
        if self.wire:
            self.wire.status = self._status

    def to_dict(self):

        x, y = self.position

        return {
            "type": "SWITCH",
            "id": self.id,
            "position": [x, y],
            "state": self._status
        }

class ONE(Component):

    """
    Switcher, beginning of the logical chain
    """

    def __init__(self, wire = None):
        super().__init__()
        self._status = True
        self._wire = wire
        self.label = "ONE"
        # Initialize the conductor with an initial value
        if self._wire:
            self._wire.status = self._status

    def to_dict(self):

        x, y = self.position

        return {
            "type": "ONE",
            "id": self.id,
            "position": [x, y]
        }

    @property
    def wire(self):

        """
        Docstring for wire
        """

        return self._wire

    @wire.setter
    def wire(self, w):
        self._wire = w
        if self._wire:
            self._wire.status = self._status

class ZERO(Component):

    """
    Switcher, beginning of the logical chain
    """

    def __init__(self, wire = None):
        super().__init__()
        self._status = False
        self._wire = wire
        self.label = "ZERO"
        # Initialize the conductor with an initial value
        if self._wire:
            self._wire.status = self._status

    def to_dict(self):

        x, y = self.position

        return {
            "type": "ZERO",
            "id": self.id,
            "position": [x, y]
        }

    @property
    def wire(self):

        """
        Docstring for wire
        """

        return self._wire

    @wire.setter
    def wire(self, w):
        self._wire = w
        if self._wire:
            self._wire.status = self._status

class Out(Component):

    """
    Ending of the logical gate
    """

    def __init__(self, wire = None):
        super().__init__()
        self.wire = wire
        self._status = False
        self.label = "OUT"
        if self.wire:
            self.wire.destinations.append(self)
            self.update()

    def update(self):

        """
        Called when input wire signal changes
        """

        self._status = self.wire.status
        # Notify all components connected to this output

    @property
    def status(self):

        """
        Docstring for status
        """

        # Always returns the current state of the conductor it is connected to
        return self._status

    def __repr__(self):
        return f"output={self.status}"

class COPY(Component):

    """
    Router for distributing the same signal over some wires amount
    """

    def __init__(self, wire = None, wires: list = None):
        super().__init__()
        self.input_w = [wire]
        self.outputs = wires

        self.label = "COPY"

        wire.destinations.append(self)
        self.update()

    def update(self):
        """
        The method that is called by the conductor when the signal changes
        """
        val = self.evaluate()
        for w in self.outputs:
            w.status = val

    def evaluate(self):
        """
        Evaluate output signal value
        """
        return self.input_w[0].status

class NOT(Gate):

    """
    NOT Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "NOT"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        if not self.input_w:
            return True
        # Ensure we are checking the status of the wire object
        wire_status = bool(self.input_w[0].status)
        return not wire_status

class BUF(Gate):

    """
    BUF Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "BUF"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire = bool(self.input_w[0].status)
        return wire

class AND(Gate):

    """
    AND Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "AND"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = bool(wire_1 and wire_2)
        return result

class NAND(Gate):

    """
    NAND Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "NAND"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = wire_1 and wire_2
        return not result

class OR(Gate):

    """
    OR Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "OR"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = wire_1 or wire_2
        return result

class NOR(Gate):

    """
    NOR Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "NOR"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = wire_1 or wire_2
        return not result

class XOR(Gate):

    """
    XOR Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "XOR"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = (wire_1 or wire_2) and (not wire_1 or not wire_2)
        return result

class XNOR(Gate):

    """
    XNOR Gate
    """

    def __init__(self, w_in, w_out=None):
        super().__init__(w_in, w_out)
        self.label = "XNOR"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = (wire_1 or wire_2) and (not wire_1 or not wire_2)
        return not result
