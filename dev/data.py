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
        self.status: Signal = None
        # self.start = i
        # self.end = o

class Gate:

    """
    Gate Father Class
    """

    def __init__(self, w_in: list, w_out = None):

        self.input_w = w_in
        self.output_w = w_out

        self.output_w.status = self.out = self.evaluate()

    def __repr__(self):
        return f"input_wires={self.input_w}, output_wire={self.output_w}, out_value={self.out}"

    def evaluate(self):

        """
        Evaluate output signal value
        """

        return Signal(False)

class NOT(Gate):

    """
    AND Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire = self.input_w[0]
        return Signal(not wire.status)

class AND(Gate):

    """
    AND Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1, wire_2 = self.input_w
        result = wire_1.status and wire_2.status
        return Signal(result)

class OR(Gate):

    """
    OR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1, wire_2 = self.input_w
        result = wire_1.status or wire_2.status
        return Signal(result)

class XOR(Gate):

    """
    XOR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1, wire_2 = self.input_w
        result = (wire_1.status or wire_2.status) and (not wire_1.status or not wire_2.status)
        return Signal(result)

class XNOR(Gate):

    """
    XNOR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1, wire_2 = self.input_w
        result = (wire_1.status or wire_2.status) and (not wire_1.status or not wire_2.status)
        return Signal(not result)


class NOR(Gate):

    """
    NOR Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1, wire_2 = self.input_w
        result = wire_1.status or wire_2.status
        return Signal(not result)

class NAND(Gate):

    """
    NAND Gate
    """

    def evaluate(self):

        """
        Evaluate output signal value
        """

        wire_1, wire_2 = self.input_w
        result = wire_1.status and wire_2.status
        return Signal(not result)

w1, w2, w3 = Wire(), Wire(), Wire()
w1.status, w2.status = Signal(True), Signal(True)

op = XOR([w1, w2], w3)
print(w3.status)
