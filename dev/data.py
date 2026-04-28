"""
Main classes for ALU dev.data
"""

# from dataclasses import dataclass

# @dataclass
# class Signal:

#     """
#     Boolean Signal 0 or 1
#     """

#     value: bool

class Signal:

    """
    Boolean Signal 0 or 1
    """

    def __init__(self, value: bool):

        if not isinstance(value, bool):
            raise TypeError("Incorrect input for boolean value")

        self.value = value

    def __repr__(self):
        return f"Singal(value={self.value})"

    def __eq__(self, other):
        return self.value == other.value

    def __bool__(self):
        return self.value

    # def __and__(self, other):
    #     return self.value and other.value

    # def __or__(self, other):
    #     return self.value or other.value

class Wire:

    """
    Docstring for Wire
    """

    def __init__(self):
        self._status = Signal(False)
        # For propagation
        self.destinations = []
        # self.start = i
        # self.end = o
    @property
    def status(self):
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
class Gate:

    """
    Gate Father Class
    """

    def __init__(self, w_in: list, w_out = None):
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
        self.output_w.status = self.out = self.evaluate()

    def __repr__(self):
        return f"input_wires={self.input_w}, output_wire={self.output_w}, out_value={self.out}"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        return Signal(False)

    def update(self):
        """
        The method that is called by the conductor when the signal changes
        """
        
        new_val = self.evaluate()
        # We update the output conductor - this will start the next wave of propagation
        self.output_w.status = new_val

class Switch:

    """
    Switcher, beginning of the logical chain
    """

    def __init__(self, value = False, wire = None):
        self._status = Signal(value)
        self.wire = wire
        # Initialize the conductor with an initial value
        if self.wire:
            self.wire.status = self._status
    def turn_on(self):
        """
        Turn on a Signal(True)
        """
        self._status = Signal(True)
        if self.wire:
            self.wire.status = self._status

    def turn_off(self):
        """
        Turns off a Signal(False)
        """
        self._status = Signal(False)
        if self.wire:
            self.wire.status = self._status

    def flip(self):
        """
        Flip to opposite status
        """
        new_val = not self._status.value
        self._status = Signal(new_val)
        if self.wire:
            self.wire.status = self._status
class OUT:

    """
    Ending of the logical gate
    """

    def __init__(self, wire = None):
        self.wire = wire
        self.status = self.wire.status
    @property
    def status(self):
        # Always returns the current state of the conductor it is connected to
        return self.wire.status if self.wire else Signal(False)
    def __repr__(self):
        return f"output={self.status}"

class COPY:

    """
    Router for distributing the same signal over some wires amount
    """

    def __init__(self, wire = None, wires: list = None):
        self.input_w = [wire]
        self.outputs = wires

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
    AND Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire = bool(self.input_w[0].status)
        return Signal(not wire)

class AND(Gate):

    """
    AND Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = bool(wire_1 and wire_2)
        return Signal(result)

class NAND(Gate):

    """
    NAND Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = wire_1 and wire_2
        return Signal(not result)

class OR(Gate):

    """
    OR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = wire_1 or wire_2
        return Signal(result)

class NOR(Gate):

    """
    NOR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = wire_1 or wire_2
        return Signal(not result)

class XOR(Gate):

    """
    XOR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = (wire_1 or wire_2) and (not wire_1 or not wire_2)
        return Signal(result)

class XNOR(Gate):

    """
    XNOR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1 = bool(self.input_w[0].status)
        wire_2 = bool(self.input_w[1].status)
        result = (wire_1 or wire_2) and (not wire_1 or not wire_2)
        return Signal(not result)

w1, w2, w3 = Wire(), Wire(), Wire()
w1.status, w2.status = Signal(True), Signal(True)

op = XOR([w1, w2], w3)
print(w3.status)
