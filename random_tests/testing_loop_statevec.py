from random_statevector_test import random_statevector_test

max_num_qubits = 24
max_num_gates = 220
for num_qubits in range(3, max_num_qubits, 4):
    for num_gates in range(10, max_num_gates, 20):
        random_statevector_test(num_qubits, num_gates)
