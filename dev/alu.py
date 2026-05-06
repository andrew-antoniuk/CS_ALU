"""
ALU implementation using basic gates from data.py
"""

from dev.data import Wire, Signal, AND, OR, NOT, COPY, Switch, OUT


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
    op1=False, op0=False → ADD (A + B)
    op1=False, op0=True  → SUB (A - B)
    op1=True,  op0=False → AND (A & B)
    op1=True,  op0=True  → NOT (~A)
    """

    def __init__(self, wires_a, wires_b, wire_op0, wire_op1, wires_out, wire_cout):

        not_b = [Wire() for _ in range(4)]
        for i in range(4):
            b_copy = Wire()
            COPY(wires_b[i], [b_copy])
            NOT([b_copy], not_b[i])

        add_sum  = [Wire() for _ in range(4)]
        add_cout = Wire()
        w_cin_add = Wire()
        Switch(False, w_cin_add)
        Adder4bit(wires_a, wires_b, w_cin_add, add_sum, add_cout)

        sub_sum  = [Wire() for _ in range(4)]
        sub_cout = Wire()
        w_cin_sub = Wire()
        Switch(True, w_cin_sub)
        Adder4bit(wires_a, not_b, w_cin_sub, sub_sum, sub_cout)

        and_res = [Wire() for _ in range(4)]
        for i in range(4):
            a_c = Wire(); b_c = Wire()
            COPY(wires_a[i], [a_c])
            COPY(wires_b[i], [b_c])
            AND([a_c, b_c], and_res[i])

        not_a = [Wire() for _ in range(4)]
        for i in range(4):
            a_c = Wire()
            COPY(wires_a[i], [a_c])
            NOT([a_c], not_a[i])

        for i in range(4):
            op0_copies = [Wire() for _ in range(5)]
            op1_copies = [Wire() for _ in range(4)]
            COPY(wire_op0, op0_copies)
            COPY(wire_op1, op1_copies)

            not_op0 = Wire()
            not_op1 = Wire()
            NOT([op0_copies[0]], not_op0)
            NOT([op1_copies[0]], not_op1)

            not_op0_c1, not_op0_c2 = Wire(), Wire()
            not_op1_c1, not_op1_c2 = Wire(), Wire()
            COPY(not_op0, [not_op0_c1, not_op0_c2])
            COPY(not_op1, [not_op1_c1, not_op1_c2])

            sel_add = Wire()
            sel_sub = Wire()
            sel_and = Wire()
            sel_not = Wire()
            AND([not_op1_c1, not_op0_c1], sel_add)
            AND([not_op1_c2, op0_copies[1]], sel_sub)
            AND([op1_copies[1], not_op0_c2], sel_and)
            AND([op1_copies[2], op0_copies[2]], sel_not)

            m_add = Wire(); m_sub = Wire()
            m_and = Wire(); m_not = Wire()
            AND([sel_add, add_sum[i]], m_add)
            AND([sel_sub, sub_sum[i]], m_sub)
            AND([sel_and, and_res[i]], m_and)
            AND([sel_not, not_a[i]],   m_not)

            w_or1 = Wire()
            w_or2 = Wire()
            OR([m_add, m_sub], w_or1)
            OR([m_and, m_not], w_or2)
            OR([w_or1, w_or2], wires_out[i])

        op0_co1, op0_co2 = Wire(), Wire()
        COPY(wire_op0, [op0_co1, op0_co2])
        not_op0_co = Wire()
        NOT([op0_co1], not_op0_co)
        m_add_co = Wire(); m_sub_co = Wire()
        AND([not_op0_co, add_cout], m_add_co)
        AND([op0_co2,    sub_cout], m_sub_co)
        OR([m_add_co, m_sub_co], wire_cout)


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
    carry  = int(bool(w_cout.status))
    print(f"ADD: {a} + {b} = {result} (carry={carry})")
    return result


def demo_sub(a: int, b: int):
    """Demo preset: subtraction (SUB) via ALU"""
    wa, wb, wout = _make_wires(), _make_wires(), _make_wires()
    w_op0, w_op1, w_cout = Wire(), Wire(), Wire()
    _set_value(wa, a); _set_value(wb, b)
    Switch(True,  w_op0)
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
    Switch(True,  w_op1)
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
