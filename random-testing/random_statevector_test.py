from qiskit import *
from qiskit.providers.aer import *

# Currently you have to manually import Snapshot instruction
# to use the circuit.snapshot method
from qiskit.extensions.simulator import Snapshot
from qiskit.extensions.simulator.snapshot import snapshot

from pprint import pprint
from create_circuit import create_circuit
import random

def random_statevector_test(num_qubits=4, num_gates=10, seed=100000000):
    backend_qasm = Aer.get_backend('qasm_simulator')

    if seed == 100000000:
        seed = random.choice(range(seed))
    print("running test: num_qubits=" + str(num_qubits) + ", num_gates=" + str(num_gates) + ", seed = " + str(seed))
    q = QuantumRegister(num_qubits)
    c = ClassicalRegister(num_qubits)
    qc = QuantumCircuit(q, c, name="tn_circuit")

    qc = create_circuit(num_qubits, num_gates, seed, qc)

#    sv_snapshot = Snapshot('my_sv', snapshot_type='statevector')
#    qc.append(sv_snapshot)
    qc.snapshot('my_sv', snapshot_type='statevector')

    BACKEND_OPTS_ES = {"method": "statevector"}

    job_sim_ES = execute([qc], QasmSimulator(), backend_options=BACKEND_OPTS_ES, shots=1)
    result_ES = job_sim_ES.result()
    res_ES = result_ES.results

    #print(">>> statevector statevector")
    statevector_ES = res_ES[0].data.snapshots.statevector
    #pprint(statevector_ES)

#--------------

    BACKEND_OPTS_TN = {"method": "tensor_network"}

    job_sim_TN = execute([qc], QasmSimulator(), backend_options=BACKEND_OPTS_TN, shots=1)
    result_TN = job_sim_TN.result()
    res_TN = result_TN.results

    #print(">>> statevector TN")
    statevector_TN = res_TN[0].data.snapshots.statevector
    #pprint(statevector_TN)

# compare results of the two statevectors
    length = pow(2, num_qubits)
    tn = statevector_TN['my_sv'][0]
    ex = statevector_ES['my_sv'][0]
    threshold = 1e-8
    errors = 0
    for i in range(length):
        diff0 = abs(tn[i][0] - ex[i][0])
        diff1 = abs(tn[i][1] - ex[i][1])
        if diff0 > threshold or diff1 > threshold:
            print("diff in index " + str(i) + " " + str(diff0) + " " + str(diff1))
            errors += 1

    if errors == 0:
        print("test passed")
    else:
        print("FAILURE: " + str(errors) + " mismatches found")
    print("-----------")


