from qiskit import *
from qiskit.providers.aer import *
from qiskit.circuit import instruction, Gate

import random
import numpy as np

def create_circuit(num_qubits, number_of_gates, seed, qc):
    
    random.seed(seed)
    kind_of_gate = ['one qubit', 'two qubits']
    one_qubit = ['x', 'y', 'z', 'h', 't', 's', 'tdg', 'sdg', 'id', 'u1', 'u2','u3']
    two_qubits = ['cx', 'cz', 'swap']

    for num_gates in range(number_of_gates):
        qubit = random.choice(range(num_qubits))
        phase_params = []

        kind = random.choice(kind_of_gate)
        if(kind == 'one qubit'):
            gate = random.choice(one_qubit)
            gate_size = 1
        else:
            gate = random.choice(two_qubits)
            gate_size = 2

        if gate in ['u1','u2','u3']:
           lambda_ = random.uniform(0, np.pi)
           phase_params.append(lambda_)
        if gate in ['u2','u3']:
           phi_ = random.uniform(0, np.pi)
           phase_params.append(phi_)
        if gate in ['u3']:
           theta_ = random.uniform(0, np.pi)
           phase_params.append(theta_)

        if gate in ['cx', 'cz', 'swap']:
           choices = list(range(num_qubits))
           choices.remove(qubit)
           second_qubit = random.choice(choices)

        full_gate = Gate(name=gate, num_qubits=gate_size, params=phase_params)
        if gate_size == 1:
            list_qubits = [qc.qubits[qubit]]
        else:
            list_qubits = [qc.qubits[qubit], qc.qubits[second_qubit]]
        qc.append(full_gate, list_qubits)

    return qc

