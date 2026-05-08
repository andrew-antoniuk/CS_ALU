import unittest
from data import Signal, Wire, Switch, OUT, COPY, NOT, AND, NAND, OR, NOR, XOR, XNOR

class TestSignal(unittest.TestCase):
    """Tests for Signal class"""

    def test_signal_initialization_true(self):
        """Test Signal initialization with True value"""
        signal = Signal(True)
        self.assertTrue(signal.value)

    def test_signal_initialization_false(self):
        """Test Signal initialization with False value"""
        signal = Signal(False)
        self.assertFalse(signal.value)

    def test_signal_invalid_input_raises_typeerror(self):
        """Test Signal raises TypeError for non-boolean input"""
        with self.assertRaises(TypeError):
            Signal(1)
        with self.assertRaises(TypeError):
            Signal("True")
        with self.assertRaises(TypeError):
            Signal(None)

    def test_signal_repr(self):
        """Test Signal string representation"""
        signal_true = Signal(True)
        signal_false = Signal(False)
        self.assertEqual(repr(signal_true), "Signal(value=True)")
        self.assertEqual(repr(signal_false), "Signal(value=False)")

    def test_signal_equality(self):
        """Test Signal equality comparison"""
        signal1 = Signal(True)
        signal2 = Signal(True)
        signal3 = Signal(False)
        self.assertEqual(signal1, signal2)
        self.assertNotEqual(signal1, signal3)

    def test_signal_bool_conversion(self):
        """Test Signal bool conversion"""
        signal_true = Signal(True)
        signal_false = Signal(False)
        self.assertTrue(bool(signal_true))
        self.assertFalse(bool(signal_false))


class TestWire(unittest.TestCase):
    """Tests for Wire class"""

    def test_wire_initialization(self):
        """Test Wire initialization with default False status"""
        wire = Wire()
        self.assertEqual(wire.status, Signal(False))
        self.assertEqual(wire.destinations, [])

    def test_wire_status_setter(self):
        """Test Wire status setter"""
        wire = Wire()
        new_signal = Signal(True)
        wire.status = new_signal
        self.assertEqual(wire.status, new_signal)

    def test_wire_status_no_change_no_propagation(self):
        """Test Wire doesn't propagate if signal hasn't changed"""
        wire = Wire()
        update_count = [0]

        class MockGate:
            def update(self):
                update_count[0] += 1

        gate = MockGate()
        wire.destinations.append(gate)

        # Set same signal twice
        wire.status = Signal(False)
        wire.status = Signal(False)

        # Should only call update once (in initialization)
        self.assertEqual(update_count[0], 0)

    def test_wire_status_change_propagates(self):
        """Test Wire propagates signal changes to destinations"""
        wire = Wire()
        update_count = [0]

        class MockGate:
            def update(self):
                update_count[0] += 1

        gate = MockGate()
        wire.destinations.append(gate)

        wire.status = Signal(True)
        self.assertEqual(update_count[0], 1)

        wire.status = Signal(False)
        self.assertEqual(update_count[0], 2)

if __name__ == "__main__":
    unittest.main()
