from random_statevector_test import random_statevector_test

max_num_qubits = 17
max_num_gates = 70
for num_qubits in range(4, max_num_qubits, 4):
    for num_gates in range(10, max_num_gates, 10):
        random_statevector_test(num_qubits, num_gates, 88888888)
