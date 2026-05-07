"""
Docstring for dev.alu
Don't know what it exactly is
"""

from data import Wire, AND, OR, NOT, COPY, Switch

def xor_gate(wa, wb, w_out):
    """
    XOR gate built from AND/OR/NOT primitives.
    XOR(a, b) = (a OR b) AND (NOT (a AND b))
    """
    w_or  = Wire()
    w_and = Wire()
    w_not = Wire()
    OR ([wa, wb],      w_or)
    AND([wa, wb],      w_and)
    NOT([w_and],       w_not)
    AND([w_or, w_not], w_out)

class Mux4to1:
    """
    4-to-1 Multiplexer.
    Selects one of the four input wires (w0-w3) based on selection wires (s1, s0).
    """
    def __init__(self, w0, w1, w2, w3, s1, s0, w_out):
        ns1, ns0 = Wire(), Wire()
        NOT([s1], ns1)
        NOT([s0], ns0)

        c_ns1, c_ns1_2 = Wire(), Wire()
        c_ns0, c_ns0_2 = Wire(), Wire()
        c_s1, c_s1_2 = Wire(), Wire()
        c_s0, c_s0_2 = Wire(), Wire()

        COPY(ns1, [c_ns1, c_ns1_2])
        COPY(ns0, [c_ns0, c_ns0_2])
        COPY(s1, [c_s1, c_s1_2])
        COPY(s0, [c_s0, c_s0_2])

        and0, and1, and2, and3 = Wire(), Wire(), Wire(), Wire()

        AND([w0, c_ns1, c_ns0], and0)
        AND([w1, c_ns1_2, c_s0], and1)
        AND([w2, c_s1, c_ns0_2], and2)
        AND([w3, c_s1_2, c_s0_2], and3)

        or1, or2 = Wire(), Wire()
        OR([and0, and1], or1)
        OR([and2, and3], or2)
        OR([or1, or2], w_out)

class FullAdder:
    """
    Task 1: 1-bit Full Adder
    Sum  = A XOR B XOR Cin
    Cout = (A AND B) OR (B AND Cin) OR (A AND Cin)
    """
    def __init__(self, wire_a, wire_b, wire_cin, wire_sum, wire_cout):
        a1, a2, a3 = Wire(), Wire(), Wire()
        b1, b2, b3 = Wire(), Wire(), Wire()
        c1, c2, c3 = Wire(), Wire(), Wire()

        COPY(wire_a,   [a1, a2, a3])
        COPY(wire_b,   [b1, b2, b3])
        COPY(wire_cin, [c1, c2, c3])

        w_xor1 = Wire()
        xor_gate(a1, b1, w_xor1)
        xor_gate(w_xor1, c1, wire_sum)

        w_and1, w_and2, w_and3 = Wire(), Wire(), Wire()
        AND([a2, b2], w_and1)
        AND([b3, c2], w_and2)
        AND([a3, c3], w_and3)

        w_or1 = Wire()
        OR([w_and1, w_and2], w_or1)
        OR([w_or1,  w_and3], wire_cout)

class Adder4bit:
    """
    Task 2: 4-bit Ripple Carry Adder
    """
    def __init__(self, wires_a, wires_b, wire_cin, wires_sum, wire_cout):
        carries = [wire_cin] + [Wire() for _ in range(3)] + [wire_cout]
        self.adders = []
        for i in range(4):
            fa = FullAdder(
                wires_a[i], wires_b[i], carries[i],
                wires_sum[i], carries[i + 1]
            )
            self.adders.append(fa)

class ALU4bit:
    """
    Task 3: ALU with operation selection
    op1=False, op0=False -> ADD (A + B)
    op1=False, op0=True  -> SUB (A - B)
    op1=True,  op0=False -> AND (A & B)
    op1=True,  op0=True  -> NOT (~A)
    """
    def __init__(self, wires_a, wires_b, wire_op0, wire_op1, wires_out, wire_cout):
        not_b = [Wire() for _ in range(4)]
        for i in range(4):
            b_c = Wire()
            COPY(wires_b[i], [b_c])
            NOT([b_c], not_b[i])

        add_sum, add_cout = [Wire() for _ in range(4)], Wire()
        w_cin_add = Wire()
        Switch(False, w_cin_add)
        Adder4bit(wires_a, wires_b, w_cin_add, add_sum, add_cout)

        sub_sum, sub_cout = [Wire() for _ in range(4)], Wire()
        w_cin_sub = Wire()
        Switch(True, w_cin_sub)
        Adder4bit(wires_a, not_b, w_cin_sub, sub_sum, sub_cout)

        and_res = [Wire() for _ in range(4)]
        for i in range(4):
            a_c, b_c = Wire(), Wire()
            COPY(wires_a[i], [a_c])
            COPY(wires_b[i], [b_c])
            AND([a_c, b_c], and_res[i])

        not_a = [Wire() for _ in range(4)]
        for i in range(4):
            a_c = Wire()
            COPY(wires_a[i], [a_c])
            NOT([a_c], not_a[i])

        for i in range(4):
            s1, s0 = Wire(), Wire()
            COPY(wire_op1, [s1])
            COPY(wire_op0, [s0])
            Mux4to1(add_sum[i], sub_sum[i], and_res[i], not_a[i], s1, s0, wires_out[i])

        op0_c1, op0_c2 = Wire(), Wire()
        COPY(wire_op0, [op0_c1, op0_c2])
        not_op0 = Wire()
        NOT([op0_c1], not_op0)
        m_add, m_sub = Wire(), Wire()
        AND([not_op0, add_cout], m_add)
        AND([op0_c2, sub_cout], m_sub)
        OR([m_add, m_sub], wire_cout)

def _make_wires(n=4):
    return [Wire() for _ in range(n)]

def _set_value(wires, value, bits=4):
    return [Switch(bool((value >> i) & 1), wires[i]) for i in range(bits)]

def _read_value(wires, bits=4):
    return sum(int(bool(wires[i].status)) << i for i in range(bits))

def demo_add(a: int, b: int):
    """Demo preset: addition (ADD)"""
    wa, wb, ws = _make_wires(), _make_wires(), _make_wires()
    w_cin, w_cout = Wire(), Wire()
    _set_value(wa, a); _set_value(wb, b)
    Switch(False, w_cin)
    Adder4bit(wa, wb, w_cin, ws, w_cout)
    result = _read_value(ws)
    carry = int(bool(w_cout.status))
    print(f"ADD: {a} + {b} = {result} (carry={carry})")
    return result

def demo_sub(a: int, b: int):
    """Demo preset: subtraction (SUB) via ALU"""
    wa, wb, wout = _make_wires(), _make_wires(), _make_wires()
    w_op0, w_op1, w_cout = Wire(), Wire(), Wire()
    _set_value(wa, a); _set_value(wb, b)
    Switch(True, w_op0)
    Switch(False, w_op1)
    ALU4bit(wa, wb, w_op0, w_op1, wout, w_cout)
    result = _read_value(wout)
    print(f"SUB: {a} - {b} = {result} (4-bit)")
    return result

def demo_and(a: int, b: int):
    """Demo preset: bitwise AND"""
    wa, wb, wout = _make_wires(), _make_wires(), _make_wires()
    w_op0, w_op1, w_cout = Wire(), Wire(), Wire()
    _set_value(wa, a); _set_value(wb, b)
    Switch(False, w_op0)
    Switch(True, w_op1)
    ALU4bit(wa, wb, w_op0, w_op1, wout, w_cout)
    result = _read_value(wout)
    print(f"AND: {a} & {b} = {result}")
    return result

def demo_not(a: int):
    """Demo preset: bitwise NOT"""
    wa, wb, wout = _make_wires(), _make_wires(), _make_wires()
    w_op0, w_op1, w_cout = Wire(), Wire(), Wire()
    _set_value(wa, a); _set_value(wb, 0)
    Switch(True, w_op0)
    Switch(True, w_op1)
    ALU4bit(wa, wb, w_op0, w_op1, wout, w_cout)
    result = _read_value(wout)
    print(f"NOT: ~{a} = {result} (4-bit)")
    return result

def demo_counter():
    """Demo preset: counter 0..7 (increments by 1 each step)"""
    print("COUNTER (0 to 7):")
    val = 0
    for _ in range(8):
        wa, wb, ws = _make_wires(), _make_wires(), _make_wires()
        w_cin, w_cout = Wire(), Wire()
        _set_value(wa, val)
        _set_value(wb, 1)
        Switch(False, w_cin)
        Adder4bit(wa, wb, w_cin, ws, w_cout)
        print(f"  {val} + 1 = ", end="")
        val = _read_value(ws)
        print(val)
        if val == 0:
            break
