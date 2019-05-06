# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
NoiseModel class integration tests
"""

import unittest
from test.terra import common
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.compiler import assemble, transpile
from qiskit.providers.aer.backends import QasmSimulator
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors.quantum_error import QuantumError
from qiskit.providers.aer.noise.errors.standard_errors import pauli_error
from qiskit.providers.aer.noise.errors.standard_errors import reset_error
from qiskit.providers.aer.noise.errors.standard_errors import amplitude_damping_error
from qiskit.providers.aer.utils.qobj_utils import measure_instr
from qiskit.providers.aer.utils.qobj_utils import append_instr


class TestNoise(common.QiskitAerTestCase):
    """Testing noise model"""

    def test_readout_error_qubit0(self):
        """Test readout error on qubit 0 for bell state"""

        # Test circuit: ideal bell state
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        # Ensure qubit 0 is measured before qubit 1
        circuit.barrier(qr)
        circuit.measure(qr[0], cr[0])
        circuit.barrier(qr)
        circuit.measure(qr[1], cr[1])
        backend = QasmSimulator()

        # Asymetric readout error on qubit-0 only
        probs_given0 = [0.9, 0.1]
        probs_given1 = [0.3, 0.7]
        noise_model = NoiseModel()
        noise_model.add_readout_error([probs_given0, probs_given1], [0])

        shots = 2000
        target = {
            '0x0': probs_given0[0] * shots / 2,
            '0x1': probs_given0[1] * shots / 2,
            '0x2': probs_given1[0] * shots / 2,
            '0x3': probs_given1[1] * shots / 2
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_readout_error_qubit1(self):
        """Test readout error on qubit 1 for bell state"""

        # Test circuit: ideal bell state
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        # Ensure qubit 0 is measured before qubit 1
        circuit.barrier(qr)
        circuit.measure(qr[0], cr[0])
        circuit.barrier(qr)
        circuit.measure(qr[1], cr[1])
        backend = QasmSimulator()

        # Asymetric readout error on qubit-0 only
        probs_given0 = [0.9, 0.1]
        probs_given1 = [0.3, 0.7]
        noise_model = NoiseModel()
        noise_model.add_readout_error([probs_given0, probs_given1], [1])

        shots = 2000
        target = {
            '0x0': probs_given0[0] * shots / 2,
            '0x1': probs_given1[0] * shots / 2,
            '0x2': probs_given0[1] * shots / 2,
            '0x3': probs_given1[1] * shots / 2
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_readout_error_all_qubit(self):
        """Test 100% readout error on all qubits"""

        # Test circuit: ideal bell state
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.h(qr[0])
        circuit.cx(qr[0], qr[1])
        # Ensure qubit 0 is measured before qubit 1
        circuit.barrier(qr)
        circuit.measure(qr[0], cr[0])
        circuit.barrier(qr)
        circuit.measure(qr[1], cr[1])
        backend = QasmSimulator()

        # Asymetric readout error on qubit-0 only
        probs_given0 = [0.9, 0.1]
        probs_given1 = [0.3, 0.7]
        noise_model = NoiseModel()
        noise_model.add_all_qubit_readout_error([probs_given0, probs_given1])

        # Expected counts
        shots = 2000
        p00 = 0.5 * (probs_given0[0]**2 + probs_given1[0]**2)
        p01 = 0.5 * (probs_given0[0] * probs_given0[1] +
                     probs_given1[0] * probs_given1[1])
        p10 = 0.5 * (probs_given0[0] * probs_given0[1] +
                     probs_given1[0] * probs_given1[1])
        p11 = 0.5 * (probs_given0[1]**2 + probs_given1[1]**2)
        target = target = {
            '0x0': p00 * shots,
            '0x1': p01 * shots,
            '0x2': p10 * shots,
            '0x3': p11 * shots
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_readout_error_correlated_2qubit(self):
        """Test a correlated two-qubit readout error"""
        # Test circuit: prepare all plus state
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.h(qr)
        circuit.barrier(qr)
        # We will manually add a correlated measure operation to
        # the assembled qobj
        backend = QasmSimulator()

        # Correlated 2-qubit readout error
        probs_given00 = [0.3, 0, 0, 0.7]
        probs_given01 = [0, 0.6, 0.4, 0]
        probs_given10 = [0, 0, 1, 0]
        probs_given11 = [0.1, 0, 0, 0.9]
        probs_noise = [
            probs_given00, probs_given01, probs_given10, probs_given11
        ]
        noise_model = NoiseModel()
        noise_model.add_readout_error(probs_noise, [0, 1])

        # Expected counts
        shots = 2000
        probs_ideal = [0.25, 0.25, 0.25, 0.25]
        p00 = sum([
            ideal * noise[0] for ideal, noise in zip(probs_ideal, probs_noise)
        ])
        p01 = sum([
            ideal * noise[1] for ideal, noise in zip(probs_ideal, probs_noise)
        ])
        p10 = sum([
            ideal * noise[2] for ideal, noise in zip(probs_ideal, probs_noise)
        ])
        p11 = sum([
            ideal * noise[3] for ideal, noise in zip(probs_ideal, probs_noise)
        ])
        target = {
            '0x0': p00 * shots,
            '0x1': p01 * shots,
            '0x2': p10 * shots,
            '0x3': p11 * shots
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        # Add measure to qobj
        item = measure_instr([0, 1], [0, 1])
        append_instr(qobj, 0, item)
        # Execute
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_reset_error_specific_qubit_50percent(self):
        """Test 50% perecent reset error on qubit-0"""

        # Test circuit: ideal outcome "11"
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.x(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        noise_circs = [[{
            "name": "reset",
            "qubits": [0]
        }], [{
            "name": "id",
            "qubits": [0]
        }]]

        # 50% reset noise on qubit-0 "u3" only.
        noise_probs = [0.5, 0.5]
        error = QuantumError(zip(noise_circs, noise_probs))
        noise_model = NoiseModel()
        noise_model.add_quantum_error(error, "u3", [0])
        shots = 2000
        target = {'0x2': shots / 2, '0x3': shots / 2}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_reset_error_specific_qubit_25percent(self):
        """Test 25% percent reset error on qubit-1"""

        # Test circuit: ideal outcome "11"
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.x(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        noise_circs = [[{
            "name": "reset",
            "qubits": [0]
        }], [{
            "name": "id",
            "qubits": [0]
        }]]

        # 25% reset noise on qubit-1 "u3" only.
        noise_probs = [0.25, 0.75]
        error = QuantumError(zip(noise_circs, noise_probs))
        noise_model = NoiseModel()
        noise_model.add_quantum_error(error, "u3", [1])
        shots = 2000
        # target = {'01': shots / 4, '11': 3 * shots / 4}
        target = {'0x1': shots / 4, '0x3': 3 * shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_reset_error_all_qubit_100percent(self):
        """Test 100% precent reset error on all qubits"""

        # Test circuit: ideal outcome "11"
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.x(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        noise_circs = [[{
            "name": "reset",
            "qubits": [0]
        }], [{
            "name": "id",
            "qubits": [0]
        }]]

        # 100% reset noise on all qubit "u3".
        noise_probs = [1, 0]
        error = QuantumError(zip(noise_circs, noise_probs))
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, "u3")
        shots = 100
        # target = {'00': shots}
        target = {'0x0': shots}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0)

    def test_all_qubit_pauli_error_gate_100percent(self):
        """Test 100% Pauli error on id gates"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.iden(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 100
        # test noise model
        error = pauli_error([('X', 1)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, 'id')
        # Execute
        target = {'0x3': shots}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0)

    def test_all_qubit_pauli_error_gate_25percent(self):
        """Test 100% Pauli error on id gates"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.iden(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, 'id')
        # Execute
        target = {
            '0x0': 9 * shots / 16,
            '0x1': 3 * shots / 16,
            '0x2': 3 * shots / 16,
            '0x3': shots / 16
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_specific_qubit_pauli_error_gate_100percent(self):
        """Test 100% Pauli error on id gates on qubit-1"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.iden(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 100
        # test noise model
        error = pauli_error([('X', 1)])
        noise_model = NoiseModel()
        noise_model.add_quantum_error(error, 'id', [1])
        # Execute
        target = {'0x2': shots}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0)

    def test_specific_qubit_pauli_error_gate_25percent(self):
        """Test 100% Pauli error on id gates qubit-0"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.iden(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_quantum_error(error, 'id', [0])
        # Execute
        target = {'0x0': 3 * shots / 4, '0x1': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_nonlocal_pauli_error_gate_25percent(self):
        """Test 100% non-local Pauli error on cx(0, 1) gate"""
        qr = QuantumRegister(3, 'qr')
        cr = ClassicalRegister(3, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.cx(qr[0], qr[1])
        circuit.barrier(qr)
        circuit.cx(qr[1], qr[0])
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('XII', 0.25), ('III', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_nonlocal_quantum_error(error, 'cx', [0, 1], [0, 1, 2])
        # Execute
        target = {'0x0': 3 * shots / 4, '0x4': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_all_qubit_pauli_error_measure_25percent(self):
        """Test 25% Pauli-X error on measure"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, 'measure')
        # Execute
        target = {
            '0x0': 9 * shots / 16,
            '0x1': 3 * shots / 16,
            '0x2': 3 * shots / 16,
            '0x3': shots / 16
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_specific_qubit_pauli_error_measure_25percent(self):
        """Test 25% Pauli-X error on measure of qubit-1"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_quantum_error(error, 'measure', [1])
        # Execute
        target = {'0x0': 3 * shots / 4, '0x2': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_nonlocal_pauli_error_measure_25percent(self):
        """Test 25% Pauli-X error on qubit-1 when measuring qubit 0"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        # use barrier to ensure measure qubit 0 is before qubit 1
        circuit.measure(qr[0], cr[0])
        circuit.barrier(qr)
        circuit.measure(qr[1], cr[1])
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_nonlocal_quantum_error(error, 'measure', [0], [1])
        # Execute
        target = {'0x0': 3 * shots / 4, '0x2': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_all_qubit_pauli_error_reset_25percent(self):
        """Test 25% Pauli-X error on reset"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.barrier(qr)
        circuit.reset(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, 'reset')
        # Execute
        target = {
            '0x0': 9 * shots / 16,
            '0x1': 3 * shots / 16,
            '0x2': 3 * shots / 16,
            '0x3': shots / 16
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_specific_qubit_pauli_error_reset_25percent(self):
        """Test 25% Pauli-X error on reset of qubit-1"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.barrier(qr)
        circuit.reset(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_quantum_error(error, 'reset', [1])
        # Execute
        target = {'0x0': 3 * shots / 4, '0x2': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_nonlocal_pauli_error_reset_25percent(self):
        """Test 25% Pauli-X error on qubit-1 when reseting qubit 0"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.barrier(qr)
        circuit.reset(qr[1])
        circuit.barrier(qr)
        circuit.reset(qr[0])
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = pauli_error([('X', 0.25), ('I', 0.75)])
        noise_model = NoiseModel()
        noise_model.add_nonlocal_quantum_error(error, 'reset', [0], [1])
        # Execute
        target = {'0x0': 3 * shots / 4, '0x2': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_amplitude_damping_error(self):
        """Test amplitude damping error damps to correct state"""
        qr = QuantumRegister(1, 'qr')
        cr = ClassicalRegister(1, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.x(qr)  # prepare + state
        for _ in range(30):
            # Add noisy identities
            circuit.barrier(qr)
            circuit.iden(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        shots = 2000
        backend = QasmSimulator()
        # test noise model
        error = amplitude_damping_error(0.75, 0.25)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, 'id')
        # Execute
        target = {'0x0': 3 * shots / 4, '0x1': shots / 4}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_standard_reset0_error_100percent(self):
        """Test 100% Pauli error on id gates"""
        qr = QuantumRegister(1, 'qr')
        cr = ClassicalRegister(1, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.x(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 100
        # test noise model
        error = reset_error(1)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x'])
        # Execute
        target = {'0x0': shots}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0)

    def test_standard_reset1_error_100percent(self):
        """Test 100% Pauli error on id gates"""
        qr = QuantumRegister(1, 'qr')
        cr = ClassicalRegister(1, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.iden(qr)
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 100
        # test noise model
        error = reset_error(0, 1)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x'])
        # Execute
        target = {'0x1': shots}
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0)

    def test_standard_reset0reset1_error_50percent(self):
        """Test 100% Pauli error on id gates"""
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circuit = QuantumCircuit(qr, cr)
        circuit.iden(qr[0])
        circuit.x(qr[1])
        circuit.barrier(qr)
        circuit.measure(qr, cr)
        backend = QasmSimulator()
        shots = 2000
        # test noise model
        error = reset_error(0.25, 0.25)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x'])
        # Execute
        target = {
            '0x0': 3 * shots / 16,
            '0x1': shots / 16,
            '0x2': 9 * shots / 16,
            '0x3': 3 * shots / 16
        }
        circuit = transpile(circuit, basis_gates=noise_model.basis_gates)
        qobj = assemble([circuit], backend, shots=shots)
        result = backend.run(qobj, noise_model=noise_model).result()
        self.is_completed(result)
        self.compare_counts(result, [circuit], [target], delta=0.05 * shots)

    def test_noise_model_basis_gates(self):
        """Test noise model basis_gates"""
        basis_gates = ['u1', 'u2', 'u3', 'cx']
        model = NoiseModel(basis_gates)
        target = sorted(basis_gates)
        self.assertEqual(model.basis_gates, target)

        # Check adding readout errors doesn't add to basis gates
        model = NoiseModel(basis_gates)
        target = sorted(basis_gates)
        model.add_all_qubit_readout_error([[0.9, 0.1], [0, 1]], False)
        self.assertEqual(model.basis_gates, target)
        model.add_readout_error([[0.9, 0.1], [0, 1]], [2], False)
        self.assertEqual(model.basis_gates, target)

        # Check a reset instruction error isn't added to basis gates
        model = NoiseModel(basis_gates)
        target = sorted(basis_gates)
        model.add_all_qubit_quantum_error(reset_error(0.2), ['reset'], False)
        self.assertEqual(model.basis_gates, target)

        # Check a non-standard gate isn't added to basis gates
        model = NoiseModel(basis_gates)
        target = sorted(basis_gates)
        model.add_all_qubit_quantum_error(reset_error(0.2), ['label'], False)
        self.assertEqual(model.basis_gates, target)

        # Check a standard gate is added to basis gates
        model = NoiseModel(basis_gates)
        target = sorted(basis_gates + ['h'])
        model.add_all_qubit_quantum_error(reset_error(0.2), ['h'], False)
        self.assertEqual(model.basis_gates, target)

    def test_noise_model_noise_instructions(self):
        """Test noise instructions"""
        model = NoiseModel()
        target = []
        self.assertEqual(model.noise_instructions, target)

        # Check a non-standard gate is added to noise instructions
        model = NoiseModel()
        model.add_all_qubit_quantum_error(reset_error(0.2), ['label'], False)
        target = ['label']
        self.assertEqual(model.noise_instructions, target)

        # Check a standard gate is added to noise instructions
        model = NoiseModel()
        model.add_all_qubit_quantum_error(reset_error(0.2), ['h'], False)
        target = ['h']
        self.assertEqual(model.noise_instructions, target)

        # Check a reset is added to noise instructions
        model = NoiseModel()
        model.add_all_qubit_quantum_error(reset_error(0.2), ['reset'], False)
        target = ['reset']
        self.assertEqual(model.noise_instructions, target)

        # Check a measure is added to noise instructions for readout error
        model = NoiseModel()
        model.add_all_qubit_readout_error([[0.9, 0.1], [0, 1]], False)
        target = ['measure']
        self.assertEqual(model.noise_instructions, target)

    def test_noise_model_noise_qubits(self):
        """Test noise instructions"""
        model = NoiseModel()
        target = []
        self.assertEqual(model.noise_qubits, target)

        # Check adding a default error isn't added to noise qubits
        model = NoiseModel()
        model.add_all_qubit_quantum_error(pauli_error([['XX', 1]]), ['label'], False)
        target = []
        self.assertEqual(model.noise_qubits, target)

        # Check adding a local error adds to noise qubits
        model = NoiseModel()
        model.add_quantum_error(pauli_error([['XX', 1]]), ['label'], [1, 0], False)
        target = sorted([0, 1])
        self.assertEqual(model.noise_qubits, target)

        # Check adding a non-local error adds to noise qubits
        model = NoiseModel()
        model.add_nonlocal_quantum_error(pauli_error([['XX', 1]]), ['label'], [0], [1, 2], False)
        target = sorted([0, 1, 2])
        self.assertEqual(model.noise_qubits, target)

        # Check adding a default error isn't added to noise qubits
        model = NoiseModel()
        model.add_all_qubit_readout_error([[0.9, 0.1], [0, 1]], False)
        target = []
        self.assertEqual(model.noise_qubits, target)

        # Check adding a local error adds to noise qubits
        model = NoiseModel()
        model.add_readout_error([[0.9, 0.1], [0, 1]], [2], False)
        target = [2]
        self.assertEqual(model.noise_qubits, target)

    def test_noise_models_equal(self):
        """Test two noise models are Equal"""
        roerror = [[0.9, 0.1], [0.5, 0.5]]
        error1 = pauli_error([['X', 1]], standard_gates=False)
        error2 = pauli_error([['X', 1]], standard_gates=True)

        model1 = NoiseModel()
        model1.add_all_qubit_quantum_error(error1, ['u3'], False)
        model1.add_quantum_error(error1, ['u3'], [2], False)
        model1.add_nonlocal_quantum_error(error1, ['cx'], [0, 1], [3], False)
        model1.add_all_qubit_readout_error(roerror, False)
        model1.add_readout_error(roerror, [0], False)

        model2 = NoiseModel()
        model2.add_all_qubit_quantum_error(error2, ['u3'], False)
        model2.add_quantum_error(error2, ['u3'], [2], False)
        model2.add_nonlocal_quantum_error(error2, ['cx'], [0, 1], [3], False)
        model2.add_all_qubit_readout_error(roerror, False)
        model2.add_readout_error(roerror, [0], False)
        self.assertEqual(model1, model2)

    def test_noise_models_not_equal(self):
        """Test two noise models are not equal"""
        error = pauli_error([['X', 1]])

        model1 = NoiseModel()
        model1.add_all_qubit_quantum_error(error, ['u3'], False)

        model2 = NoiseModel(basis_gates=['u3', 'cx'])
        model2.add_all_qubit_quantum_error(error, ['u3'], False)


if __name__ == '__main__':
    unittest.main()
